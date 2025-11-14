"""SecurityChatbot RAG Query Handler

Gemini File Search API를 사용하여 RAG 기반 쿼리를 처리하고 응답을 생성합니다.
"""

import logging
from typing import Any

from google.api_core.exceptions import GoogleAPIError
from google.genai import types

from security_chatbot.config import API_TIMEOUT_SECONDS, GEMINI_MODEL_NAME
from security_chatbot.utils.api_client import GeminiClientManager
from security_chatbot.utils.error_handler import QueryError, error_handler

logger = logging.getLogger(__name__)

# 보안 특화 시스템 프롬프트
SECURITY_SYSTEM_PROMPT = """
당신은 보안 전문 챗봇입니다. 제공된 보안 문서, 위협 인텔리전스 데이터, 보안 정책 등을 분석하여 사용자 질문에 정확하고 심층적인 답변을 제공해야 합니다. 다음 지침을 따르세요:

1. 보안 관련 질문에만 집중하여 답변하세요.
2. 출처 문서의 내용을 기반으로 답변을 생성하고, 추측하거나 없는 정보를 만들어내지 마세요.
3. 위협 분석, 취약점 평가, 보안 정책 해석, 규정 준수 관련 질문에 특히 강점을 보이세요.
4. 답변은 명확하고 간결하며, 필요한 경우 기술적인 세부 정보를 포함하세요.
5. 가능한 경우, 답변의 근거가 되는 출처를 명확히 제시하세요.
6. 한국어로 답변하세요.
"""


def parse_grounding_metadata(response: types.GenerateContentResponse) -> list[str]:
    """Grounding metadata에서 출처 정보를 추출합니다.

    Args:
        response: Gemini API로부터 받은 응답 객체

    Returns:
        List[str]: 출처 문서 이름 목록

    """
    citations = []
    try:
        # 응답에 candidates가 있는지 확인
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            # grounding_metadata가 있는지 확인
            if (
                hasattr(candidate, "grounding_metadata")
                and candidate.grounding_metadata
            ):
                grounding_metadata = candidate.grounding_metadata

                # grounding_chunks에서 출처 추출
                if hasattr(grounding_metadata, "grounding_chunks"):
                    for chunk in grounding_metadata.grounding_chunks:
                        # 파일 정보 추출
                        if (
                            hasattr(chunk, "retrieved_context")
                            and chunk.retrieved_context
                        ):
                            if (
                                hasattr(chunk.retrieved_context, "title")
                                and chunk.retrieved_context.title
                            ):
                                citations.append(chunk.retrieved_context.title)
                            elif (
                                hasattr(chunk.retrieved_context, "uri")
                                and chunk.retrieved_context.uri
                            ):
                                citations.append(chunk.retrieved_context.uri)
                        # 웹 정보 추출
                        if hasattr(chunk, "web") and chunk.web:
                            if hasattr(chunk.web, "title") and chunk.web.title:
                                citations.append(chunk.web.title)
                            elif hasattr(chunk.web, "uri") and chunk.web.uri:
                                citations.append(chunk.web.uri)

                # retrieval_metadata에서 추출 (File Search의 경우)
                if hasattr(grounding_metadata, "retrieval_metadata"):
                    for metadata in grounding_metadata.retrieval_metadata:
                        if hasattr(metadata, "source") and metadata.source:
                            citations.append(str(metadata.source))

    except Exception as e:
        logger.warning(f"Grounding metadata 파싱 중 오류 발생: {e}")

    # 중복 제거 및 반환
    return list(set(citations)) if citations else []


def format_response(
    response: types.GenerateContentResponse, citations: list[str]
) -> dict[str, Any]:
    """Gemini 응답을 표준화된 딕셔너리 형태로 포맷팅합니다.

    Args:
        response: Gemini API로부터 받은 응답 객체
        citations: 파싱된 출처 목록

    Returns:
        Dict[str, Any]: 포맷팅된 응답 딕셔너리

    """
    content = ""
    error_message = None
    success = False

    try:
        # 응답 텍스트 추출
        if response.text:
            content = response.text
            success = True
        else:
            # 응답 텍스트가 없는 경우
            error_message = "Gemini 모델로부터 응답 텍스트를 받지 못했습니다."

            # 프롬프트 피드백 확인
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                if hasattr(response.prompt_feedback, "block_reason"):
                    error_message += f" (프롬프트 차단 이유: {response.prompt_feedback.block_reason})"

            # 완료 이유 확인
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason"):
                    error_message += f" (응답 완료 이유: {candidate.finish_reason})"

            logger.warning(error_message)

    except Exception as e:
        error_message = f"응답 포맷팅 중 오류 발생: {e}"
        logger.error(error_message)

    return {
        "content": content,
        "citations": citations,
        "success": success,
        "error": error_message,
    }


