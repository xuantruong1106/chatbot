import streamlit as st
import pandas as pd
from connectsql import (
    is_question_duplicate, load_faq, add_faq,
    load_unanswered_logs, load_unanswered_questions, update_faq, delete_faq
)
from pathlib import Path

docs_path = Path("docs")


def admin_interface():
    if not st.session_state.get('authenticated', False):
        st.warning("Bạn chưa đăng nhập. Vui lòng đăng nhập trước.")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🔐 Thông tin tài khoản")
        st.write(f"**👤 Tên người dùng:** {st.session_state['username']}")
        st.write(f"**🔓 Vai trò:** {'Admin' if st.session_state['username'] == 'admin' else 'Người dùng'}")
        st.divider()
        if st.button("🚪Đăng xuất"):
            st.session_state['authenticated'] = False
            st.rerun()

    st.title("✨ Quản lý Dữ liệu Chatbot")

    # Tabs chính
    tab_add, tab_edit, tab_load_logs = st.tabs(
        ["➕ Thêm Dữ liệu", "✏️ Chỉnh sửa Dữ liệu", "📋 Quản lý Log",]
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

    with tab_edit:
        st.header("✏️ Chỉnh sửa Dữ liệu")  # Thêm biểu tượng cho tiêu đề
        questions, faq_data = load_faq()  # Giả sử faq_data chứa cả câu trả lời

        # Hộp chọn câu hỏi với biểu tượng
        selected_question = st.selectbox("🔍 Chọn câu hỏi:", questions)

        # Tìm câu trả lời tương ứng với câu hỏi đã chọn
        current_answer = faq_data[selected_question]

        # Nhập câu hỏi mới và câu trả lời mới
        new_question = st.text_input("✏️ Cập nhật câu hỏi:", value=selected_question)
        new_answer = st.text_area("📝 Cập nhật câu trả lời:", value=current_answer)  # Hiển thị câu trả lời cũ

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



    with tab_load_logs:
        st.header("📋 Quản lý Câu Hỏi Chưa Trả Lời")
        logs = load_unanswered_questions()
        if logs:
            questions = [log[0] for log in logs]  # Thay đổi chỉ số
            selected_question = st.selectbox("❓ Câu hỏi chưa trả lời:", questions, key="unanswered_questions_selectbox")
            
            st.markdown("### ✏️ Nhập câu trả lời:")
            answer = st.text_area("Câu trả lời:", key="unanswered_questions_textarea")
            
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

