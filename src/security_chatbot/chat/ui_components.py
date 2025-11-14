"""
SecurityChatbot UI Components

Streamlit 채팅 인터페이스를 위한 재사용 가능한 UI 컴포넌트를 제공합니다.
"""

import streamlit as st
from typing import List, Dict, Union, Any
from datetime import datetime
import time  # For simulating loading

# ChatMessage 타입 정의
ChatMessage = Dict[str, Any]

def display_message(message: ChatMessage) -> None:
    """
    단일 채팅 메시지를 Streamlit의 st.chat_message를 사용하여 표시합니다.
    타임스탬프와 마크다운 포맷팅, 그리고 어시스턴트 메시지에 대한 출처를 지원합니다.

    Args:
        message: 'role', 'content', 'timestamp' (ISO format string) 키를 포함하는 딕셔너리입니다.
                 어시스턴트 메시지의 경우 선택적으로 'citations' (List[str]) 키를 포함할 수 있습니다.
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  # Markdown support
        if "timestamp" in message:
            # Display timestamp in a smaller, greyed-out font
            st.markdown(f"<p class='chat-timestamp'>{message['timestamp']}</p>", unsafe_allow_html=True)

        if message["role"] == "assistant" and "citations" in message and message["citations"]:
            st.markdown("<div class='chat-citation'>", unsafe_allow_html=True)
            st.markdown("**출처:**")
            for i, citation in enumerate(message["citations"]):
                st.markdown(f"- {citation}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_chat_history() -> None:
    """
    세션 상태에 저장된 모든 채팅 메시지를 렌더링합니다.
    """
    from security_chatbot.chat import session
    messages: List[ChatMessage] = session.get_chat_messages()
    for message in messages:
        display_message(message)


def process_chat_input() -> None:
    """
    사용자 입력을 처리하고, 유효성 검사 후 세션에 메시지를 추가하며,
    기본 에코 봇 응답을 생성하여 세션에 추가합니다.
    RAG 활성화 여부에 따라 다른 응답 로직을 사용합니다.
    """
    from security_chatbot.chat import session
    user_input: Union[str, None] = st.chat_input("메시지를 입력하세요...", disabled=session.get_processing_files_status())

    if user_input:
        current_time = datetime.now()
        session.add_chat_message(role="user", content=user_input, timestamp=current_time)

        # Simulate RAG response or echo bot
        if session.get_rag_engine_active_status():
            # Placeholder for RAG query
            with st.chat_message("assistant"):
                with st.spinner("생각 중..."):
                    time.sleep(2)  # Simulate RAG processing time
                assistant_response = f"RAG 기반 답변: '{user_input}'에 대한 보안 정보를 찾고 있습니다. (이것은 현재 에코 응답입니다.)"
                citations = ["보안 정책 문서 v1.0", "최신 위협 보고서 2023"]  # Mock citations
                st.markdown(assistant_response)
                st.markdown(f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>", unsafe_allow_html=True)
                st.markdown("<div class='chat-citation'>", unsafe_allow_html=True)
                st.markdown("**출처:**")
                for citation in citations:
                    st.markdown(f"- {citation}")
                st.markdown("</div>", unsafe_allow_html=True)
            session.add_chat_message(role="assistant", content=assistant_response, timestamp=datetime.now(), citations=citations)
        else:
            with st.chat_message("assistant"):
                with st.spinner("생각 중..."):
                    time.sleep(1)  # Simulate echo bot processing time
                assistant_response = f"Echo: {user_input}"
                st.markdown(assistant_response)
                st.markdown(f"<p class='chat-timestamp'>{datetime.now().isoformat()}</p>", unsafe_allow_html=True)
            session.add_chat_message(role="assistant", content=assistant_response, timestamp=datetime.now())

        st.rerun()
