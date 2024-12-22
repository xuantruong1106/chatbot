import time
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from suggestion_file import select_suggestion
from rapidfuzz import process
from st_alys import compare_strings_highest_score
from connectsql import add_faq, mactching_with_load_from_postgresql, get_answer, get_answer_id_faq_from_key_word, load_from_postgresql, log_chat
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import pdfplumber
from pathlib import Path

# Cấu hình ban đầu
chat_container = st.empty()
DetectorFactory.seed = 0
pdf_path = Path("./docs")


def get_pdf_text(pdf_path):
    """Đọc nội dung từ file PDF."""
    try:
        text = ""
        # Lấy danh sách tất cả các file PDF trong thư mục
        pdf_files = Path(pdf_path).glob("*.pdf")
        for pdf_file in pdf_files:
            with pdfplumber.open(pdf_file) as pdf_reader:
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Lỗi khi đọc PDF: {e}"


def get_text_chunks(text):
    """Chia nội dung văn bản thành các đoạn nhỏ."""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


def get_conversation_chain(vectorstore):
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs={"temperature": 0.5, "max_length": 1024}
    )
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)


def detect_language(text):
    """Phát hiện ngôn ngữ của văn bản."""
    try:
        return detect(text)
    except Exception as e:
        return f"Lỗi nhận biết ngôn ngữ: {e}"


def translate_text(text, target_lang, detected_lang):
    """Dịch văn bản sang ngôn ngữ đích."""
    try:
        return GoogleTranslator(source=detected_lang, target=target_lang).translate(text)
    except Exception as e:
        return None


def handle_user_input(user_input):
    """Xử lý đầu vào từ người dùng để tìm câu trả lời trong cơ sở dữ liệu."""
    matching = mactching_with_load_from_postgresql(user_input)
    if matching:
        return get_answer(user_input)
    elif matching == False:
        return get_answer_id_faq_from_key_word(user_input)
    else:
        return 'Không tìm thấy câu trả lời.', False


def handle_input_with_pdf(user_question):
    """Tìm câu trả lời từ PDF nếu không có trong cơ sở dữ liệu."""
    response = st.session_state.conversation({'question': user_question})
    if 'chat_history' in response:
        chat_history = response['chat_history']
        return chat_history[-1].content, True
    return None, False


def user_interface():
    """Giao diện chính của ứng dụng."""
    load_dotenv()
    st.title("Chatbot Giải Đáp Thắc Mắc")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "username" not in st.session_state:
        st.session_state.username = "Người dùng"

    raw_text = get_pdf_text(pdf_path)

    print("Dịch nội dung PDF sang tiếng Anh...")
    translated_text = translate_text(
        raw_text, detected_lang="vi", target_lang="en")
    
  
    text_chunks = get_text_chunks(translated_text)
    
    vectorstore = get_vectorstore(text_chunks)

    st.session_state.conversation = get_conversation_chain(vectorstore)

    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
        submit_button = st.form_submit_button("Gửi")

        if submit_button and user_input.strip():
            st.session_state.messages.append(
                {"role": "user", "content": user_input})

            lang = detect_language(user_input)
            if lang != 'vi':
                user_input = translate_text(
                    user_input, target_lang='vi', detected_lang=lang)

            print("Đầu vào:", user_input)

            answer, is_answered = None, False

            question_suggestions = select_suggestion(user_input)
            print("Các câu hỏi gần nhất: ", question_suggestions)

            # question_suggestions = select_suggestion(user_input)

            # if question_suggestions:
            #     answer, is_answered = handle_user_input(user_input)
            #     have_answer = 1
            #     log_chat(st.session_state['username'],
            #              user_input, answer, is_answered)
            # else:
            for question in load_from_postgresql():
                print("Question: ", question)
                if compare_strings_highest_score(user_input, question):
                    print("Câu hỏi đúng: ", question)
                    answer, is_answered = handle_user_input(question)
                    log_chat(
                        st.session_state['username'], user_input, answer, is_answered)
                    break

            # answer, is_answered = handle_user_input(user_input)

            if is_answered == False:
                print("Không tìm thấy câu trả lời trong cơ sở dữ liệu.")
                question = translate_text(
                    user_input, detected_lang="vi", target_lang="en")
                answer, is_answered = handle_input_with_pdf(question)
                print("Dịch câu trả lời sang tiếng Việt...")
                answer = translate_text(
                    answer, detected_lang="en", target_lang="vi")
                add_faq(user_input, answer)
                print("Đã thêm vào csdl")
                log_chat(st.session_state['username'],
                         user_input, answer, is_answered)
                print("Câu trả lời:", answer)

            if not answer:
                answer = 'Rất cảm ơn câu hỏi, nhà trường sẽ giải đáp sau.'

            answer_lang = detect_language(answer)
            if answer_lang == 'vi' and lang != 'vi':
                answer = translate_text(
                    answer, target_lang=lang, detected_lang='vi')
            print("Câu trả lời:", answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": f"```\n{answer}\n```"})

            log_chat(st.session_state['username'],
                     user_input, answer, is_answered)

            st.rerun()


if __name__ == "__main__":
    user_interface()
