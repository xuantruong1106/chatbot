import streamlit as st
import psycopg2
from rapidfuzz import process

# Kết nối đến PostgreSQL
def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="chatbot",
        user="postgres",  
        password="12345",
        host="localhost",        
        port="5432"             
    )
    return conn

# Đọc dữ liệu từ PostgreSQL
def load_from_postgresql():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM faq")
    rows = cursor.fetchall()
    questions = [row[0] for row in rows]
    answers = {row[0]: row[1] for row in rows}
    cursor.close()
    conn.close()
    return questions, answers

# Thêm câu hỏi và câu trả lời vào PostgreSQL
def add_to_postgresql(question, answer):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq (question, answer) VALUES (%s, %s)", (question, answer))
    conn.commit()
    cursor.close()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Chatbot Giải Đáp", page_icon="💬")

st.title("Chatbot Giải Đáp Thắc Mắc 💬")

tab1, tab2 = st.tabs(["💬 Chatbot", "🛠️ Thêm dữ liệu"])

# Load dữ liệu từ PostgreSQL
questions, answers = load_from_postgresql()

# Tab 1: Chatbot
with tab1:
    st.write("Xin chào! Mình là chatbot hỗ trợ giải đáp các thắc mắc của sinh viên VKU. Bạn có thể hỏi mình bất kỳ điều gì liên quan đến trường!")
    user_input = st.text_input("Nhập câu hỏi của bạn:", placeholder="Ví dụ: Học phí của trường là bao nhiêu?")

    if user_input:
        # Sử dụng hàm extractOne từ rapidfuzz để tìm câu hỏi gần nhất
        result = process.extractOne(user_input, questions, score_cutoff=70)
        if result:
            best_match, score = result[:2]  # Lấy giá trị tốt nhất và điểm số
            st.success(f"**Câu trả lời:** {answers[best_match]}")
        else:
            st.warning("Xin lỗi, mình chưa tìm thấy thông tin phù hợp. Bạn thử hỏi lại nhé!")


# Tab 2: Thêm dữ liệu
with tab2:
    st.write("Bạn có thể thêm câu hỏi và câu trả lời mới vào chatbot.")
    new_question = st.text_input("Nhập câu hỏi mới:")
    new_answer = st.text_area("Nhập câu trả lời cho câu hỏi trên:")

    if st.button("Thêm vào dữ liệu"):
        if new_question and new_answer:
            # Thêm dữ liệu vào PostgreSQL
            add_to_postgresql(new_question, new_answer)
            # Cập nhật lại dữ liệu trên UI
            questions.append(new_question)
            answers[new_question] = new_answer
            st.success("Câu hỏi mới đã được thêm vào cơ sở dữ liệu PostgreSQL!")
        else:
            st.warning("Vui lòng nhập đầy đủ câu hỏi và câu trả lời.")
