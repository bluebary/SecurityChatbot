"""
SecurityChatbot Main Application

Streamlit 기반 보안 챗봇의 메인 애플리케이션 진입점입니다.
"""

import streamlit as st
import tempfile
import os
import json
from datetime import datetime
import pandas as pd
from google.api_core.exceptions import GoogleAPIError

from security_chatbot import config
from security_chatbot.chat import session
from security_chatbot.chat import ui_components
from security_chatbot.rag.store_manager import FileSearchStoreManager
from security_chatbot.rag.document_manager import DocumentManager

# --- Custom CSS ---
CUSTOM_CSS = """
<style>
    /* General body styling */
    html, body {
        font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        color: #333333; /* Dark grey text */
    }

    /* Streamlit main content area */
    .stApp {
        background-color: #f0f2f6; /* Light grey background */
    }

    /* Sidebar styling */
    .st-emotion-cache-1ldfecr { /* Target sidebar by class, might change in future Streamlit versions */
        background-color: #e0e6ed; /* Slightly darker grey for sidebar */
        padding: 1rem;
        border-right: 1px solid #c0c8d1;
    }

    /* Header/Title styling */
    h1 {
        color: #2c3e50; /* Darker blue-grey for main title */
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    h2, h3 {
        color: #34495e; /* Slightly lighter blue-grey for subheaders */
    }

    /* Custom banner style */
    .banner-container {
        background-color: #4a90e2; /* A shade of blue */
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .banner-container h1 {
        color: white;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    .banner-container p {
        color: #e0e0e0;
        font-size: 1.1em;
    }

    /* Chat message styling */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: #d1e7ff; /* Light blue for user messages */
        border-top-right-radius: 2px;
    }
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background-color: #f8f9fa; /* Off-white for assistant messages */
        border-top-left-radius: 2px;
    }
    .chat-timestamp {
        font-size: 0.75em;
        color: #888888;
        text-align: right;
        margin-top: 5px;
    }
    .chat-citation {
        font-size: 0.8em;
        color: #555555;
        border-left: 3px solid #4a90e2;
        padding-left: 10px;
        margin-top: 10px;
        background-color: #e6f2ff;
        border-radius: 0 5px 5px 0;
    }
    .chat-citation p {
        margin: 0;
    }

    /* RAG status indicator */
    .rag-status-active {
        background-color: #d4edda; /* Light green */
        color: #155724; /* Dark green */
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .rag-status-inactive {
        background-color: #f8d7da; /* Light red */
        color: #721c24; /* Dark red */
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Streamlit button styling */
    .stButton>button {
        background-color: #4a90e2; /* Blue button */
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #357ABD; /* Darker blue on hover */
        color: white;
    }
    .stButton>button:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    /* Streamlit info/success/warning messages */
    .stAlert {
        border-radius: 8px;
    }
    .stAlert.info {
        background-color: #e6f2ff; /* Lighter blue for info */
        border-left: 5px solid #4a90e2;
    }
    .stAlert.success {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .stAlert.warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .stAlert.error {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #4a90e2; /* Blue progress bar */
    }
</style>
"""

# --- Constants ---
SUPPORTED_FILE_TYPES: list[str] = ["pdf", "txt", "md", "hwp", "hwpx"]
MAX_TOKENS_PER_CHUNK: int = 200
OVERLAP_TOKENS: int = 20

# --- Helper Functions ---

