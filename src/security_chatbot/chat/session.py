"""
SecurityChatbot Session State Management

Streamlit 세션 상태를 관리하는 모듈입니다.
채팅 히스토리, File Search Store 정보, 업로드된 문서 메타데이터 등을 관리합니다.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional

from security_chatbot import config

# --- Type Definitions for Clarity ---
ChatMessage = Dict[str, Any]
"""Represents a single chat message with 'role', 'content', 'timestamp', and optional 'citations'."""

FileMetadata = Dict[str, Any]
"""
Represents metadata for an uploaded file.
Expected keys: 'name' (str), 'size' (int), 'upload_date' (str, ISO format),
and 'corpus_file_resource_name' (str, Google Gemini API에서 사용하는 코퍼스 파일의 전체 리소스 이름).
"""

# --- Session State Initialization ---

def initialize_session_state() -> None:
    """
    Initializes Streamlit's session state with default values if they don't already exist.
    This function is idempotent and safe to call multiple times without resetting
    existing user data.

    세션 상태를 초기 값으로 설정합니다. 이미 존재하는 값은 덮어쓰지 않으므로
    여러 번 호출해도 안전합니다.
    """
    # 1. Chat Message History
    if "messages" not in st.session_state:
        st.session_state.messages: List[ChatMessage] = []

    # 2. File Search Store Information
    if "store_name" not in st.session_state:
        st.session_state.store_name: str = config.DEFAULT_STORE_DISPLAY_NAME
    if "store_id" not in st.session_state:
        # store_id is typically generated after a store is created, so it starts as None
        st.session_state.store_id: Optional[str] = None

    # 3. Uploaded Document Metadata
    if "uploaded_files_metadata" not in st.session_state:
        st.session_state.uploaded_files_metadata: List[FileMetadata] = []

    # Additional practical session states for UI/logic control
    if "processing_files" not in st.session_state:
        # Indicates if files are currently being processed (e.g., uploaded, indexed)
        st.session_state.processing_files: bool = False
    if "rag_engine_active" not in st.session_state:
        # Indicates if a RAG query engine (with a store) is currently active and ready
        st.session_state.rag_engine_active: bool = False

# --- Chat Message History Management ---

def get_chat_messages() -> List[ChatMessage]:
    """
    Retrieves the current list of chat messages from the session state.

    Returns:
        List[ChatMessage]: A list of chat messages.
    """
    return st.session_state.messages

def add_chat_message(role: str, content: str, timestamp: Optional[datetime] = None, citations: Optional[List[str]] = None) -> None:
    """
    Adds a new message to the chat history in the session state.

    Args:
        role (str): The role of the message sender (e.g., "user", "assistant").
        content (str): The content of the message.
        timestamp (Optional[datetime]): The datetime when the message was created. Defaults to now if None.
        citations (Optional[List[str]]): A list of source citations for assistant messages.
    """
    message_data = {
        "role": role,
        "content": content,
        "timestamp": (timestamp if timestamp else datetime.now()).isoformat(),  # Store as ISO string
    }
    if citations:
        message_data["citations"] = citations
    st.session_state.messages.append(message_data)

def clear_chat_messages() -> None:
    """
    Clears all chat messages from the session state.
    """
    st.session_state.messages = []

# --- File Search Store Information Management ---

def get_file_store_info() -> tuple[str, Optional[str]]:
    """
    Retrieves the current file search store name and ID from the session state.

    Returns:
        tuple[str, Optional[str]]: A tuple containing the store name and store ID.
                                   `store_id` will be `None` if not yet set.
    """
    return st.session_state.store_name, st.session_state.store_id

def set_file_store_info(store_name: str, store_id: str) -> None:
    """
    Sets the file search store name and ID in the session state.

    Args:
        store_name (str): The display name of the file search store.
        store_id (str): The unique identifier of the file search store.
    """
    st.session_state.store_name = store_name
    st.session_state.store_id = store_id

def clear_file_store_info() -> None:
    """
    Clears the file search store name and ID from the session state,
    resetting to default values defined in `config.py` and `None` for ID.
    """
    st.session_state.store_name = config.DEFAULT_STORE_DISPLAY_NAME
    st.session_state.store_id = None

# --- Uploaded Document Metadata Management ---

def get_uploaded_files_metadata() -> List[FileMetadata]:
    """
    Retrieves the list of metadata for uploaded documents from the session state.

    Returns:
        List[FileMetadata]: A list of dictionaries, each representing file metadata.
    """
    return st.session_state.uploaded_files_metadata

def add_uploaded_file_metadata(file_name: str, file_size: int, upload_datetime: datetime, corpus_file_resource_name: str) -> None:
    """
    새로 업로드된 문서의 메타데이터를 세션 상태에 추가합니다.

    Args:
        file_name (str): 업로드된 파일의 이름.
        file_size (int): 업로드된 파일의 크기(바이트).
        upload_datetime (datetime): 파일이 업로드된 시간. ISO 형식 문자열로 저장됩니다.
        corpus_file_resource_name (str): Google Gemini API에서 사용하는 코퍼스 파일의 전체 리소스 이름.
    """
    st.session_state.uploaded_files_metadata.append(
        {
            "name": file_name,
            "size": file_size,
            "upload_date": upload_datetime.isoformat(),
            "corpus_file_resource_name": corpus_file_resource_name
        }
    )

def remove_uploaded_file_metadata(file_name: str) -> bool:
    """
    주어진 파일 이름과 일치하는 업로드된 문서 메타데이터를 세션 상태에서 제거합니다.

    Args:
        file_name (str): 제거할 파일의 이름.

    Returns:
        bool: 메타데이터 제거 성공 시 True, 해당 파일을 찾을 수 없으면 False.
    """
    initial_count = len(st.session_state.uploaded_files_metadata)
    st.session_state.uploaded_files_metadata = [
        f for f in st.session_state.uploaded_files_metadata if f["name"] != file_name
    ]
    return len(st.session_state.uploaded_files_metadata) < initial_count

def clear_uploaded_files_metadata() -> None:
    """
    Clears all uploaded document metadata from the session state.
    """
    st.session_state.uploaded_files_metadata = []

# --- General UI/Process State Management ---

def set_processing_files_status(status: bool) -> None:
    """
    Sets the status indicating whether files are currently being processed
    (e.g., uploading, indexing, creating store).

    Args:
        status (bool): True if files are being processed, False otherwise.
    """
    st.session_state.processing_files = status

def get_processing_files_status() -> bool:
    """
    Retrieves the status indicating whether files are currently being processed.

    Returns:
        bool: True if files are being processed, False otherwise.
    """
    return st.session_state.processing_files

def set_rag_engine_active_status(status: bool) -> None:
    """
    Sets the status indicating whether a RAG query engine is currently active
    and ready to answer questions based on a file store.

    Args:
        status (bool): True if a RAG engine is active, False otherwise.
    """
    st.session_state.rag_engine_active = status

def get_rag_engine_active_status() -> bool:
    """
    Retrieves the status indicating whether a RAG query engine is currently active.

    Returns:
        bool: True if a RAG engine is active, False otherwise.
    """
    return st.session_state.rag_engine_active
