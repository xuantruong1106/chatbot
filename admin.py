from sentence_transformers import SentenceTransformer
import streamlit as st
import pandas as pd
import torch
from connectsql import (
    connect_to_postgresql, is_question_duplicate, load_faq, add_faq,
    load_unanswered_logs, load_unanswered_questions, show_statistics, update_faq, delete_faq
)
from pathlib import Path
from transformers import pipeline
from sentence_transformers import util
from PyPDF2 import PdfReader
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
from transformers import T5ForConditionalGeneration, AutoTokenizer
import logging
from typing import List, Tuple, Optional
from tqdm import tqdm
import numpy as np
import re

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

docs_path = Path("D:\\chatbot\\docs")


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


class QAGenerator:
    def __init__(self):
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model = T5ForConditionalGeneration.from_pretrained(
            "VietAI/vit5-base").to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-base")
        self.similarity_model = SentenceTransformer(
            'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')

    def preprocess_text(self, text: str) -> str:
        # Chuẩn hóa text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def postprocess_text(self, text: str) -> str:
        # Xử lý output
        text = re.sub(
            r'[^\x00-\x7F\u0100-\u017F\u0180-\u024F\u1EA0-\u1EF9\u0300-\u036f]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_question(self, context: str) -> list[str]:
        context = self.preprocess_text(context)
        input_text = f"hãy đặt câu hỏi dựa trên đoạn văn sau: {context}"

        inputs = self.tokenizer(input_text,
                                return_tensors="pt",
                                max_length=512,
                                truncation=True).to(self.device)

        outputs = self.model.generate(
            inputs.input_ids,
            max_length=128,
            min_length=10,
            num_return_sequences=3,
            num_beams=5,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            no_repeat_ngram_size=2,
            do_sample=True
        )

        questions = []
        for output in outputs:
            question = self.tokenizer.decode(output, skip_special_tokens=True)
            question = self.postprocess_text(question)
            if len(question) > 10:
                questions.append(question)

        return questions

    def generate_answer(self, question: str, context: str) -> str:
        question = self.preprocess_text(question)
        context = self.preprocess_text(context)

        input_text = f"trả lời câu hỏi sau dựa trên đoạn văn: câu hỏi: {question} đoạn văn: {context}"

        inputs = self.tokenizer(input_text,
                                return_tensors="pt",
                                max_length=512,
                                truncation=True).to(self.device)

        outputs = self.model.generate(
            inputs.input_ids,
            max_length=256,
            min_length=20,
            num_beams=5,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            no_repeat_ngram_size=2
        )

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.postprocess_text(answer)

    def evaluate_qa_quality(self, question: str, answer: str, context: str) -> bool:
        # Kiểm tra độ dài tối thiểu
        if len(question) < 10 or len(answer) < 20:
            return False

        # Kiểm tra chất lượng văn bản
        if not re.match(r'^[\w\s\.,\?\!]+$', question) or not re.match(r'^[\w\s\.,\?\!]+$', answer):
            return False

        # Đánh giá độ tương đồng
        try:
            embeddings = self.similarity_model.encode(
                [question, answer, context])
            q_c_similarity = np.dot(embeddings[0], embeddings[2])
            a_c_similarity = np.dot(embeddings[1], embeddings[2])
            return q_c_similarity > 0.5 and a_c_similarity > 0.6
        except:
            return False


class PDFProcessor:
    @staticmethod
    def get_pdf_text(pdf_path: Path) -> str:
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Lỗi đọc PDF: {e}")
            return ""

    @staticmethod
    def improve_chunk_quality(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        try:
            sentences = text.split('.')
            chunks = []
            current_chunk = []
            current_length = 0

            for sentence in sentences:
                sentence = sentence.strip() + '.'
                sentence_length = len(sentence.split())

                if current_length + sentence_length > chunk_size:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = sentence_length
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length

            if current_chunk:
                chunks.append(' '.join(current_chunk))

            return chunks
        except Exception as e:
            logger.error(f"Lỗi xử lý chunks: {e}")
            return []


def process_pdf_and_generate_qa(pdf_path: Path) -> List[Tuple[str, str]]:
    try:
        processor = PDFProcessor()
        generator = QAGenerator()

        # Đọc và xử lý PDF
        pdf_text = processor.get_pdf_text(pdf_path)
        if not pdf_text:
            st.error("Không thể đọc nội dung PDF")
            return []

        # Chia thành chunks và sinh Q&A
        chunks = processor.improve_chunk_quality(pdf_text)
        qa_pairs = []

        with st.spinner("Đang sinh câu hỏi và câu trả lời..."):
            progress_bar = st.progress(0)
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:
                    continue

                questions = generator.generate_question(chunk)
                for question in questions:
                    answer = generator.generate_answer(question, chunk)
                    if answer and generator.evaluate_qa_quality(question, answer, chunk):
                        qa_pairs.append((question, answer))

                progress_bar.progress((i + 1) / len(chunks))

        return qa_pairs

    except Exception as e:
        logger.error(f"Lỗi trong quá trình xử lý: {e}")
        st.error(f"Có lỗi xảy ra: {str(e)}")
        return []


def admin_interface():
    if not st.session_state.get('authenticated', False):
        st.warning("Bạn chưa đăng nhập. Vui lòng đăng nhập trước.")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🔐 Thông tin tài khoản")
        st.write(f"**👤 Tên người dùng:** {st.session_state['username']}")
        st.write(
            f"**🔓 Vai trò:** {'Admin' if st.session_state['username'] == 'admin' else 'Người dùng'}")
        st.divider()
        if st.button("🚪Đăng xuất"):
            st.session_state['authenticated'] = False
            st.rerun()

    st.title("✨ Quản lý Dữ liệu Chatbot")

    # Tabs chính
    tab_add, tab_edit, tab_load_logs, tab_statistics, tab_generate_question = st.tabs(
        ["➕ Thêm Dữ liệu", "✏️ Chỉnh sửa Dữ liệu",
            "📋 Quản lý Log", "Thống kê", "🪄 Dự đoán dữ liệu"]
    )

    with tab_add:
        st.header("➕ Thêm Dữ liệu")
        st.markdown("### Nhập thông tin câu hỏi và câu trả lời:")
        col1, col2 = st.columns(2)
        with col1:
            question = st.text_input("Câu hỏi:")
        with col2:
            answer = st.text_area("Câu trả lời:")

        st.markdown("---")
        if st.button("Thêm vào FAQ", key="add_data"):
            if question and answer:
                if add_faq(question, answer):
                    st.success("✅ Dữ liệu đã được thêm thành công!")
                else:
                    st.warning("⚠️ Câu hỏi này đã tồn tại!")
            else:
                st.error("⛔ Vui lòng nhập đầy đủ thông tin!")

        with st.expander("📄 Upload File PDF"):
            uploaded_pdf = st.file_uploader("Chọn file PDF:", type="pdf")
            if uploaded_pdf:
                pdf_path = docs_path / uploaded_pdf.name
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())
                st.success(f"📂 File **{uploaded_pdf.name}** đã được lưu!")

        st.markdown("---")
        st.subheader("📄 Upload File Excel")

        uploaded_excel = st.file_uploader(
            "Chọn file Excel để upload:", type=["xlsx", "xls"])

        if uploaded_excel:
            try:
                df = pd.read_excel(uploaded_excel)
                if st.button("Thêm dữ liệu từ Excel", key="add_from_excel"):
                    added_count = 0
                    skipped_count = 0
                    for _, row in df.iterrows():
                        question, answer = row['Question'], row['Answer']
                        if question and answer:
                            if is_question_duplicate(question):
                                skipped_count += 1  # Đếm số câu hỏi bị bỏ qua
                            else:
                                if add_faq(question, answer):
                                    added_count += 1  # Đếm số câu hỏi được thêm
                    st.success(
                        f"✅ Đã thêm {added_count} câu hỏi từ file Excel!")
                    if skipped_count > 0:
                        st.warning(
                            f"⚠️ Bỏ qua {skipped_count} câu hỏi do đã tồn tại trong cơ sở dữ liệu.")
                else:
                    st.error("⛔ File Excel phải có cột 'Question' và 'Answer'!")
            except Exception as e:
                st.error(f"⛔ Lỗi khi đọc file Excel: {e}")

    with tab_edit:
        st.header("✏️ Chỉnh sửa Dữ liệu")  # Thêm biểu tượng cho tiêu đề
        questions, faq_data = load_faq()  # Giả sử faq_data chứa cả câu trả lời

        # Hộp chọn câu hỏi với biểu tượng
        selected_question = st.selectbox("🔍 Chọn câu hỏi:", questions)

        # Tìm câu trả lời tương ứng với câu hỏi đã chọn
        current_answer = faq_data[selected_question]

        # Nhập câu hỏi mới và câu trả lời mới
        new_question = st.text_input(
            "✏️ Cập nhật câu hỏi:", value=selected_question)
        # Hiển thị câu trả lời cũ
        new_answer = st.text_area(
            "📝 Cập nhật câu trả lời:", value=current_answer)

        col1, col2 = st.columns(2)

        # Cột Cập nhật với biểu tượng
        with col1:
            if st.button("✔️ Cập nhật", key="update_data"):
                update_faq(selected_question, new_question, new_answer)
                st.success("✅ Dữ liệu đã được cập nhật!")

        # Cột Xóa với biểu tượng
        with col2:
            if st.button("❌ Xóa", key="delete_data"):
                delete_faq(selected_question)
                st.success("✅ Dữ liệu đã được xóa!")

    with tab_statistics:
        show_statistics()

    with tab_load_logs:
        st.header("📋 Quản lý Câu Hỏi Chưa Trả Lời")
        logs = load_unanswered_questions()
        if logs:
            questions = [log[0] for log in logs]  # Thay đổi chỉ số
            selected_question = st.selectbox(
                "❓ Câu hỏi chưa trả lời:", questions, key="unanswered_questions_selectbox")

            st.markdown("### ✏️ Nhập câu trả lời:")
            answer = st.text_area(
                "Câu trả lời:", key="unanswered_questions_textarea")

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("💾 Lưu", key="save_log_answer"):
                    if selected_question and answer:
                        if add_faq(selected_question, answer):
                            st.success("✅ Câu trả lời đã được lưu!")
                        else:
                            st.warning("⚠️ Câu hỏi đã tồn tại!")
                    else:
                        st.error("⛔ Vui lòng nhập đầy đủ thông tin!")
            with col2:
                st.empty()  # Giữ khoảng trống để căn chỉnh nút lưu
        else:
            st.info("📭 Không có câu hỏi chưa được trả lời.")

    with tab_generate_question:
        st.subheader("🤖 Tự động sinh câu hỏi từ tài liệu PDF")

    # Hiển thị danh sách PDF
    docs_path = Path("D:\\chatbot\\docs")
    docs = [file.name for file in docs_path.iterdir()
            if file.suffix.lower() == ".pdf"]

    if not docs:
        st.warning("Không tìm thấy file PDF nào trong thư mục docs")
        return

    selected_doc = st.selectbox("📄 Chọn tài liệu:", docs)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎯 Bắt đầu sinh câu hỏi", key="generate_qa"):
            pdf_path = docs_path / selected_doc
            qa_pairs = process_pdf_and_generate_qa(pdf_path)

            if qa_pairs:
                st.session_state.qa_pairs = qa_pairs
                st.success(
                    f"Đã sinh được {len(qa_pairs)} cặp câu hỏi - trả lời")
            else:
                st.error("Không thể sinh câu hỏi từ tài liệu này")

    # Hiển thị kết quả nếu có
    if hasattr(st.session_state, 'qa_pairs'):
        st.subheader("📝 Kết quả sinh câu hỏi - trả lời")
        for i, (question, answer) in enumerate(st.session_state.qa_pairs):
            with st.expander(f"Câu hỏi {i+1}: {question}"):
                st.write("**Câu trả lời:**", answer)
                if st.button(f"💾 Lưu Q&A #{i+1}", key=f"save_qa_{i}"):
                    if add_faq(question, answer):
                        st.success("✅ Đã lưu thành công!")
                    else:
                        st.warning("⚠️ Câu hỏi này đã tồn tại!")
