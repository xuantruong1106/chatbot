import streamlit as st
from database import check_user, create_user
from users import user_interface
from admin import admin_interface

def login_or_register():
    st.title("Đăng nhập hoặc Đăng ký")
    menu = st.radio("Chọn hành động", ["Đăng nhập", "Đăng ký"])

    if menu == "Đăng nhập":
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            role = check_user(username, password)
            if role:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
            else:
                st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

    elif menu == "Đăng ký":
        username = st.text_input("Tên đăng nhập mới")
        password = st.text_input("Mật khẩu mới", type="password")
        if st.button("Đăng ký"):
            if create_user(username, password):
                st.success("Tài khoản đã được tạo thành công! Bạn có thể đăng nhập.")
            else:
                st.error("Tên đăng nhập đã tồn tại. Vui lòng thử tên khác.")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_or_register()
else:
    if st.session_state['role'] == "admin":
        admin_interface()
    elif st.session_state['role'] == "user":
        user_interface()
