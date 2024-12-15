import streamlit as st
import pandas as pd
from connectsql import handle_csv_upload, load_faq, add_faq, load_unanswered_questions, update_answer_for_unanswered, update_faq, delete_faq, load_unanswered_logs, display_statistics, save_to_faqs
from trainpdf import extract_text_from_pdf, generate_questions


def admin_interface():
    st.title("Quản lý Dữ liệu Chatbot")

    tab_add, tab_training, tab_edit, tab_load_logs, tab_statistics, tab_unanswered, tab_trainpdf = st.tabs(
        ["Thêm dữ liệu", "Huấn luyện chatbot", "Chỉnh sửa dữ liệu",
            "Quản lý Log Chatbot", "Thống kê", "Câu hỏi chưa trả lời", "Huấn luyện bằng PDF"]
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
            # Lấy danh sách câu hỏi (cột đầu tiên của mỗi tuple)
            question_texts = [q[0] for q in unanswered_questions]

            selected_question = st.selectbox(
                "Chọn câu hỏi chưa trả lời", question_texts)

            # Lấy thông tin của câu hỏi đã chọn
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
        
        
        
# ------------------------------Train PDF---------------------------------------        
    with tab_trainpdf:
        st.header("Huấn luyện bằng PDF")
        
        uploaded_file = st.file_uploader("Tải lên file PDF", type="pdf")

        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            st.text_area("Nội dung PDF:", text, height=300)
            
            if st.button("Huấn luyện"):
                questions_and_answers = generate_questions(text)
    
                for q in questions_and_answers:
                    save_to_faqs(q["question"], q["answer"])
                    st.success("Huấn luyện thành công! Các câu hỏi đã được lưu.")
                else:
                    st.error("Không thể sinh câu hỏi từ nội dung PDF.")
