import streamlit as st
from connectsql import connect_to_postgresql, load_from_postgresql, add_to_postgresql
from rapidfuzz import process
from suggestion_file import select_suggestion


# Streamlit UI
st.set_page_config(page_title="Chatbot Giải Đáp", page_icon="💬")

st.title("Chatbot Giải Đáp Thắc Mắc 💬")

tab1, tab2 = st.tabs(["💬 Chatbot", "🛠️ Thêm dữ liệu"])

# Load dữ liệu từ PostgreSQL
# questions, answers = load_from_postgresql()

# Tab 1: Chatbot
with tab1:
    st.write("Xin chào! Mình là chatbot hỗ trợ giải đáp các thắc mắc của sinh viên VKU. Bạn có thể hỏi mình bất kỳ điều gì liên quan đến trường!")
    user_input = st.text_input("Nhập câu hỏi của bạn:", value = st.session_state.user_input, placeholder="Ví dụ: Học phí của trường là bao nhiêu?")
    st.session_state.user_input = user_input

    if user_input:
        question_suggestion = select_suggestion(user_input)
        st.markdown("### Gợi ý câu hỏi:")
        for suggestion in question_suggestion:
            if st.button(f"🔍 {suggestion}"):
                st.session_state.user_input = suggestion            
                # Re-run the script to update the suggestions dynamically
    else:
        # If the user input is empty, clear the suggestions
        st.session_state.user_input = ""     
                  
        # # Sử dụng hàm extractcOne từ rapidfuzz để tìm câu hỏi gần nhất
        # result = process.extractOne(user_input, questions, score_cutoff=70)
        # if result:
        #     best_match, score = result[:2]  # Lấy giá trị tốt nhất và điểm số
        #     st.success(f"**Câu trả lời:** {answers[best_match]}")
        # else:
        #     st.warning("Xin lỗi, mình chưa tìm thấy thông tin phù hợp. Bạn thử hỏi lại nhé!")


# Tab 2: Thêm dữ liệu
with tab2:
    st.write("Bạn có thể thêm câu hỏi và câu trả lời mới vào chatbot.")
    new_question = st.text_input("Nhập câu hỏi mới:")
    new_answer = st.text_area("Nhập câu trả lời cho câu hỏi trên:")

    if st.button("Thêm vào dữ liệu"):
        if new_question and new_answer:
            # Thêm dữ liệu vào PostgreSQL
            add_to_postgresql(new_question, new_answer)
            st.success("Câu hỏi mới đã được thêm vào cơ sở dữ liệu PostgreSQL!")
        else:
            st.warning("Vui lòng nhập đầy đủ câu hỏi và câu trả lời.")
