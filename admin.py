import streamlit as st
from connectsql import load_faq, add_faq, update_faq, delete_faq, load_unanswered_logs, display_statistics

def admin_interface():
    st.title("Quản lý Dữ liệu Chatbot")

    tab_add, tab_edit, tab_load_logs, tab_statistics = st.tabs(["Thêm dữ liệu", "Chỉnh sửa dữ liệu", "Quản lý Log Chatbot", "Thống kê"])

    with tab_add:
        question = st.text_input("Thêm câu hỏi:")
        answer = st.text_area("Thêm câu trả lời:")
        if st.button("Thêm dữ liệu"):
            if question and answer:
                add_faq(question, answer)
                st.success("Dữ liệu đã được thêm thành công!")
            else:
                st.warning("Vui lòng nhập đầy đủ thông tin!")

    with tab_edit:
        questions, _ = load_faq()
        selected_question = st.selectbox("Chọn câu hỏi để chỉnh sửa:", questions)
        new_question = st.text_input("Cập nhật câu hỏi:", value=selected_question)
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