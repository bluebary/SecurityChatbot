"""
SecurityChatbot Main Application

Streamlit 기반 보안 챗봇의 메인 애플리케이션 진입점입니다.
"""

import streamlit as st
import tempfile
import os
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

def _display_uploaded_documents() -> None:
    """Displays a table of uploaded documents and a clear button.

    업로드된 문서 목록을 테이블로 표시하고 삭제 버튼을 제공합니다.
    """
    uploaded_files_metadata = session.get_uploaded_files_metadata()
    if uploaded_files_metadata:
        st.subheader("📄 업로드된 문서")
        df = pd.DataFrame(uploaded_files_metadata)
        df['size'] = df['size'].apply(_format_bytes)
        df['upload_date'] = pd.to_datetime(df['upload_date']).dt.strftime('%Y-%m-%d %H:%M')
        df.columns = ['파일명', '크기', '업로드 날짜']
        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("🗑️ 모든 문서 삭제", key="clear_all_docs"):
            session.clear_uploaded_files_metadata()
            session.clear_file_store_info()
            session.set_rag_engine_active_status(False)
            st.success("모든 업로드된 문서와 스토어 정보가 삭제되었습니다.")
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
                    uploaded_doc = doc_manager.upload_file(temp_file_path, display_name=uploaded_file.name)

                    if uploaded_doc:
                        session.add_uploaded_file_metadata(
                            file_name=uploaded_file.name,
                            file_size=uploaded_file.size,
                            upload_datetime=datetime.now()
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
