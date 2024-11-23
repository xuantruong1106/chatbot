import streamlit as st
from user import user_interface
from admin import admin_interface
from login_or_register import login_or_register



if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_or_register()
else:
    if st.session_state['role'] == "admin":
        admin_interface()
    elif st.session_state['role'] == "user":
        user_interface()
        
    

# # Streamlit UI
# st.set_page_config(page_title="Chatbot Giải Đáp", page_icon="💬")

# st.title("Chatbot Giải Đáp Thắc Mắc 💬")

# tab1, tab2 = st.tabs(["💬 Chatbot", "🛠️ Thêm dữ liệu"])

# st.session_state.user_input = ''

# with tab1:
#     st.write("Xin chào! Mình là chatbot hỗ trợ giải đáp các thắc mắc của sinh viên VKU. Bạn có thể hỏi mình bất kỳ điều gì liên quan đến trường!")
    
#     user_input = st.text_input(
#         "Nhập câu hỏi của bạn:", 
#         value = st.session_state.user_input, 
#         placeholder ="Ví dụ: Học phí của trường là bao nhiêu?"
#     )
    
#     if user_input:
#         st.session_state.user_input = user_input 
        
#         question_suggestion = select_suggestion(st.session_state.user_input)
        
#         if question_suggestion:
        
#             st.markdown("### Gợi ý câu hỏi:")
#             for suggestion in question_suggestion:
#                 if st.button(f"🔍 {suggestion}"):
#                     if ( mactching_with_load_from_postgresql(suggestion) == True):
#                         st.success(get_answer(suggestion))
#                     elif(mactching_with_load_from_postgresql(suggestion) == False):
#                         st.success(get_answer_id_faq(suggestion))
#                     else:
#                         st.write('Rất cảm ơn, câu hỏi này sẽ được trả lời bằng email')
#         else:
#             st.session_state.user_input = user_input 
#             if ( mactching_with_load_from_postgresql(st.session_state.user_input) == True):
#                 st.success(get_answer(st.session_state.user_input))
#             else:
#                 for i in load_from_postgresql():
#                     if(compare_strings_highest_score(st.session_state.user_input,i) >= 0.75):
#                         st.success(get_answer(i))
#                         break
#                     else:
#                         st.write('Rất cảm ơn, câu hỏi này sẽ được trả lời bằng email')
                        
                    
                
#     else:
#         st.session_state.user_input = ""
                  