import streamlit as st
from connectsql import mactching_with_load_from_postgresql, add_to_postgresql, get_answer, get_answer_id_faq, load_from_postgresql
from st_alys import compare_strings_highest_score
from rapidfuzz import process
from suggestion_file import select_suggestion


# Streamlit UI
st.set_page_config(page_title="Chatbot Giải Đáp", page_icon="💬")

st.title("Chatbot Giải Đáp Thắc Mắc 💬")

tab1, tab2 = st.tabs(["💬 Chatbot", "🛠️ Thêm dữ liệu"])

st.session_state.user_input = ''

with tab1:
    st.write("Xin chào! Mình là chatbot hỗ trợ giải đáp các thắc mắc của sinh viên VKU. Bạn có thể hỏi mình bất kỳ điều gì liên quan đến trường!")
    
    user_input = st.text_input(
        "Nhập câu hỏi của bạn:", 
        value = st.session_state.user_input, 
        placeholder ="Ví dụ: Học phí của trường là bao nhiêu?"
    )
    
    if user_input:
        st.session_state.user_input = user_input 
        
        question_suggestion = select_suggestion(st.session_state.user_input)
        
        if question_suggestion:
        
            st.markdown("### Gợi ý câu hỏi:")
            for suggestion in question_suggestion:
                if st.button(f"🔍 {suggestion}"):
                    if ( mactching_with_load_from_postgresql(suggestion) == True):
                        st.success(get_answer(suggestion))
                    elif(mactching_with_load_from_postgresql(suggestion) == False):
                        st.success(get_answer_id_faq(suggestion))
                    else:
                        st.write('Rất cảm ơn, câu hỏi này sẽ được trả lời bằng email')
        else:
            st.session_state.user_input = user_input 
            if ( mactching_with_load_from_postgresql(st.session_state.user_input) == True):
                st.success(get_answer(st.session_state.user_input))
            else:
                for i in load_from_postgresql():
                    if(compare_strings_highest_score(st.session_state.user_input,i) >= 0.75):
                        st.success(get_answer(i))
                        break
                    else:
                        st.write('Rất cảm ơn, câu hỏi này sẽ được trả lời bằng email')
                        
                    
                
    else:
        st.session_state.user_input = ""
                  
        


# Tab 2: Thêm dữ liệu
with tab2:
    st.write("Bạn có thể thêm câu hỏi và câu trả lời mới vào chatbot.")
    new_question = st.text_input("Nhập câu hỏi mới:")
    new_answer = st.text_area("Nhập câu trả lời cho câu hỏi trên:")

    if st.button("Thêm vào dữ liệu"):
        if new_question and new_answer:
            # Thêm dữ liệu vào PostgreSQL
            add_to_postgresql(new_question, new_answer)
            st.success("Câu hỏi mới đã được thêm vào cơ sở dữ liệu PostgreSQL!")
        else:
            st.warning("Vui lòng nhập đầy đủ câu hỏi và câu trả lời.")
