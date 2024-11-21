import streamlit as st
import time
import psycopg2
from googletrans import Translator
from rapidfuzz import process
from werkzeug.security import generate_password_hash, check_password_hash

# Kết nối đến PostgreSQL
def connect_to_postgresql():
    try:
        conn = psycopg2.connect(
            dbname="chatbot",
            user="postgres",
            password="andubadao123",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        st.error("Không thể kết nối tới cơ sở dữ liệu!")
        st.stop()

# Hàm kiểm tra tài khoản người dùng
def check_user(username, password):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, role FROM users WHERE username = %s", (username,))
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
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, hashed_password))
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
    cursor.execute(
        "INSERT INTO faq (question, answer) VALUES (%s, %s)", (question, answer))
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
                st.success(
                    "Tài khoản đã được tạo thành công! Bạn có thể đăng nhập.")
            else:
                st.error("Tên đăng nhập đã tồn tại. Vui lòng thử tên khác.")

# Hiệu ứng gõ chữ (typewriter effect)
def typewriter_effect(text, speed=0.01):
    response = st.empty()
    for i in range(1, len(text) + 1):
        response.markdown(text[:i])
        time.sleep(speed)


def process_user_input(user_input):
    translator = Translator()
    detected_language = translator.detect(
        user_input).lang  # Phát hiện ngôn ngữ

    if detected_language != "vi":  # Nếu không phải tiếng Việt thì dịch sang tiếng Việt
        user_input_translated = translator.translate(
            user_input, src=detected_language, dest='vi').text
    else:  # Nếu là tiếng Việt thì giữ nguyên
        user_input_translated = user_input

    return user_input_translated

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
                if message["role"] == "user":
                    # Tin nhắn của người dùng (căn bên phải với avatar)
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px;">
                            <div style="margin-right: 10px; text-align: right;">
                                <div style="background-color: #d1e7dd; padding: 10px 15px; border-radius: 15px; max-width: 100%; color: #155724;">
                                    {message['content']}
                                </div>
                            </div>
                            <img src="https://cdn1.iconfinder.com/data/icons/website-internet/48/website_-_male_user-512.png" alt="user avatar" style="border-radius: 50%; width: 40px; height: 40px;">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif message["role"] == "assistant":
                    # Tin nhắn của chatbot (căn bên trái với avatar)
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 10px;">
                            <img src="https://media.istockphoto.com/id/1957053641/vi/vec-to/nh%C3%A2n-v%E1%BA%ADt-robot-kawaii-d%E1%BB%85-th%C6%B0%C6%A1ng-tr%E1%BB%A3-l%C3%BD-bot-tr%C3%B2-chuy%E1%BB%87n-th%C3%A2n-thi%E1%BB%87n-cho-c%C3%A1c-%E1%BB%A9ng-d%E1%BB%A5ng-tr%E1%BB%B1c-tuy%E1%BA%BFn.jpg?s=1024x1024&w=is&k=20&c=a55fKkMIC4qBxb8OC47hJ2hxM0W_EYvaa4WWboo-zDk=" alt="assistant avatar" style="border-radius: 50%; width: 40px; height: 40px; margin-right: 10px;">
                            <div style="background-color: #f8d7da; padding: 10px 15px; border-radius: 15px; max-width: 70%; color: #721c24;">
                                {message['content']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )



        # Tạo form cho phần nhập liệu
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Nhập câu hỏi của bạn:",
                placeholder="Ví dụ: Học phí của trường là bao nhiêu?"
            )
            submit_button = st.form_submit_button("Gửi")

            if submit_button and user_input.strip():
                # Lưu tin nhắn của người dùng vào session_state
                st.session_state.messages.append(
                    {"role": "user", "content": user_input})

                 # Xử lý câu hỏi: kiểm tra và dịch nếu cần
                user_input_translated = process_user_input(user_input)

                # Tìm câu trả lời từ FAQ
                questions, answers = load_faq()
                result = process.extractOne(
                    user_input_translated, questions, score_cutoff=70)

                if result:
                    best_match = result[0]
                    answer = answers[best_match]
                else:
                    answer = "Xin lỗi, mình không tìm thấy câu trả lời phù hợp!"

                # Lưu tin nhắn của chatbot vào session_state
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer})

                # Áp dụng hiệu ứng gõ chữ cho câu trả lời chatbot
                typewriter_effect(answer)


# Kiểm tra trạng thái đăng nhập
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_or_register()
else:
    main_interface()
