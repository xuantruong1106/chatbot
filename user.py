import os
import time
import streamlit as st
from suggestion_file import select_suggestion
from rapidfuzz import process
from st_alys import compare_strings_highest_score
from connectsql import mactching_with_load_from_postgresql, get_answer, get_answer_id_faq_from_key_word, load_from_postgresql, load_faq, log_chat, save_pdf_answer_to_db
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import fitz  # PyMuPDF for reading PDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

chat_container = st.empty()
DetectorFactory.seed = 0

# Đọc nội dung từ một file PDF
def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.split('. ')  # Chia thành các câu

# Đọc nội dung từ tất cả các file PDF trong thư mục
def read_all_pdfs(directory_path):
    all_sentences = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(directory_path, file_name)
            sentences = read_pdf(file_path)
            all_sentences.extend(sentences)
    return all_sentences

# Tìm câu tương đồng nhất trong nội dung PDF
def find_best_match(question, pdf_content):
    if not pdf_content:
        return None 
    vectorizer = TfidfVectorizer().fit_transform([question] + pdf_content)
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    best_match_index = cosine_similarities.argmax()
    best_score = cosine_similarities[best_match_index]
    return pdf_content[best_match_index] if best_score >= 0.2 else None  # Ngưỡng tương đồng là 20%

def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except Exception as e:
        return f"Lỗi nhận biết ngôn ngữ: {e}"

def translate_text(text, target_lang, detected_lang):
    try:
        translation = GoogleTranslator(
            source=detected_lang, target=target_lang).translate(text)
        return translation
    except Exception as e:
        return None, f"Lỗi dịch thuật: {e}"

def handle_user_input(user_input, pdf_content=None):
    # Tìm câu trả lời từ cơ sở dữ liệu
    matching = mactching_with_load_from_postgresql(user_input)
    if matching:
        answer, is_answer = get_answer(user_input)
    elif matching == False:
        answer, is_answer = get_answer_id_faq_from_key_word(user_input)
    else:
        answer = 'error'
        is_answer = False

    # Nếu không tìm thấy câu trả lời, kiểm tra nội dung PDF
    if not is_answer and pdf_content:
        pdf_match = find_best_match(user_input, pdf_content)
        if pdf_match:
            answer = pdf_match
            is_answer = True
            save_pdf_answer_to_db(user_input, answer)  # Lưu câu hỏi và câu trả lời vào cơ sở dữ liệu

    # Nếu không tìm thấy câu trả lời trong cơ sở dữ liệu và PDF
    if not is_answer:
        answer = "Rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau."
        log_chat("anonymous", user_input, answer, False)  # Lưu câu hỏi vào logs

    return answer or "Xin lỗi, hiện tại không tìm thấy câu trả lời phù hợp.", is_answer

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
        user_input = st.text_input(
            "Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
        submit_button = st.form_submit_button("Gửi")

        # Đường dẫn đến thư mục chứa file PDF
        pdf_directory = "docs"
        pdf_content = read_all_pdfs(pdf_directory)

        if submit_button and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Xử lý ngôn ngữ
            lang = detect_language(user_input)
            if lang != 'vi':
                user_input = translate_text(text=user_input, target_lang='vi', detected_lang=lang)

            answer, is_answered = handle_user_input(user_input, pdf_content=pdf_content)
            st.session_state.messages.append({"role": "assistant", "content": f"```\n{answer}\n```"})

            st.rerun()