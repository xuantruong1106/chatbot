CREATE TABLE faq (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);

INSERT INTO faq (id, question, answer) VALUES (1, 'học phí 1 tín chỉ của ngành công nghệ thông tin bao nhiêu?','473,000đ / 1 tín chỉ')


--Thử nghiệm
CREATE TABLE faq_test (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

ALTER TABLE faq_test ADD COLUMN category_id INT REFERENCES categories(id);


--Dữ liệu mẫu
INSERT INTO categories (name) VALUES
('Thông tin chung'),
('Tuyển sinh'),
('Học phí'),
('Học bổng'),
('Cơ sở vật chất'),
('Hoạt động ngoại khóa'),
('Hợp tác quốc tế'),
('Thực tập và việc làm'),
('Đào tạo');


INSERT INTO faq_test (question, answer, category_id) VALUES
('Trường VKU có địa chỉ ở đâu?', 'Trường VKU nằm tại số 470 Trần Đại Nghĩa, Ngũ Hành Sơn, Đà Nẵng.', 1),
('Các ngành đào tạo của VKU là gì?', 'Trường đào tạo các ngành liên quan đến Công nghệ Thông tin, Khoa học Dữ liệu, Trí tuệ Nhân tạo, và Kinh doanh Số.', 1),
('Làm thế nào để nộp hồ sơ vào VKU?', 'Bạn có thể nộp hồ sơ trực tiếp tại trường hoặc qua hệ thống tuyển sinh trực tuyến.', 2),
('Học phí trung bình của VKU là bao nhiêu?', 'Học phí trung bình từ 16 - 20 triệu đồng mỗi học kỳ, tùy theo ngành học.', 3),
('Trường VKU có học bổng không?', 'VKU cung cấp nhiều chương trình học bổng dành cho sinh viên giỏi, sinh viên có hoàn cảnh khó khăn, và học bổng doanh nghiệp.', 4),
('Ký túc xá của VKU có sức chứa bao nhiêu?', 'Ký túc xá có sức chứa khoảng 2000 sinh viên với đầy đủ tiện nghi.', 5),
('Trường có các câu lạc bộ nào?', 'VKU có các câu lạc bộ như CLB Công nghệ, CLB Văn nghệ, CLB Thể thao, và CLB Học thuật.', 6),
('VKU có hợp tác với những doanh nghiệp nào?', 'VKU hợp tác với các doanh nghiệp lớn như FPT Software, Axon Active, và VNPT.', 7),
('Sinh viên VKU có được hỗ trợ tìm kiếm việc làm không?', 'Trường có trung tâm hỗ trợ thực tập và việc làm giúp kết nối sinh viên với các nhà tuyển dụng.', 8),
('Chương trình đào tạo của VKU kéo dài bao lâu?', 'Chương trình đào tạo đại học tại VKU thường kéo dài 4 năm.', 9);


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(10) NOT NULL
);

INSERT INTO users (username, password, role) 
VALUES ('admin', 'scrypt:32768:8:1$LgwDzlq04rqHNo7d$5ce454bfee85cc8489979d3d66a37e86735f8d74088bd84de76d0db7e4bbc953a883d8dd838c24171a1b8c56ecc9a699fc322645bdba62e2a4520226b0ed3127', 'admin');


CREATE TABLE unanswered_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
