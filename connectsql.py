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

def get_answer(question):
    cursor.execute("select get_faq_answer(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        return answer[0], True
    else:
        return 'rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau', False

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
        return 'rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau'


def get_answer_id_faq_from_key_word(question):
    cursor.execute("select get_answer_id_faq_from_key_word(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        print(answer[0])
        return answer[0], True
    else:
        return 'rất cảm ơn câu hỏi, nhà trường sẽ giải đáp câu hỏi của bạn sau', False

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


def load_unanswered_questions():
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()
        cursor.execute("SELECT question FROM unanswered_questions")
        unanswered_questions = cursor.fetchall()
        cursor.close()
        conn.close()
        print(f"Dữ liệu tải về: {unanswered_questions}")  # Thêm dòng này
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

def save_pdf_answer_to_db(question, answer):
    try:
        with connect_to_postgresql() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO faq (question, answer) VALUES (%s, %s)",
                (question, answer)
            )
            conn.commit()
            print("Câu hỏi và câu trả lời từ PDF đã được lưu vào cơ sở dữ liệu.")
    except Exception as e:
        print(f"Lỗi khi lưu câu hỏi và câu trả lời từ PDF: {e}")
        
def log_unanswered_question(question):
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()

        # Kiểm tra xem câu hỏi đã tồn tại chưa
        cursor.execute(
            "SELECT COUNT(*) FROM unanswered_questions WHERE question = %s", (question,))
        count = cursor.fetchone()[0]

        if count == 0:  # Nếu chưa tồn tại, thêm mới
            cursor.execute(
                """
                INSERT INTO unanswered_questions (question, timestamp)
                VALUES (%s, NOW())
                """,
                (question,)
            )
            conn.commit()
            print("Câu hỏi chưa được trả lời đã được lưu.")
        else:  # Nếu đã tồn tại, bỏ qua
            print("Câu hỏi đã tồn tại. Không lưu lại.")
    except Exception as e:
        print(f"Lỗi khi lưu câu hỏi chưa được trả lời: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

          
          
            
def log_user_question(question):
    try:
        conn = connect_to_postgresql()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_questions (question, timestamp)
            VALUES (%s, NOW())
            """,
            (question,)
        )
        conn.commit()
        print("Câu hỏi của người dùng đã được lưu.")
    except Exception as e:
        print(f"Lỗi khi lưu câu hỏi của người dùng: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def show_statistics():
    try:
        conn = connect_to_postgresql()
        query = """
            SELECT question, COUNT(*) as count
            FROM user_questions
            GROUP BY question
            ORDER BY count DESC;
        """
        stats_df = pd.read_sql_query(query, conn)
        conn.close()

        st.subheader("📊 Thống kê câu hỏi")

        fig = px.bar(stats_df, x='question', y='count', title="Top những câu hỏi")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Lỗi khi tải thống kê: {e}")




