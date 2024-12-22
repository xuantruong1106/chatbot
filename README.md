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
2. Cài đặt các thư viện cần thiết bằng cách sử dụng pip:
   ```bash
   pip install -r requirements.txt
Đảm bảo bạn đã cài đặt và cấu hình PostgreSQL. Tạo cơ sở dữ liệu cần thiết và chạy các câu lệnh SQL để thiết lập bảng.
Chạy ứng dụng

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
