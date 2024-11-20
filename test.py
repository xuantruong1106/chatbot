import streamlit as st
import time
import psycopg2
from rapidfuzz import process
from werkzeug.security import generate_password_hash, check_password_hash

# Kết nối đến PostgreSQL
def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="chatbot",
        user="postgres",
        password="123456789",
        host="127.0.0.1",
        port="5432"
    )
    return conn

# Hàm kiểm tra tài khoản người dùng
def check_user(username, password):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user[0], password):
        return user[1]  # Trả về vai trò (admin/user)
    return None

# Hàm tạo tài khoản
def create_user(username, password):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, hashed_password))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False  # Tên tài khoản đã tồn tại
    finally:
        cursor.close()
        conn.close()
    return True

# Đọc dữ liệu FAQ từ PostgreSQL
def load_faq():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM faq")
    rows = cursor.fetchall()
    questions = [row[0] for row in rows]
    answers = {row[0]: row[1] for row in rows}
    cursor.close()
    conn.close()
    return questions, answers

# Thêm dữ liệu FAQ vào PostgreSQL
def add_faq(question, answer):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq (question, answer) VALUES (%s, %s)", (question, answer))
    conn.commit()
    cursor.close()
    conn.close()

# Giao diện đăng nhập và đăng ký
def login_or_register():
    st.title("Đăng nhập hoặc Đăng ký")
    menu = st.radio("Chọn hành động", ["Đăng nhập", "Đăng ký"])

    if menu == "Đăng nhập":
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            role = check_user(username, password)
            if role:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
            else:
                st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

    elif menu == "Đăng ký":
        username = st.text_input("Tên đăng nhập mới")
        password = st.text_input("Mật khẩu mới", type="password")
        if st.button("Đăng ký"):
            if create_user(username, password):
                st.success("Tài khoản đã được tạo thành công! Bạn có thể đăng nhập.")
            else:
                st.error("Tên đăng nhập đã tồn tại. Vui lòng thử tên khác.")

# Hiệu ứng gõ chữ (typewriter effect)
def typewriter_effect(text, speed=0.01):
    response = st.empty()  # Để tạo vị trí trống cho phần trả lời
    for i in range(1, len(text) + 1):
        response.markdown(text[:i])
        time.sleep(speed)

# Giao diện chính sau khi đăng nhập
def main_interface():
    st.sidebar.title("Thông tin người dùng")
    st.sidebar.write(f"Xin chào, {st.session_state['username']}!")

    if st.session_state['role'] == "admin":
        st.title("Quản lý Dữ liệu Chatbot")
        question = st.text_input("Thêm câu hỏi:")
        answer = st.text_area("Thêm câu trả lời:")
        if st.button("Thêm dữ liệu"):
            if question and answer:
                add_faq(question, answer)
                st.success("Dữ liệu đã được thêm thành công!")
            else:
                st.warning("Vui lòng nhập đầy đủ thông tin.")

    elif st.session_state['role'] == "user":
        st.title("Chatbot Giải Đáp Thắc Mắc")

        # Hiển thị các tin nhắn chat trước đó
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Phần hiển thị các tin nhắn
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Tạo form cho phần nhập liệu
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Nhập câu hỏi của bạn:",
                placeholder="Ví dụ: Học phí của trường là bao nhiêu?"
            )
            submit_button = st.form_submit_button("Gửi")

            if submit_button and user_input.strip():
                # Lưu tin nhắn của người dùng vào session_state
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Tìm câu trả lời từ FAQ
                questions, answers = load_faq()
                result = process.extractOne(user_input, questions, score_cutoff=70)

                if result:
                    best_match = result[0]
                    answer = answers[best_match]
                else:
                    answer = "Xin lỗi, mình không tìm thấy câu trả lời phù hợp!"

                # Lưu tin nhắn của chatbot vào session_state
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Áp dụng hiệu ứng gõ chữ cho câu trả lời chatbot
                typewriter_effect(answer)

        # Tạo phần cuộn cho chat, luôn luôn cố định thanh nhập câu hỏi ở dưới
        st.markdown("""
            <style>
                /* Cố định phần thanh nhập câu hỏi ở dưới */
                .css-1v3fvcr {
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                    padding: 10px;
                    background-color: white;
                    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
                    z-index: 1000;
                }

                /* Tạo phần cuộn cho phần chat */
                .css-1o5pa15 {
                    padding-bottom: 80px; /* Đảm bảo có không gian cho phần thanh nhập ở dưới */
                    max-height: 70vh;
                    overflow-y: auto;
                }
            </style>
        """, unsafe_allow_html=True)

# Kiểm tra trạng thái đăng nhập
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_or_register()
else:
    main_interface()