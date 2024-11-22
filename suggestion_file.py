from connectsql import connect_to_postgresql

conn = connect_to_postgresql()
    
def select_suggestion(str1):
    cursor = conn.cursor()
    cursor.execute("select suggestion(%s) limit 5", (str1,))
    rows = cursor.fetchall()
    questions = [row[0] for row in rows]
    return questions

    