from transformers import pipeline
import torch


def generate_questions_and_answers_from_chunks(chunks):
    try:
        # Initialize GPT-2 question generation pipeline
        question_generator = pipeline(
            "text-generation",
            model="openai-community/gpt2-medium",  # Sử dụng GPT-2 từ Hugging Face
            max_length=128,
            num_return_sequences=2,  # Trả về 2 câu hỏi cho mỗi chunk
            temperature=0.7,  # Điều chỉnh độ sáng tạo của mô hình
            device=0 if torch.cuda.is_available() else -1
        )

        # Initialize GPT-2 answer generation pipeline
        answer_generator = pipeline(
            "text-generation",
            model="openai-community/gpt2-medium",  # Sử dụng GPT-2 để trả lời câu hỏi
            max_length=256,
            temperature=0.7,
            device=0 if torch.cuda.is_available() else -1
        )

        question_answer_pairs = []

        for chunk in chunks:
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue

            print(f"Processing chunk: {chunk}")

            # Generate questions
            input_text = f"Generate a question based on this text: {chunk}"
            questions = question_generator(input_text, num_return_sequences=2)
            print(f"Generated questions: {questions}")

            for q in questions:
                question = q['generated_text'].strip()
                print(f"Question: {question}")

                # Generate answer
                context = f"Answer the question: {question}\nContext: {chunk}"
                answer = answer_generator(context, num_return_sequences=1)[
                    0]['generated_text']
                print(f"Answer: {answer}")

                if len(question) > 10 and len(answer) > 20:  # Basic quality check
                    question_answer_pairs.append((question, answer))

        print(f"Generated {len(question_answer_pairs)} question-answer pairs.")
        return question_answer_pairs

    except Exception as e:
        print(f"Error in question generation: {e}")
        return []


# Test với dữ liệu tiếng Việt
chunks_vietnamese = [
    "Python là một ngôn ngữ lập trình phổ biến. Nó được sử dụng rộng rãi trong phát triển web, khoa học dữ liệu và học máy."
]

question_answer_pairs_vn = generate_questions_and_answers_from_chunks(
    chunks_vietnamese)

# In kết quả
if question_answer_pairs_vn:
    for idx, (question, answer) in enumerate(question_answer_pairs_vn, 1):
        print(f"Pair {idx}:\nQuestion: {question}\nAnswer: {answer}\n")
else:
    print("No question-answer pairs generated.")
