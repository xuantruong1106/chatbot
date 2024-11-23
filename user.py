import time
import streamlit as st
from suggestion_file import select_suggestion
from rapidfuzz import process
from st_alys import compare_strings_highest_score
from connectsql import mactching_with_load_from_postgresql, get_answer, get_answer_id_faq_from_key_word, load_from_postgresql, load_faq, log_chat

chat_container = st.empty()



def typewriter_effect(text, speed=0.01):
    response = st.empty()
    for i in range(1, len(text) + 1):
        response.markdown(text[:i])
        time.sleep(speed)
        
def handle_user_input(user_input):
    matching = mactching_with_load_from_postgresql(user_input)  
    if matching:
        return get_answer(user_input)
    elif matching == False:
       return (get_answer_id_faq_from_key_word(user_input))
    else:
        return 'handle_user_input - Xin lỗi, mình không tìm thấy câu trả lời phù hợp!'


def user_interface():
    
    st.title("Chatbot Giải Đáp Thắc Mắc")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and message["content"].startswith("```") and message["content"].endswith("```"):
                    st.code(message["content"][3:-3], language="text")  
                else:
                    st.markdown(message["content"])

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
        submit_button = st.form_submit_button("Gửi")
        
        answer = None

        if submit_button and user_input.strip():
            
            st.session_state.user_input = user_input 
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            
            question_suggestions = select_suggestion(user_input)
            questions, answers = load_faq()
            result = process.extractOne(user_input, questions, score_cutoff=70)
            
            
            if question_suggestions: 
                answer = handle_user_input(user_input)
            else:
                    for question in load_from_postgresql():
                        if compare_strings_highest_score(user_input, question) >= 0.75:
                            answer = get_answer(question)
                            break
                                  
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
