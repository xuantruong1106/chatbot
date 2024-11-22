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

conn = connect_to_postgresql()
cursor = conn.cursor()

# Đọc dữ liệu từ PostgreSQL
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
        else:
            return False

def get_answer(question):
    cursor.execute("select get_faq_answer(%s)", (question,))
    answer = cursor.fetchone()
    if answer:
        return answer[0]
    else:
        return 'get_answer dont answer'

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
        return 'get_answer_id_faq dont answer'
# print (get_answer_id_faq('học phí 1 tín chỉ bao nhiêu'))