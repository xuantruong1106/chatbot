import time
import streamlit as st
from suggestion_file import select_suggestion
from rapidfuzz import process
from st_alys import compare_strings_highest_score
from connectsql import mactching_with_load_from_postgresql, get_answer, get_answer_id_faq_from_key_word, load_from_postgresql, load_faq, log_chat
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

chat_container = st.empty()

DetectorFactory.seed = 0

def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except Exception as e:
        return f"Lỗi nhận biết ngôn ngữ: {e}"

def translate_text(text, target_lang, detected_lang):
    """Dịch văn bản sang ngôn ngữ đích"""
    try:
        translation = GoogleTranslator(
            source=detected_lang, target=target_lang).translate(text)
        return translation
    except Exception as e:
        return None, f"Lỗi dịch thuật: {e}"

def typewriter_effect(text, speed=0.01):
    response = st.empty()
    for i in range(1, len(text) + 1):
        response.markdown(text[:i])
        time.sleep(speed)

def handle_user_input(user_input):
    # Tìm câu trả lời từ cơ sở dữ liệu
    matching = mactching_with_load_from_postgresql(user_input)
    if matching:
        answer, is_answer = get_answer(user_input)
    elif matching == False:
        answer, is_answer = get_answer_id_faq_from_key_word(user_input)
    else:
        answer = 'error'
        is_answer = False
        
    return answer, is_answer

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
        user_input = st.text_input(
            "Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
        submit_button = st.form_submit_button("Gửi")

        user_input_temp = user_input
        answer = None

        if submit_button and user_input.strip():

            st.session_state.user_input = user_input
            st.session_state.messages.append(
                {"role": "user", "content": user_input})

            lang = detect_language(user_input)

            if lang != 'vi':
                user_input = translate_text(text=user_input,
                                         target_lang='vi', detected_lang=lang)

            question_suggestions = select_suggestion(user_input)

            if question_suggestions:
                answer, is_answered = handle_user_input(user_input)  
                log_chat(st.session_state['username'],user_input, answer, is_answered)
            else:
                for question in load_from_postgresql():
                    if compare_strings_highest_score(user_input, question) >= 0.75:
                        answer, is_answered = get_answer(question)
                        log_chat(st.session_state['username'],user_input, answer, is_answered)
                        break
            
            answer_lang = detect_language(answer)
            user_input_temp_lang = detect_language(user_input_temp)

            if answer_lang == 'vi' and user_input_temp_lang != 'vi':
                answer = translate_text(text=answer,
                                        detected_lang=answer_lang, target_lang=user_input_temp_lang)
            st.session_state.messages.append(
                {"role": "assistant", "content":  f"```\n{answer}\n```"})
            # reload để hiển thị kết quả ngay lập tức
            st.rerun()
