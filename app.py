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
    
                  