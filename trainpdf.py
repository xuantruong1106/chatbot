import pdfplumber
import re
import streamlit as st
from transformers import pipeline

# Hàm dịch câu hỏi sang tiếng Việt theo lô
def translate_to_vietnamese_batch(questions):
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-vi")
    translated = translator(questions, max_length=256, batch_size=8)
    return [output["translation_text"] for output in translated]

# Hàm trích xuất văn bản từ file PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.strip()

# Hàm tách câu văn bản
def split_sentences(text):
    return [sentence.strip() for sentence in re.split(r'(?<=[.!?])\s+', text) if sentence.strip()]

# Hàm sinh câu hỏi từ mô hình
def generate_questions(text):
    # Mô hình sinh câu hỏi
    question_generator = pipeline("text2text-generation", model="google/flan-t5-base")
    questions_en = []

    sentences = split_sentences(text)
    for sentence in sentences:
        if sentence:  # Kiểm tra câu không rỗng
            prompt = f"Generate a question from this sentence: {sentence}"
            try:
                # Sinh câu hỏi bằng tiếng Anh
                outputs = question_generator(prompt, max_new_tokens=64, num_return_sequences=1, do_sample=False)
                if outputs and isinstance(outputs, list) and len(outputs) > 0:
                    question_text_en = outputs[0].get("generated_text", "").strip()
                    if question_text_en:  # Chỉ thêm câu hỏi hợp lệ
                        questions_en.append({"question": question_text_en, "answer": sentence})
            except Exception as e:
                st.warning(f"Lỗi sinh câu hỏi cho câu: '{sentence}'. Chi tiết: {e}")

    # Kiểm tra nếu có câu hỏi nào được sinh ra
    if questions_en:
        try:
            # Lấy danh sách câu hỏi tiếng Anh
            questions_texts = [q["question"] for q in questions_en]

            # Dịch sang tiếng Việt theo lô
            questions_texts_vi = translate_to_vietnamese_batch(questions_texts)

            # Kiểm tra số lượng câu hỏi đã dịch có khớp với số lượng ban đầu
            if len(questions_texts_vi) == len(questions_en):
                # Tạo danh sách câu hỏi - câu trả lời
                questions_and_answers = [
                    {"question": vi, "answer": q["answer"]}
                    for vi, q in zip(questions_texts_vi, questions_en)
                ]
            else:
                st.error("Số lượng câu hỏi đã dịch không khớp với câu hỏi gốc.")
                questions_and_answers = []
        except Exception as e:
            st.error(f"Lỗi trong quá trình dịch câu hỏi: {e}")
            questions_and_answers = []
    else:
        st.warning("Không thể sinh bất kỳ câu hỏi nào từ nội dung PDF.")
        questions_and_answers = []

    return questions_and_answers