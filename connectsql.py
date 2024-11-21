# Kết nối đến PostgreSQL

import psycopg2

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
    cursor.execute("call insert_faq_procedure(%s, %s)", (question, answer))
    conn.commit()
    cursor.close()
    conn.close()