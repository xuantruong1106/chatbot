from werkzeug.security import generate_password_hash

# Thay "admin_password" bằng mật khẩu bạn muốn sử dụng
hashed_password = generate_password_hash("123456")
print(hashed_password)
