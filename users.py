import streamlit as st
from database import load_faq, log_unanswered, log_chat
from rapidfuzz import process
import time

def typewriter_effect(text, speed=0.01):
    response = st.empty()
    for i in range(1, len(text) + 1):
        response.markdown(text[:i])
        time.sleep(speed)

def user_interface():
    st.title("Chatbot Giải Đáp Thắc Mắc")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
        submit_button = st.form_submit_button("Gửi")

        if submit_button and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Tìm câu trả lời từ FAQ
            questions, answers = load_faq()
            result = process.extractOne(user_input, questions, score_cutoff=70)

            if result:
                best_match = result[0]
                answer = answers[best_match]
                is_answered = True
                log_chat(st.session_state['username'], user_input, answer, is_answered)
            else:
                answer = "Xin lỗi, mình không tìm thấy câu trả lời phù hợp!"
                is_answered = False

                # Lưu log cho câu hỏi không có câu trả lời
                log_chat(st.session_state['username'], user_input, answer, is_answered)

            # Lưu tin nhắn của chatbot vào session_state
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Hiển thị câu trả lời
            typewriter_effect(answer)

