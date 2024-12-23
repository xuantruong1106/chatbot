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


def get_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def split_text_into_chunks(text, chunk_size=1024, overlap=50):
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


def generate_questions_and_answers_from_chunks(chunks):
    try:
        # Initialize question generation pipeline
        question_generator = pipeline(
            "text2text-generation",
            model="facebook/bart-large-cnn",
            max_length=128,
            device=0 if torch.cuda.is_available() else -1
        )

        # Initialize answer generation pipeline
        answer_generator = pipeline(
            "text2text-generation",
            model="facebook/bart-large-cnn",
            max_length=256,
            device=0 if torch.cuda.is_available() else -1
        )

        question_answer_pairs = []

        for chunk in chunks:
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue

            # Generate questions
            input_text = f"generate question: {chunk}"
            questions = question_generator(input_text, num_return_sequences=2)

            for q in questions:
                question = q['generated_text'].strip()

                # Generate answer
                context = f"answer question: {question}\ncontext: {chunk}"
                answer = answer_generator(context, num_return_sequences=1)[
                    0]['generated_text']

                if len(question) > 10 and len(answer) > 20:  # Basic quality check
                    question_answer_pairs.append((question, answer))

        return question_answer_pairs

    except Exception as e:
        print(f"Error in question generation: {e}")
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
        st.subheader("Tự động sinh câu hỏi từ tài liệu PDF")

        # List available PDFs
        docs = [file.name for file in docs_path.iterdir()
                if file.suffix == ".pdf"]
        selected_doc = st.selectbox("Chọn tài liệu:", docs)

        if st.button("Sinh câu hỏi"):
            pdf_path = docs_path / selected_doc
            pdf_text = get_pdf_text(pdf_path)  # Extract text from PDF

            if pdf_text.strip():
                # Chia văn bản thành các đoạn nhỏ
                chunks = split_text_into_chunks(pdf_text)

                print(chunks)

                # Sinh câu hỏi và câu trả lời từ các đoạn văn bản
                question_answer_pairs = generate_questions_and_answers_from_chunks(
                    chunks)

                print(question_answer_pairs)

                # Hiển thị câu hỏi và câu trả lời
                if question_answer_pairs:
                    for question, answer in question_answer_pairs:
                        st.write(f"**Câu hỏi:** {question}")
                        st.write(f"**Câu trả lời:** {answer}")
                        if st.button(f"Lưu câu hỏi: {question}"):
                            # Lưu câu hỏi và câu trả lời vào database
                            add_faq(question, answer)
                            st.success("Câu hỏi đã được lưu thành công!")
                else:
                    st.warning("Không thể sinh câu hỏi từ tài liệu này.")
            else:
                st.error(
                    "Không thể đọc nội dung từ file PDF. Vui lòng kiểm tra lại file.")
