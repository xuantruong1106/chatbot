from transformers import pipeline

# Khởi tạo pipeline để tạo câu hỏi


def generate_questions_with_hf(chunk):
    try:
        # Sử dụng mô hình "google/flan-t5-large" để tạo câu hỏi
        question_generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
            tokenizer="google/flan-t5-large"
        )

        # Prompt để sinh câu hỏi
        prompt = f"Đoạn văn: {chunk}\nTạo 5 câu hỏi và câu trả lời liên quan:"
        result = question_generator(
            prompt, max_length=256, num_return_sequences=5)

        question_answer_pairs = []
        for r in result:
            text = r['generated_text']
            if "Câu hỏi:" in text and "Trả lời:" in text:
                pairs = text.split("Câu hỏi:")
                for pair in pairs[1:]:
                    question, answer = pair.split("Trả lời:")
                    question_answer_pairs.append(
                        (question.strip(), answer.strip()))
        return question_answer_pairs
    except Exception as e:
        print(f"Lỗi khi sử dụng Hugging Face model: {e}")
        return []


# Tích hợp vào tab_generate_question
with tab_generate_question:
    st.subheader("Tự động sinh câu hỏi từ tài liệu PDF (Hugging Face)")

    # List available PDFs
    docs = [file.name for file in docs_path.iterdir() if file.suffix == ".pdf"]
    selected_doc = st.selectbox("Chọn tài liệu:", docs)

    if st.button("Sinh câu hỏi với Hugging Face"):
        pdf_path = docs_path / selected_doc
        pdf_text = get_pdf_text(pdf_path)  # Extract text from PDF

        if pdf_text.strip():
            # Chunk the text
            chunks = split_text_into_chunks(pdf_text)

            for chunk in chunks:
                question_answer_pairs = generate_questions_with_hf(chunk)
                if question_answer_pairs:
                    for question, answer in question_answer_pairs:
                        st.write(f"**Câu hỏi:** {question}")
                        st.write(f"**Câu trả lời:** {answer}")
                        save_question_button = st.button(
                            f"Lưu câu hỏi: {question}")
                        if save_question_button:
                            add_faq(question, answer)
                            st.success("Câu hỏi và câu trả lời đã được lưu!")
                else:
                    st.warning("Không thể sinh câu hỏi từ đoạn văn này.")
        else:
            st.error(
                "Không thể đọc nội dung từ file PDF. Vui lòng kiểm tra lại file.")
