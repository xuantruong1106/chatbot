import streamlit as st
import pandas as pd
from connectsql import connect_to_postgresql, load_faq, add_faq, load_unanswered_questions, update_answer_for_unanswered, update_faq, delete_faq, load_unanswered_logs, display_statistics
import os
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from sentence_transformers import util


def handle_csv_upload():
    uploaded_file = st.file_uploader("Tải lên file CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Kiểm tra các cột của CSV để đảm bảo có cột 'question' và 'answer'
            if 'question' in df.columns and 'answer' in df.columns:
                progress_bar = st.progress(0)
                progress_text = st.empty()
                total_questions = len(df)

                for index, row in df.iterrows():
                    question = row['question']
                    answer = row['answer']

                    if is_question_duplicate(question):
                        st.warning(
                            f"Câu hỏi '{question}' đã tồn tại trong cơ sở dữ liệu và không được thêm.")
                    else:
                        add_faq(question, answer)
                        st.success(
                            f"Câu hỏi '{question}' đã được thêm thành công!")

                    progress = (index + 1) / total_questions
                    progress_bar.progress(progress)
                    progress_text.text(f"Đang xử lý: {int(progress * 100)}%")

                st.success("Hoàn thành việc huấn luyện từ file CSV!")
            else:
                st.error("File CSV không chứa các cột 'question' và 'answer'.")
        except Exception as e:
            st.error(f"Lỗi khi xử lý file CSV: {e}")


def is_question_duplicate(question):
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM faq WHERE question = %s", (question,))
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count > 0
    except Exception as e:
        print(f"Lỗi khi kiểm tra câu hỏi: {e}")
        return False

def filter_duplicate_questions(questions, model):
    embeddings = model.encode(questions, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)
    
    filtered_questions = []
    for i, question in enumerate(questions):
        if all(cosine_scores[i][j] < 0.85 for j in range(len(filtered_questions))):
            filtered_questions.append(question)
    return filtered_questions

# Chunking function


def split_text_into_chunks(text, chunk_size=512, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

# Embedding generation function


def generate_embeddings(chunks):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

# Question generation function


def generate_questions_and_answers_from_chunks(chunks):
    question_answer_pairs = []
    question_generator = pipeline(
        "text2text-generation", model="google/flan-t5-base", num_beams=5)  # Added beam search

    answer_generator = pipeline(
        "question-answering", model="deepset/roberta-base-squad2")

    for chunk in chunks:
        # Generate questions with beam search (allows multiple sequences)
        generated_questions = question_generator(
            chunk, max_length=128, num_return_sequences=5, num_beams=5, early_stopping=True)  # Now supports num_return_sequences = 2 with beam search

        for question in generated_questions:
            question_text = question['generated_text']
            # Generate answers based on the question and chunk of text
            answer = answer_generator(
                question=question_text, context=chunk, max_answer_length=50)['answer']
            question_answer_pairs.append((question_text, answer))

    return question_answer_pairs


# Function to extract text from PDF


def get_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def admin_interface():
    st.title("Quản lý Dữ liệu Chatbot")

    # Đảm bảo thư mục docs tồn tại
    docs_path = Path("docs")
    docs_path.mkdir(exist_ok=True)

    tab_add, tab_training, tab_edit, tab_load_logs, tab_statistics, tab_unanswered, tab_generate_question = st.tabs(
        ["Thêm dữ liệu", "Huấn luyện chatbot", "Chỉnh sửa dữ liệu",
         "Quản lý Log Chatbot", "Thống kê", "Câu hỏi chưa trả lời", "Tự tạo câu hỏi"]
    )

    with tab_add:
        if "question_input" not in st.session_state:
            st.session_state.question_input = ""
        if "answer_input" not in st.session_state:
            st.session_state.answer_input = ""

        question = st.text_input(
            "Thêm câu hỏi:", value=st.session_state.question_input)
        answer = st.text_area("Thêm câu trả lời:",
                              value=st.session_state.answer_input)

        if st.button("Thêm dữ liệu"):
            if question and answer:
                if add_faq(question, answer):
                    st.session_state.question_input = ""
                    st.session_state.answer_input = ""
                    st.success("Dữ liệu đã được thêm thành công!")
                else:
                    st.warning("Câu hỏi đã tồn tại trong cơ sở dữ liệu!")
            else:
                st.warning("Vui lòng nhập đầy đủ thông tin!")

        st.write("---")
        st.subheader("Thêm file PDF")

        uploaded_pdf = st.file_uploader("Chọn file PDF để upload:", type="pdf")

        if uploaded_pdf:
            pdf_path = docs_path / uploaded_pdf.name
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            st.success(
                f"File {uploaded_pdf.name} đã được lưu vào thư mục docs!")

    with tab_edit:
        questions, _ = load_faq()
        selected_question = st.selectbox(
            "Chọn câu hỏi để chỉnh sửa:", questions)
        new_question = st.text_input(
            "Cập nhật câu hỏi:", value=selected_question)
        new_answer = st.text_area("Cập nhật câu trả lời:")
        if st.button("Cập nhật"):
            update_faq(selected_question, new_question, new_answer)
            st.success("Dữ liệu đã được cập nhật thành công!")
        if st.button("Xóa"):
            delete_faq(selected_question)
            st.success("Dữ liệu đã được xóa thành công!")

    with tab_load_logs:
        logs = load_unanswered_logs()

        if logs:
            st.table([{
                "Người dùng": log[0],
                "Câu hỏi": log[1],
                "Thời gian": log[2].strftime("%Y-%m-%d %H:%M:%S")
            } for log in logs])
        else:
            st.write("Hiện chưa có câu hỏi nào chưa được trả lời.")

    with tab_statistics:
        if st.session_state['role'] == 'admin':
            display_statistics()

    with tab_unanswered:
        unanswered_questions = load_unanswered_questions()

        if unanswered_questions:
            question_texts = [q[0] for q in unanswered_questions]

            selected_question = st.selectbox(
                "Chọn câu hỏi chưa trả lời", question_texts)

            question_info = next(
                q for q in unanswered_questions if q[0] == selected_question)
            question_text = question_info[0]
            timestamp = question_info[1]

            st.write(f"**Câu hỏi:** {question_text}")
            st.write(f"**Thời gian:** {timestamp}")

            if "answer_input" not in st.session_state:
                st.session_state.answer_input = ""

            answer_input = st.text_area(
                "Nhập câu trả lời:", value=st.session_state.answer_input, key="answer_input")

            if st.button("Cập nhật câu trả lời"):
                if answer_input.strip():
                    update_answer_for_unanswered(question_text, answer_input)
                    st.success("Câu trả lời đã được cập nhật!")
                    st.session_state.answer_input = ""
                else:
                    st.warning("Vui lòng nhập câu trả lời!")
        else:
            st.write("Hiện chưa có câu hỏi nào chưa được trả lời.")

    with tab_training:
        st.header("Huấn luyện Chatbot")
        handle_csv_upload()

    with tab_generate_question:
        st.subheader("Tự động sinh câu hỏi từ tài liệu PDF")

        # List available PDFs
        docs = [file.name for file in docs_path.iterdir()
                if file.suffix == ".pdf"]
        selected_doc = st.selectbox("Chọn tài liệu:", docs)

        if st.button("Sinh câu hỏi"):
            pdf_path = docs_path / selected_doc
            pdf_text = get_pdf_text(pdf_path)  # Extract text from PDF

            if pdf_text.strip():
                # Chunk the text
                chunks = split_text_into_chunks(pdf_text)

                # Generate embeddings (optional, not used in this example)
                embeddings = generate_embeddings(chunks)

                # Generate questions
                question_answer_pairs = generate_questions_and_answers_from_chunks(
                    chunks)

                if question_answer_pairs:
                    for question, answer in question_answer_pairs:
                        st.write(f"**Câu hỏi:** {question}")
                        st.write(f"**Câu trả lời:** {answer}")
                        if st.button(f"Lưu câu hỏi: {question, answer}"):
                            # Save question without an answer
                            add_faq(question, answer)
                            st.success("Câu hỏi đã được lưu thành công!")
                else:
                    st.warning("Không thể sinh câu hỏi từ tài liệu này.")
            else:
                st.error(
                    "Không thể đọc nội dung từ file PDF. Vui lòng kiểm tra lại file.")
