# Kết nối đến PostgreSQL
import streamlit as st
import pandas as pd
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.express as px


def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="chatbotVKU",
        user="postgres",
        password="123456789",
        host="localhost",
        port="5432"
    )
    return conn

conn = connect_to_postgresql()
cursor = conn.cursor()


def load_from_postgresql():
    cursor.execute("SELECT question FROM faq")
    rows = cursor.fetchall()
    questions = [row[0] for row in rows]
    return questions


def mactching_with_load_from_postgresql(ques):
    questions = load_from_postgresql()
    for i in questions:
        if (i == ques):
            return True
            break
    return False


def get_answer(question):
    cursor.execute("select get_faq_answer(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        return answer[0], True
    else:
        return 'get_answer rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau', False

# Thêm câu hỏi và câu trả lời vào PostgreSQL


def add_to_postgresql(question, answer):
    cursor.execute("call insert_faq_procedure(%s, %s)", (question, answer))
    conn.commit()
    cursor.close()
    conn.close()


def get_answer_id_faq(question):
    cursor.execute("select get_id_faq(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        return answer[0]
    else:
        return 'get_answer_id_faq rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau'


def get_answer_id_faq_from_key_word(question):
    cursor.execute("select get_answer_id_faq_from_key_word(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        print(answer[0])
        return answer[0], True
    else:
        return 'get_answer_id_faq_from_key_word rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau', False

# -----------------------------------nhan------------------------------------------------


def check_user(username, password):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, role FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user[0], password):
        return user[1]
    return None


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
        return False
    finally:
        cursor.close()
        conn.close()
    return True


def load_faq():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM faq")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    questions = [row[0] for row in rows]
    answers = {row[0]: row[1] for row in rows}
    return questions, answers


def add_faq(question, answer):
    if is_question_duplicate(question):
        print("Câu hỏi đã tồn tại!")
    else:
        try:
            conn = connect_to_postgresql()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO faq (question, answer) VALUES (%s, %s)",
                (question, answer)
            )

            conn.commit()
            cursor.close()
            conn.close()

            print("Dữ liệu đã được thêm thành công!")
            return True
        except Exception as e:
            print(f"Lỗi khi thêm câu hỏi: {e}")
            return False


def update_faq(old_question, new_question, new_answer):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("UPDATE faq SET question = %s, answer = %s WHERE question = %s",
                   (new_question, new_answer, old_question))
    conn.commit()
    cursor.close()
    conn.close()


def delete_faq(question):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faq WHERE question = %s", (question,))
    conn.commit()
    cursor.close()
    conn.close()

# Ghi log vào cơ sở dữ liệu


def load_unanswered_logs():
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, question, timestamp FROM logs WHERE is_answered = FALSE ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs


def log_chat(username, question, answer, is_answered):
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()

        if is_answered:
            cursor.execute(
                """
                INSERT INTO logs (username, question, answer, is_answered, timestamp) 
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (username, question, answer, is_answered)
            )
        else:
            cursor.execute(
                """
                INSERT INTO unanswered_questions (question, time) 
                VALUES (%s, NOW())
                """,
                (question,)
            )

        conn.commit()
    except Exception as e:
        print(f"Lỗi khi lưu log: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Lấy dữ liệu log từ database


def fetch_logs_data():
    conn = connect_to_postgresql()
    query = """
        SELECT question, is_answered, COUNT(*) as count
        FROM logs
        GROUP BY question, is_answered
        ORDER BY count DESC;
    """
    logs_df = pd.read_sql_query(query, conn)
    conn.close()
    return logs_df

# Hiển thị thống kê bằng biểu đồ


def display_statistics():
    st.title("Thống kê Chatbot")

    logs_data = fetch_logs_data()

    # Số lượng câu hỏi đã trả lời và chưa trả lời
    answered_data = logs_data.groupby('is_answered').sum().reset_index()
    answered_data['status'] = answered_data['is_answered'].replace(
        {True: "Đã trả lời", False: "Chưa trả lời"})

    # Biểu đồ tròn
    pie_chart = px.pie(
        answered_data,
        values='count',
        names='status',
        title='Tỷ lệ câu hỏi đã trả lời',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(pie_chart)

    # Biểu đồ cột: Câu hỏi được hỏi nhiều nhất
    top_questions = logs_data.sort_values(by='count', ascending=False).head(10)
    bar_chart = px.bar(
        top_questions,
        x='question',
        y='count',
        color='is_answered',
        labels={'is_answered': 'Trạng thái'},
        title='Top 10 câu hỏi được hỏi nhiều nhất',
        color_discrete_map={True: 'green', False: 'red'}
    )
    st.plotly_chart(bar_chart)


def load_unanswered_questions():
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question, time FROM unanswered_questions ORDER BY time DESC")
        unanswered_questions = cursor.fetchall()
        cursor.close()
        conn.close()
        return unanswered_questions
    except Exception as e:
        print(f"Lỗi khi tải câu hỏi chưa trả lời: {e}")
        return []


def update_answer_for_unanswered(question, answer):
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO faq (question, answer)
            VALUES (%s, %s)
        """, (question, answer))

        cursor.execute("""
            DELETE FROM unanswered_questions 
            WHERE question = %s
        """, (question,))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Lỗi khi cập nhật câu trả lời cho câu hỏi chưa trả lời: {e}")