def _format_bytes(size: int) -> str:
    """Formats a size in bytes to a human-readable string.

    바이트 단위의 크기를 사람이 읽기 쉬운 문자열로 변환합니다.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def _export_chat_as_json() -> str:
    """
    현재 채팅 기록을 JSON 형식 문자열로 내보냅니다.

    Returns:
        str: JSON 형식의 채팅 기록
    """
    messages = session.get_chat_messages()
    return json.dumps(messages, ensure_ascii=False, indent=2)

def _export_chat_as_txt() -> str:
    """
    현재 채팅 기록을 사람이 읽기 쉬운 텍스트 형식 문자열로 내보냅니다.

    Returns:
        str: 텍스트 형식의 채팅 기록
    """
    messages = session.get_chat_messages()
    export_lines = []

    # 헤더 추가
    export_lines.append("=== Security Chatbot 대화 기록 ===")
    export_lines.append(f"내보낸 날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for msg in messages:
        # ISO 형식 문자열을 datetime 객체로 변환하여 포맷팅
        timestamp_dt = datetime.fromisoformat(msg['timestamp'])
        formatted_timestamp = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')

        # 역할 표시 (한글로 변환)
        role_display = "사용자" if msg['role'] == "user" else "어시스턴트"
        export_lines.append(f"[{formatted_timestamp}] {role_display}:")
        export_lines.append(f"{msg['content']}\n")

        # 인용이 있는 경우 추가
        if 'citations' in msg and msg['citations']:
            export_lines.append("  [참고 자료]:")
            for citation in msg['citations']:
                export_lines.append(f"    - {citation}")
            export_lines.append("")  # 인용 후 한 줄 띄기

    return "\n".join(export_lines)

def _handle_individual_document_deletion(file_name: str, corpus_file_resource_name: str) -> None:
    """
    개별 문서를 삭제하는 로직을 처리합니다.

    Args:
        file_name: 삭제할 파일의 이름
        corpus_file_resource_name: 삭제할 코퍼스 파일의 리소스 이름
    """
    store_display_name, store_resource_name = session.get_file_store_info()
    if not store_resource_name:
        st.error("❌ File Search Store ID를 찾을 수 없습니다. 문서를 삭제할 수 없습니다.")
        return

    store_manager = FileSearchStoreManager()
    try:
        delete_success = store_manager.delete_corpus_file(corpus_file_resource_name=corpus_file_resource_name)

        if delete_success:
            session.remove_uploaded_file_metadata(file_name)
            st.success(f"✅ 문서 '{file_name}'이(가) 성공적으로 삭제되었습니다.")

            # 모든 문서가 삭제되면 RAG 엔진 비활성화
            if not session.get_uploaded_files_metadata():
                session.set_rag_engine_active_status(False)
                st.info("모든 문서가 삭제되어 RAG 엔진이 비활성화되었습니다.")
        else:
            st.error(f"❌ 문서 '{file_name}' 삭제에 실패했습니다. 로그를 확인해주세요.")

    except Exception as e:
        st.error(f"❌ 문서 '{file_name}' 삭제 중 예상치 못한 오류 발생: {e}")
    finally:
        # 확인 상태 초기화
        if 'confirm_delete_file_name' in st.session_state:
            del st.session_state['confirm_delete_file_name']
        if 'confirm_delete_corpus_resource_name' in st.session_state:
            del st.session_state['confirm_delete_corpus_resource_name']
        st.rerun()

def _handle_delete_all_documents() -> None:
    """
    모든 문서를 삭제하고 스토어 정보를 초기화합니다.
    """
    store_display_name, store_resource_name = session.get_file_store_info()
    if store_resource_name:
        store_manager = FileSearchStoreManager()
        try:
            if store_manager.delete_store(store_resource_name):
                st.success(f"✅ File Search Store '{store_display_name}'가 성공적으로 삭제되었습니다.")
            else:
                st.warning(f"⚠️ File Search Store '{store_display_name}' 삭제에 실패했거나 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"❌ File Search Store 삭제 중 오류 발생: {e}")

    session.clear_uploaded_files_metadata()
    session.clear_file_store_info()
    session.set_rag_engine_active_status(False)
    st.success("모든 업로드된 문서와 스토어 정보가 삭제되었습니다.")

    # 확인 상태 초기화
    if 'confirm_delete_all_docs' in st.session_state:
        del st.session_state['confirm_delete_all_docs']
    st.rerun()

def _display_uploaded_documents() -> None:
    """
    업로드된 문서 목록을 표시하고 개별/전체 삭제 버튼을 제공합니다.
    검색 기능을 통해 파일명으로 필터링할 수 있습니다.
    """
    uploaded_files_metadata = session.get_uploaded_files_metadata()

    if not uploaded_files_metadata:
        st.info("업로드된 문서가 없습니다.")
        return

    st.subheader("📄 업로드된 문서")

    # 검색 기능 추가
    search_query = st.text_input(
        "파일명으로 검색",
        "",
        help="업로드된 문서 목록을 파일명으로 필터링합니다.",
        key="document_search_input"
    )

    # 검색어에 따라 문서 필터링 (대소문자 구분 없음)
    if search_query:
        filtered_files_metadata = [
            file_meta for file_meta in uploaded_files_metadata
            if search_query.lower() in file_meta['name'].lower()
        ]
    else:
        filtered_files_metadata = uploaded_files_metadata

    # 개별 파일 삭제 확인 UI (맨 위에 표시)
    if 'confirm_delete_file_name' in st.session_state and st.session_state.get('confirm_delete_file_name'):
        file_to_delete = st.session_state['confirm_delete_file_name']
        corpus_resource_to_delete = st.session_state['confirm_delete_corpus_resource_name']

        st.warning(f"⚠️ 정말로 문서 '{file_to_delete}'을(를) 삭제하시겠습니까?")
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            if st.button("예", key=f"confirm_yes_delete_{file_to_delete}"):
                _handle_individual_document_deletion(file_to_delete, corpus_resource_to_delete)
        with col2:
            if st.button("아니오", key=f"confirm_no_delete_{file_to_delete}"):
                del st.session_state['confirm_delete_file_name']
                del st.session_state['confirm_delete_corpus_resource_name']
                st.rerun()

    # 검색 결과 표시
    if not filtered_files_metadata:
        st.info("검색 결과가 없습니다.")
    else:
        # 문서 목록 테이블 (개별 삭제 버튼 포함)
        col_header1, col_header2, col_header3, col_header4 = st.columns([0.45, 0.15, 0.25, 0.15])
        with col_header1:
            st.markdown("**파일명**")
        with col_header2:
            st.markdown("**크기**")
        with col_header3:
            st.markdown("**업로드 날짜**")
        with col_header4:
            st.markdown("**삭제**")

        for i, file_meta in enumerate(filtered_files_metadata):
            file_name = file_meta['name']
            file_size_formatted = _format_bytes(file_meta['size'])
            upload_date_formatted = pd.to_datetime(file_meta['upload_date']).strftime('%Y-%m-%d %H:%M')
            corpus_file_resource_name = file_meta['corpus_file_resource_name']

            col1, col2, col3, col4 = st.columns([0.45, 0.15, 0.25, 0.15])
            with col1:
                st.write(file_name)
            with col2:
                st.write(file_size_formatted)
            with col3:
                st.write(upload_date_formatted)
            with col4:
                if st.button("🗑️", key=f"delete_doc_{i}_{file_name}", help=f"'{file_name}' 문서 삭제"):
                    st.session_state['confirm_delete_file_name'] = file_name
                    st.session_state['confirm_delete_corpus_resource_name'] = corpus_file_resource_name
                    st.rerun()

    st.markdown("---")

    # 모든 문서 삭제 버튼 및 확인 UI
    if st.button("🗑️ 모든 문서 삭제", key="clear_all_docs_trigger"):
        st.session_state['confirm_delete_all_docs'] = True
        st.rerun()

    if st.session_state.get('confirm_delete_all_docs', False):
        st.warning("⚠️ 모든 문서를 삭제하고 File Search Store를 초기화하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("예 (모두 삭제)", key="confirm_clear_all_docs_yes"):
                _handle_delete_all_documents()
        with col2:
            if st.button("아니오 (취소)", key="confirm_clear_all_docs_no"):
                del st.session_state['confirm_delete_all_docs']
                st.rerun()

def _handle_document_upload(uploaded_files: list[st.runtime.uploaded_file_manager.UploadedFile]) -> None:
    """
    Handles the document upload process, including store creation and file indexing.

    문서 업로드 프로세스를 처리합니다. 스토어 생성 및 파일 인덱싱을 포함합니다.

    Args:
        uploaded_files: Streamlit file uploader에서 받은 업로드된 파일 목록
    """
    if not uploaded_files:
        st.warning("⚠️ 최소 하나 이상의 파일을 업로드해주세요.")
        return

    session.set_processing_files_status(True)
    try:
        store_display_name, store_resource_name = session.get_file_store_info()

        # 1. Create or get File Search Store
        store_manager = FileSearchStoreManager()
        if store_resource_name is None:
            with st.spinner(f"📦 File Search Store 생성 중: '{store_display_name}'..."):
                try:
                    store = store_manager.create_store(display_name=store_display_name)
                    if store and store.name:
                        session.set_file_store_info(store_display_name, store.name)
                        store_resource_name = store.name
                        st.success(f"✅ File Search Store '{store_display_name}' 생성 완료!")
                    else:
                        st.error(f"❌ File Search Store '{store_display_name}' 생성 실패")
                        return
                except GoogleAPIError as e:
                    st.error(f"❌ Google API 오류 (스토어 생성): {e}")
                    return
                except Exception as e:
                    st.error(f"❌ 스토어 생성 중 예상치 못한 오류 발생: {e}")
                    return
        else:
            st.info(f"📦 기존 File Search Store 사용: '{store_display_name}' (ID: {store_resource_name.split('/')[-1]})")

        # 2. Upload files to the store
        doc_manager = DocumentManager(
            store_name=store_resource_name,
            max_tokens_per_chunk=MAX_TOKENS_PER_CHUNK,
            overlap_tokens=OVERLAP_TOKENS
        )

        total_files = len(uploaded_files)
        progress_text = "📤 파일 업로드 및 처리 중..."
        progress_bar = st.progress(0, text=progress_text)
        files_uploaded_count = 0
        successful_uploads = []
        failed_uploads = []

        with st.spinner("⚙️ 문서 처리 중..."):
            for i, uploaded_file in enumerate(uploaded_files):
                progress_bar.progress((i + 1) / total_files, text=f"{progress_text} ({i+1}/{total_files})")
                try:
                    # Streamlit UploadedFile needs to be saved to a temp file for DocumentManager
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_file_path = tmp_file.name

                    file_validation = doc_manager.validate_file(temp_file_path)
                    if not file_validation['valid']:
                        raise ValueError(f"파일 검증 실패: {uploaded_file.name} - {file_validation.get('error', '알 수 없는 오류')}")

                    st.info(f"📤 '{uploaded_file.name}' 업로드 중...")
                    upload_result = doc_manager.upload_file(temp_file_path, display_name=uploaded_file.name)

                    if upload_result and upload_result.get('corpus_file_name'):
                        session.add_uploaded_file_metadata(
                            file_name=uploaded_file.name,
                            file_size=uploaded_file.size,
                            upload_datetime=datetime.now(),
                            corpus_file_resource_name=upload_result['corpus_file_name']
                        )
                        successful_uploads.append(uploaded_file.name)
                        files_uploaded_count += 1
                    else:
                        failed_uploads.append(uploaded_file.name)
                        st.warning(f"⚠️ '{uploaded_file.name}' 업로드 실패")

                except ValueError as ve:
                    st.error(f"❌ '{uploaded_file.name}' 처리 오류: {ve}")
                    failed_uploads.append(uploaded_file.name)
                except GoogleAPIError as e:
                    st.error(f"❌ Google API 오류 ('{uploaded_file.name}' 업로드): {e}")
                    failed_uploads.append(uploaded_file.name)
                except Exception as e:
                    st.error(f"❌ '{uploaded_file.name}' 처리 중 예상치 못한 오류 발생: {e}")
                    failed_uploads.append(uploaded_file.name)
                finally:
                    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)  # Clean up the temporary file

        progress_bar.empty()  # Clear the progress bar

        if successful_uploads:
            st.success(f"✅ {len(successful_uploads)}/{total_files}개 파일 업로드 완료!")
            session.set_rag_engine_active_status(True)
        if failed_uploads:
            st.error(f"❌ {len(failed_uploads)}개 파일 업로드 실패: {', '.join(failed_uploads)}")

    except Exception as e:
        st.error(f"❌ 업로드 프로세스 중 오류 발생: {e}")
    finally:
        session.set_processing_files_status(False)
        st.rerun()  # Rerun to update the UI with new document list and status

def main() -> None:
    """
    Main function for the Streamlit Security Chatbot application.
    Sets up the page configuration, initializes session state,
    and defines the basic layout for the sidebar and main content area.

    Streamlit Security Chatbot 애플리케이션의 메인 함수입니다.
    페이지 설정, 세션 상태 초기화, 사이드바 및 메인 영역의 기본 레이아웃을 정의합니다.
    """
    # 1. Streamlit 페이지 설정
    st.set_page_config(
        page_title="Security Chatbot",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 세션 상태 초기화
    session.initialize_session_state()

    # 2. 앱 타이틀 및 설명 표시 (배너로 대체)
    st.markdown(
        """
        <div class="banner-container">
            <h1>🔒 Security Chatbot</h1>
            <p>보안 문서(정책, 사고 보고서, 가이드라인 등)를 업로드하고 AI 기반 인사이트와 답변을 받아보세요.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. 기본 레이아웃 구조: 사이드바 및 메인 영역
    with st.sidebar:
        st.header("📂 문서 관리")

        # 1. st.file_uploader를 사용하여 여러 파일 동시 업로드 지원
        uploaded_files = st.file_uploader(
            "보안 문서 업로드",
            type=SUPPORTED_FILE_TYPES,
            accept_multiple_files=True,
            key="file_uploader",
            help="지원 형식: PDF, TXT, Markdown, HWP, HWPX (최대 100MB)"
        )

        # 2. 업로드 버튼 추가
        # 3. 업로드 진행 상황 표시 (disabled 상태 관리)
        if st.button(
            "📤 스토어에 문서 업로드",
            on_click=_handle_document_upload,
            args=(uploaded_files,),
            disabled=session.get_processing_files_status() or not uploaded_files,
            key="upload_button"
        ):
            pass  # The on_click handler will manage the state and rerun

        st.markdown("---")

        # 4. 업로드된 문서 목록 표시
        _display_uploaded_documents()

        st.markdown("---")  # Separator for visual clarity
        st.header("⚙️ 채팅 옵션")
        if st.button("🔄 채팅 초기화", key="clear_chat", help="현재까지의 모든 채팅 기록을 삭제합니다."):
            session.clear_chat_messages()
            st.success("채팅 기록이 초기화되었습니다.")
            st.rerun()

        # 채팅 내보내기 기능
        with st.expander("📥 채팅 내보내기", expanded=False):
            chat_messages = session.get_chat_messages()
            export_disabled = not chat_messages

            if export_disabled:
                st.info("내보낼 채팅 기록이 없습니다.")
            else:
                current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')

                # JSON 내보내기 버튼
                st.download_button(
                    label="📥 JSON으로 내보내기",
                    data=_export_chat_as_json(),
                    file_name=f"chat_export_{current_time_str}.json",
                    mime="application/json",
                    disabled=export_disabled,
                    key="export_json_button",
                    help="전체 채팅 기록을 JSON 파일로 내보냅니다."
                )

                # TXT 내보내기 버튼
                st.download_button(
                    label="📥 TXT로 내보내기",
                    data=_export_chat_as_txt(),
                    file_name=f"chat_export_{current_time_str}.txt",
                    mime="text/plain",
                    disabled=export_disabled,
                    key="export_txt_button",
                    help="전체 채팅 기록을 사람이 읽기 쉬운 텍스트 파일로 내보냅니다."
                )

    # 메인 영역
    st.subheader("💬 채팅 인터페이스")

    # RAG 활성화 상태 안내 메시지 개선
    rag_active = session.get_rag_engine_active_status()
    if rag_active:
        st.markdown("<div class='rag-status-active'>✅ RAG 엔진 활성화: 업로드된 문서를 기반으로 답변합니다.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='rag-status-inactive'>⚠️ RAG 엔진 비활성화: 사이드바에서 문서를 업로드하면 RAG 기반 채팅이 활성화됩니다. 현재는 에코 봇으로 동작합니다.</div>", unsafe_allow_html=True)

    # 채팅 히스토리 렌더링 및 입력 처리 (RAG 활성화 여부와 관계없이 항상 표시)
    ui_components.render_chat_history()
    ui_components.process_chat_input()

if __name__ == "__main__":
    main()
