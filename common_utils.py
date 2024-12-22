import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import hashlib

# Load spaCy model for sentence splitting
nlp = spacy.load("en_core_web_sm")

# Load Transformers pipelines
question_generator = pipeline(
    "text2text-generation", model="google/flan-t5-base")
answer_generator = pipeline(
    "question-answering", model="deepset/roberta-base-squad2")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 1: Split text into chunks while preserving sentence boundaries


def split_text_with_sentences(text, chunk_size=512):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) < chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Step 2: Generate questions from text chunks


def generate_questions_from_chunks(chunks):
    questions = []
    for chunk in chunks:
        generated = question_generator(
            chunk, max_length=128, num_return_sequences=5, num_beams=5, early_stopping=True
        )
        for item in generated:
            questions.append(item['generated_text'])
    return questions

# Step 3: Filter duplicate questions using Sentence-BERT


def filter_duplicate_questions(questions, threshold=0.85):
    embeddings = embedding_model.encode(questions, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

    filtered_questions = []
    for i, question in enumerate(questions):
        if all(cosine_scores[i][j] < threshold for j in range(len(filtered_questions))):
            filtered_questions.append(question)
    return filtered_questions

# Step 4: Generate answers for each question


def generate_answers(questions, chunks):
    qa_pairs = []
    for question in questions:
        for chunk in chunks:
            result = answer_generator(
                question=question, context=chunk, max_answer_length=50)
            if result['score'] > 0.5:  # Confidence threshold
                qa_pairs.append((question, result['answer']))
                break
    return qa_pairs

# Step 5: Generate unique keys for Streamlit components


def generate_unique_key(question):
    return hashlib.md5(question.encode()).hexdigest()

# Step 6: Display questions and answers for review using Streamlit


def display_and_review_qa(qa_pairs):
    st.title("Tự Động Sinh Câu Hỏi và Trả Lời từ Tài Liệu")

    reviewed_qa = []
    for question, answer in qa_pairs:
        st.write(f"**Câu hỏi:** {question}")
        st.write(f"**Trả lời:** {answer}")
        unique_key = generate_unique_key(question)  # Tạo key duy nhất
        selected = st.checkbox("Lưu câu hỏi này?", key=unique_key)
        if selected:
            reviewed_qa.append((question, answer))
    return reviewed_qa

# Step 7: Mock function to save QA pairs to database


def save_to_database(qa_pairs):
    if qa_pairs:
        for question, answer in qa_pairs:
            # Giả lập lưu vào database
            st.success(f"Đã lưu thành công: **Q:** {question} **A:** {answer}")
    else:
        st.warning("Không có câu hỏi nào được lưu.")

# Main function


def main():
    st.title("Sinh Câu Hỏi và Trả Lời Tự Động")
    uploaded_file = st.file_uploader("Tải lên file PDF", type=["pdf"])

    if uploaded_file is not None:
        # Step 1: Extract text from PDF
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        text = " ".join([page.extract_text()
                        for page in reader.pages if page.extract_text()])

        st.write("**Bước 1:** Chia văn bản thành các đoạn nhỏ.")
        chunks = split_text_with_sentences(text)
        st.write(f"Đã chia thành **{len(chunks)} đoạn**.")

        # Step 2: Generate questions
        st.write("**Bước 2:** Sinh câu hỏi từ văn bản.")
        questions = generate_questions_from_chunks(chunks)
        st.write(
            f"Sinh được **{len(questions)} câu hỏi** trước khi lọc trùng lặp.")

        # Step 3: Filter duplicate questions
        filtered_questions = filter_duplicate_questions(questions)
        st.write(
            f"**{len(filtered_questions)} câu hỏi** còn lại sau khi lọc trùng lặp.")

        # Step 4: Generate answers
        st.write("**Bước 3:** Tạo câu trả lời tương ứng.")
        qa_pairs = generate_answers(filtered_questions, chunks)
        st.write(f"Đã tạo **{len(qa_pairs)} cặp câu hỏi và câu trả lời**.")

        # Step 5: Review and save QA pairs
        st.write("**Bước 4:** Duyệt và chọn câu hỏi muốn lưu.")
        reviewed_qa = display_and_review_qa(qa_pairs)

        if st.button("Lưu vào Database"):
            save_to_database(reviewed_qa)


if __name__ == "__main__":
    main()