def query_with_rag(query: str, store_name: str) -> dict[str, Any]:
    """RAG 기반 쿼리 실행 및 응답 반환.
    Gemini File Search API를 사용하여 보안 문서에서 정보를 검색하고 답변을 생성합니다.

    Args:
        query: 사용자 질의
        store_name: Gemini File Search Store의 리소스 이름 (예: "corpora/...")

    Returns:
        Dict[str, Any]: AI 생성 응답, 출처, 성공 여부, 에러 메시지를 포함하는 딕셔너리

    """
    try:
        # Gemini 클라이언트 가져오기
        client = GeminiClientManager.get_client()
        if not client:
            raise ValueError("Gemini API 클라이언트를 초기화할 수 없습니다.")

        # File Search Tool 설정
        file_search_tool = types.Tool(
            file_search=types.FileSearch(file_search_store_names=[store_name])
        )

        # 모델 생성 설정
        generate_content_config = types.GenerateContentConfig(
            system_instruction=SECURITY_SYSTEM_PROMPT,
            temperature=0.2,  # RAG에서는 사실 기반 답변을 위해 낮은 temperature 사용
            tools=[file_search_tool],
        )

        # 쿼리 실행
        logger.info(f"RAG 쿼리 실행 중: '{query[:50]}...' (Store: {store_name})")
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME, contents=query, config=generate_content_config
        )

        # 응답 처리 및 포맷팅
        citations = parse_grounding_metadata(response)
        formatted_response = format_response(response, citations)

        if formatted_response["success"]:
            logger.info(f"RAG 쿼리 성공: {len(citations)}개의 출처 발견")
        else:
            logger.warning(
                f"RAG 쿼리 실패: {formatted_response.get('error', '알 수 없는 오류')}"
            )

        return formatted_response

    except GoogleAPIError as e:
        # Gemini API 관련 오류 처리
        logger.error(f"Gemini API 오류 발생: {e}")
        error_info = error_handler.handle_error(e, "RAG 쿼리 실행")
        return {
            "content": "",
            "citations": [],
            "success": False,
            "error": error_info["message"],
            "solution": error_info["solution"],
        }
    except TimeoutError as e:
        # API 호출 타임아웃 오류 처리, QueryError로 래핑하여 error_handler 사용
        logger.error(f"Gemini API 호출 타임아웃 발생 (초: {API_TIMEOUT_SECONDS}): {e}")
        error_info = error_handler.handle_error(
            QueryError(f"API 호출 타임아웃 발생 (초: {API_TIMEOUT_SECONDS}): {e}"),
            "RAG 쿼리 실행",
        )
        return {
            "content": "",
            "citations": [],
            "success": False,
            "error": error_info["message"],
            "solution": error_info["solution"],
        }
    except ValueError as e:
        # Gemini API 클라이언트 초기화 오류 등 ValueError 처리, QueryError로 래핑하여 error_handler 사용
        logger.error(f"설정 또는 입력 값 오류 발생: {e}")
        error_info = error_handler.handle_error(
            QueryError(f"설정 또는 입력 값 오류: {e}"), "RAG 쿼리 실행"
        )
        return {
            "content": "",
            "citations": [],
            "success": False,
            "error": error_info["message"],
            "solution": error_info["solution"],
        }
    except Exception as e:
        # 그 외 예상치 못한 오류 처리
        logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
        error_info = error_handler.handle_error(e, "RAG 쿼리 실행")
        return {
            "content": "",
            "citations": [],
            "success": False,
            "error": error_info["message"],
            "solution": error_info["solution"],
        }
