import streamlit as st
import psycopg2
from rapidfuzz import process

# Kết nối đến PostgreSQL


def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="chatbot",
        user="postgres",
        password="andubadao123",
        host="localhost",
        port="5432"
    )
    return conn

# Đọc dữ liệu từ PostgreSQL


def load_from_postgresql():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer, category_id FROM faq_test")
    rows = cursor.fetchall()
    questions = [row[1] for row in rows]
    answers = {row[1]: row[2] for row in rows}
    category_ids = {row[1]: row[3] for row in rows}
    cursor.close()
    conn.close()
    return questions, answers, category_ids

# Cập nhật danh mục từ PostgreSQL


def load_categories():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

# Thêm câu hỏi và câu trả lời vào PostgreSQL


def add_to_postgresql(question, answer, category_id):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq_test (question, answer, category_id) VALUES (%s, %s, %s)",
                   (question, answer, category_id))
    conn.commit()
    cursor.close()
    conn.close()

# Cập nhật câu hỏi trong cơ sở dữ liệu


def update_question_in_db(question_id, new_question, new_answer, new_category_id):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("""UPDATE faq_test
                      SET question = %s, answer = %s, category_id = %s
                      WHERE id = %s""",
                   (new_question, new_answer, new_category_id, question_id))
    conn.commit()
    cursor.close()
    conn.close()

# Xóa câu hỏi khỏi cơ sở dữ liệu


def delete_question_from_db(question_id):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faq_test WHERE id = %s", (question_id,))
    conn.commit()
    cursor.close()
    conn.close()


# Streamlit UI
st.set_page_config(page_title="Chatbot Giải Đáp", page_icon="💬")

st.title("Chatbot Giải Đáp Thắc Mắc 💬")

tab1, tab2 = st.tabs(["💬 Chatbot", "🛠️ Thêm dữ liệu"])

# Load dữ liệu từ PostgreSQL
questions, answers, category_ids = load_from_postgresql()

# Load categories
categories = load_categories()
category_names = [category[1] for category in categories]

# Lưu lịch sử câu hỏi và câu trả lời
history = []

# Tab 1: Chatbot
with tab1:
    st.write("Xin chào! Mình là chatbot hỗ trợ giải đáp các thắc mắc của sinh viên VKU. Bạn có thể hỏi mình bất kỳ điều gì liên quan đến trường!")

    # Thêm selectbox để lọc câu hỏi theo danh mục
    selected_category = st.selectbox("Chọn danh mục câu hỏi:", category_names)

    # Lọc câu hỏi theo danh mục
    filtered_questions = [q for q, cid in category_ids.items(
    ) if category_names[cid-1] == selected_category]

    user_input = st.text_input(
        "Nhập câu hỏi của bạn:", placeholder="Ví dụ: Vị trí của trường VKU ở đâu?")

    if user_input:
        # Sử dụng hàm extractOne từ rapidfuzz để tìm câu hỏi gần nhất
        result = process.extractOne(
            user_input, filtered_questions, score_cutoff=70)

        if result:
            best_match, score = result[:2]
            st.success(f"**Câu trả lời:** {answers[best_match]}")
            # Lưu lịch sử câu hỏi và câu trả lời
            history.append(
                {"question": user_input, "answer": answers[best_match]})
        else:
            st.warning(
                "Xin lỗi, mình chưa tìm thấy thông tin phù hợp. Bạn thử hỏi lại nhé!")

    # Hiển thị lịch sử câu hỏi và câu trả lời
    st.write("Lịch sử câu hỏi và câu trả lời:")
    for item in history:
        st.write(f"**Câu hỏi**: {item['question']}")
        st.write(f"**Câu trả lời**: {item['answer']}")

    # Chức năng đánh giá phản hồi
    if len(history) > 0:
        st.write("Bạn có thấy câu trả lời này hữu ích?")
        feedback = st.radio("Chọn một đánh giá:", ("Hữu ích", "Không hữu ích"))
        if feedback == "Hữu ích":
            st.success("Cảm ơn bạn đã đánh giá tích cực!")
        else:
            st.warning("Cảm ơn bạn đã đánh giá. Chúng tôi sẽ cải thiện hơn!")

# Tab 2: Thêm dữ liệu
with tab2:
    st.write("Bạn có thể thêm câu hỏi và câu trả lời mới vào chatbot.")
    category_id = st.selectbox("Chọn chủ đề cho câu hỏi:", category_names)
    new_question = st.text_input("Nhập câu hỏi mới:")
    new_answer = st.text_area("Nhập câu trả lời cho câu hỏi trên:")

    if st.button("Thêm vào dữ liệu"):
        if new_question and new_answer:
            # Lấy id của category đã chọn
            selected_category_id = next(
                category[0] for category in categories if category[1] == category_id)
            # Thêm câu hỏi và câu trả lời vào cơ sở dữ liệu
            add_to_postgresql(new_question, new_answer, selected_category_id)
            # Cập nhật lại dữ liệu trên UI
            questions.append(new_question)
            answers[new_question] = new_answer
            category_ids[new_question] = selected_category_id
            st.success("Câu hỏi mới đã được thêm vào cơ sở dữ liệu PostgreSQL!")
        else:
            st.warning("Vui lòng nhập đầy đủ câu hỏi và câu trả lời.")

    # Chỉnh sửa câu hỏi
    st.write("Chỉnh sửa câu hỏi trong cơ sở dữ liệu.")
    selected_question = st.selectbox("Chọn câu hỏi cần chỉnh sửa:", questions)

    if selected_question:
        selected_question_id = list(
            answers.keys()).index(selected_question) + 1
        current_answer = answers[selected_question]
        current_category = category_ids[selected_question]
        category_name = next(cat[1]
                             for cat in categories if cat[0] == current_category)

        new_question = st.text_input("Câu hỏi mới:", value=selected_question)
        new_answer = st.text_area("Câu trả lời mới:", value=current_answer)
        new_category = st.selectbox(
            "Chọn chủ đề mới:", category_names, index=category_names.index(category_name))

        if st.button("Cập nhật câu hỏi"):
            new_category_id = next(
                category[0] for category in categories if category[1] == new_category)
            update_question_in_db(selected_question_id,
                                  new_question, new_answer, new_category_id)
            st.success("Câu hỏi đã được cập nhật!")

    # Xóa câu hỏi
    st.write("Xóa câu hỏi khỏi cơ sở dữ liệu.")
    selected_question_for_delete = st.selectbox(
        "Chọn câu hỏi để xóa:", questions)

    if selected_question_for_delete:
        selected_question_id = list(answers.keys()).index(
            selected_question_for_delete) + 1

        if st.button("Xóa câu hỏi"):
            delete_question_from_db(selected_question_id)
            st.success("Câu hỏi đã được xóa khỏi cơ sở dữ liệu!")
