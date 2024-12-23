# Chatbot Giải Đáp Thắc Mắc

## Giới thiệu
Chatbot Giải Đáp Thắc Mắc là một ứng dụng web được xây dựng bằng Python và Streamlit, cho phép người dùng nhập câu hỏi và nhận câu trả lời từ cơ sở dữ liệu hoặc từ các tài liệu PDF. Ứng dụng cũng hỗ trợ quản lý dữ liệu cho admin, bao gồm thêm, chỉnh sửa và xóa câu hỏi và câu trả lời.

## Công nghệ sử dụng
- **Python**: Ngôn ngữ lập trình chính.
- **Streamlit**: Thư viện để xây dựng giao diện web.
- **RapidFuzz**: Thư viện để xử lý tương đồng chuỗi.
- **PyMuPDF**: Thư viện để đọc nội dung từ file PDF.
- **Scikit-learn**: Thư viện cho việc tính toán độ tương đồng văn bản.
- **Deep Translator**: Thư viện dịch ngôn ngữ.
- **PostgreSQL**: Cơ sở dữ liệu để lưu trữ câu hỏi và câu trả lời.

## Cài đặt
1. Clone hoặc tải xuống dự án.
   ```bash
   git clone <repository-url>
   cd chatbot

2. Tạo và kích hoạt môi trường ảo: https://drive.google.com/file/d/1wm1JsmXrXTy9rd6qMv-Xu9N6h_ZPdw__/view?usp=sharing

3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt

<<<<<<< HEAD
4. Đảm bảo bạn đã cài đặt và cấu hình PostgreSQL. Tạo cơ sở dữ liệu cần thiết và cập nhật thông tin kết nối trong file connectsql.py.

## Sử dụng
1. Chạy ứng dụng:
   ```bash
   streamlit run app.py

2. Mở trình duyệt và truy cập vào địa chỉ được cung cấp (thường là http://localhost:8501).

### Chức năng
### Người dùng
 - Đăng nhập/Đăng ký: Người dùng có thể đăng nhập hoặc đăng ký tài khoản mới.
 - Chatbot: Người dùng có thể nhập câu hỏi và nhận câu trả lời từ cơ sở dữ liệu hoặc từ các tài liệu PDF.
### Admin
 - Quản lý Dữ liệu: Admin có thể thêm, chỉnh sửa và xóa câu hỏi và câu trả lời.
 - Quản lý Log: Admin có thể xem và trả lời các câu hỏi chưa được trả lời.
### Cấu trúc dự án
 - app.py: Điểm vào chính của ứng dụng.
 - user.py: Giao diện và logic cho người dùng.
 - admin.py: Giao diện và logic cho admin.
 - login_or_register.py: Giao diện và logic cho đăng nhập và đăng ký.
 - connectsql.py: Kết nối và thao tác với cơ sở dữ liệu PostgreSQL.
 - requirements.txt: Danh sách các thư viện cần thiết.
=======
Để chạy ứng dụng, sử dụng lệnh sau:
   ```bash
   streamlit run user.py
   ```
Giao diện người dùng sẽ mở ra trong trình duyệt mặc định của bạn.

Sử dụng
Người dùng: Nhập câu hỏi vào ô nhập liệu và nhấn "Gửi". Ứng dụng sẽ tìm kiếm câu trả lời trong cơ sở dữ liệu hoặc trong các file PDF đã tải lên.
Quản trị viên: Truy cập vào giao diện quản lý để thêm, chỉnh sửa hoặc xóa câu hỏi và câu trả lời. Quản trị viên cũng có thể quản lý các câu hỏi chưa được trả lời.
Ghi chú
Đảm bảo rằng thư mục docs chứa các file PDF cần thiết để chatbot có thể tham khảo.
Cấu hình kết nối cơ sở dữ liệu trong tệp connectsql.py nếu cần thiết.

Môi trường ảo : https://drive.google.com/file/d/1wm1JsmXrXTy9rd6qMv-Xu9N6h_ZPdw__/view?usp=sharing
>>>>>>> aea9c3b78f89db3cc97202b68d9f9baeaa3d4954
