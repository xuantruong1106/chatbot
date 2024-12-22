import streamlit as st
from connectsql import check_user, create_user

# Hàm tạo giao diện Đăng nhập hoặc Đăng ký
def login_or_register():
    st.title("🔒 **Hệ thống Đăng nhập & Đăng ký**")
    st.write("Chào mừng bạn! Vui lòng chọn hành động bên dưới:")
    
    menu = st.radio(
        "Lựa chọn:",
        ["Đăng nhập", "Đăng ký"],
        horizontal=True
    )

    st.divider()  # Dòng phân cách

    if menu == "Đăng nhập":
        st.subheader("🔑 **Đăng nhập**")
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập...")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            submit_login = st.form_submit_button("Đăng nhập")
        
        if submit_login:
            role = check_user(username, password)
            if role:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
                st.success(f"🎉 Xin chào, {username}! Bạn đã đăng nhập thành công với quyền {role}.")
            else:
                st.error("⚠️ Tên đăng nhập hoặc mật khẩu không chính xác! Vui lòng thử lại.")

    elif menu == "Đăng ký":
        st.subheader("📝 **Đăng ký tài khoản mới**")
        with st.form("register_form"):
            username = st.text_input("Tên đăng nhập mới", placeholder="Nhập tên đăng nhập mới...")
            password = st.text_input("Mật khẩu mới", type="password", placeholder="Nhập mật khẩu mới...")
            submit_register = st.form_submit_button("Đăng ký")
        
        if submit_register:
            if create_user(username, password):
                st.success(f"✅ Tài khoản **{username}** đã được tạo thành công! Vui lòng đăng nhập.")
            else:
                st.error("⚠️ Tên đăng nhập đã tồn tại. Vui lòng thử tên khác.")
    
    # Ghi chú cuối giao diện
    st.divider()
    st.caption("💡 Nếu bạn gặp vấn đề khi đăng nhập, hãy liên hệ với bộ phận hỗ trợ.")
