from connectsql import connect_to_postgresql

conn = connect_to_postgresql()
    
def select_suggestion(str1):
    cursor = conn.cursor()
    cursor.execute("select * from suggestion(%s)", (str1,))
    rows = cursor.fetchall()
    questions = [row[0] for row in rows]
    # cursor.close()
    # conn.close()
    return questions

    