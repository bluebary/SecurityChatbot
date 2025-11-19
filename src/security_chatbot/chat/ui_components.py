"""SecurityChatbot UI Components

Streamlit 채팅 인터페이스를 위한 재사용 가능한 UI 컴포넌트를 제공합니다.
"""

import time  # For simulating loading
from datetime import datetime
from typing import Any

import streamlit as st

# ChatMessage 타입 정의
ChatMessage = dict[str, Any]


def display_message(message: ChatMessage) -> None:
    """단일 채팅 메시지를 Streamlit의 st.chat_message를 사용하여 표시합니다.
    타임스탬프와 마크다운 포맷팅, 그리고 어시스턴트 메시지에 대한 출처를 지원합니다.

    Args:
        message: 'role', 'content', 'timestamp' (ISO format string) 키를 포함하는 딕셔너리입니다.
                 어시스턴트 메시지의 경우 선택적으로 'citations' (List[str]) 키를 포함할 수 있습니다.

    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  # Markdown support
        if "timestamp" in message:
            # Display timestamp in a smaller, greyed-out font
            st.markdown(
                f"<p class='chat-timestamp'>{message['timestamp']}</p>",
                unsafe_allow_html=True,
            )

        if (
            message["role"] == "assistant"
            and "citations" in message
            and message["citations"]
        ):
            st.markdown("<div class='chat-citation'>", unsafe_allow_html=True)
            st.markdown("**출처:**")
            for i, citation in enumerate(message["citations"]):
                st.markdown(f"- {citation}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_chat_history() -> None:
    """세션 상태에 저장된 모든 채팅 메시지를 렌더링합니다.
    """
    from security_chatbot.chat import session

    messages: list[ChatMessage] = session.get_chat_messages()
    for message in messages:
        display_message(message)


def process_chat_input() -> None:
    """사용자 입력을 처리하고, 유효성 검사 후 세션에 메시지를 추가하며,
    RAG 활성화 여부에 따라 실제 RAG 응답 또는 에코 봇 응답을 생성합니다.
    """
    from security_chatbot.chat import session
    from security_chatbot.rag.query_handler import query_with_rag

    user_input: str | None = st.chat_input(
        "메시지를 입력하세요...", disabled=session.get_processing_files_status()
    )

    if user_input:
        # --- 사용자 입력 검증 시작 ---
        # 1. 빈 문자열 또는 공백만 있는 입력 거부
        if not user_input.strip():
            st.warning("⚠️ 메시지를 입력해주세요.")
            return  # 검증 실패 시 함수 종료

        # 2. 입력 길이 검증 (최대 2000자)
        MAX_INPUT_LENGTH = 2000
        if len(user_input) > MAX_INPUT_LENGTH:
            st.warning(
                f"⚠️ 메시지가 너무 깁니다. 최대 {MAX_INPUT_LENGTH}자까지 입력 가능합니다."
            )
            return  # 검증 실패 시 함수 종료
        # --- 사용자 입력 검증 끝 ---

        current_time = datetime.now()
        session.add_chat_message(
            role="user", content=user_input, timestamp=current_time
        )

        # RAG 활성화 여부에 따른 응답 생성
        if session.get_rag_engine_active_status():
            # 실제 RAG 쿼리 실행
            _, store_resource_name = session.get_file_store_info()

            if not store_resource_name:
                # Store가 없는 경우 에러 메시지
                with st.chat_message("assistant"):
                    error_message = "⚠️ File Search Store가 설정되지 않았습니다. 문서를 먼저 업로드해주세요."
                    st.markdown(error_message)
                    st.markdown(
                        f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>",
                        unsafe_allow_html=True,
                    )
                session.add_chat_message(
                    role="assistant", content=error_message, timestamp=datetime.now()
                )
            else:
                # RAG 쿼리 실행
                with st.chat_message("assistant"):
                    with st.spinner("보안 문서를 분석하고 답변을 생성하는 중..."):
                        rag_response = query_with_rag(
                            query=user_input, store_name=store_resource_name
                        )

                    if rag_response["success"]:
                        # 성공적인 응답
                        assistant_response = rag_response["content"]
                        citations = rag_response["citations"]

                        st.markdown(assistant_response)
                        st.markdown(
                            f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>",
                            unsafe_allow_html=True,
                        )

                        # 출처 정보 표시
                        if citations:
                            st.markdown(
                                "<div class='chat-citation'>", unsafe_allow_html=True
                            )
                            st.markdown("**출처:**")
                            for citation in citations:
                                st.markdown(f"- {citation}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        session.add_chat_message(
                            role="assistant",
                            content=assistant_response,
                            timestamp=datetime.now(),
                            citations=citations,
                        )
                    else:
                        # 오류 발생
                        error_type = rag_response.get('error_type', '')

                        if error_type == 'quota_exceeded':
                            # API 사용량 초과 특별 처리
                            error_message = "⚠️ API 사용량을 초과하였습니다"
                            st.error(error_message)
                            st.warning(
                                "Gemini API의 무료 사용량을 초과했습니다. "
                                "잠시 후 다시 시도해주세요."
                            )
                            retry_delay = rag_response.get('retry_delay', '잠시 후')
                            if retry_delay != '잠시 후':
                                st.info(f"💡 추천 재시도 대기 시간: {retry_delay}")
                        else:
                            # 일반 오류 처리
                            error_message = f"❌ 오류가 발생했습니다: {rag_response.get('error', '알 수 없는 오류')}"
                            st.error(error_message)
                            if 'solution' in rag_response:
                                st.info(f"💡 해결 방법: {rag_response['solution']}")

                        st.markdown(
                            f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>",
                            unsafe_allow_html=True,
                        )
                        session.add_chat_message(
                            role="assistant",
                            content=error_message,
                            timestamp=datetime.now(),
                        )
        else:
            # RAG 비활성화 시 에코 봇
            with st.chat_message("assistant"):
                with st.spinner("생각 중..."):
                    time.sleep(1)  # Simulate echo bot processing time
                assistant_response = f"Echo: {user_input}"
                st.markdown(assistant_response)
                st.markdown(
                    f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>",
                    unsafe_allow_html=True,
                )
            session.add_chat_message(
                role="assistant", content=assistant_response, timestamp=datetime.now()
            )
