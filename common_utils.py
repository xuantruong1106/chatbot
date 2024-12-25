import os
import json
import csv
import time
import asyncio
import aiofiles
import streamlit as st
from langchain.llms import CTransformers
from langchain.chains import QAGenerationChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
# Use a pipeline as a high-level helper
from transformers import pipeline

# Load LLM model


def load_llm():
    pipe = pipeline("text-generation",
                    model="mistralai/Mistral-7B-Instruct-v0.3")
    return pipe

# File processing function to extract questions and answers


def file_processing(file_path):
    loader = PyPDFLoader(file_path)
    data = loader.load()

    question_gen = ''
    for page in data:
        question_gen += page.page_content

    splitter_ques_gen = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)

    document_ques_gen = [Document(page_content=t) for t in chunks_ques_gen]

    splitter_ans_gen = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )

    document_answer_gen = splitter_ans_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen

# LLM pipeline for question generation and answer retrieval


def llm_pipeline(file_path):
    document_ques_gen, document_answer_gen = file_processing(file_path)

    llm_ques_gen_pipeline = load_llm()

    prompt_template = """
    You are an expert at creating questions based on coding materials and documentation.
    Your goal is to prepare a coder or programmer for their exam and coding tests.
    You do this by asking questions about the text below:

    ------------
    {text}
    ------------

    Create questions that will prepare the coders or programmers for their tests.
    Make sure not to lose any important information.

    QUESTIONS:
    """

    PROMPT_QUESTIONS = PromptTemplate(
        template=prompt_template, input_variables=["text"])

    refine_template = ("""
    You are an expert at creating practice questions based on coding material and documentation.
    Your goal is to help a coder or programmer prepare for a coding test.
    We have received some practice questions to a certain extent: {existing_answer}.
    We have the option to refine the existing questions or add new ones.
    (only if necessary) with some more context below.
    ------------
    {text}
    ------------

    Given the new context, refine the original questions in English.
    If the context is not helpful, please provide the original questions.
    QUESTIONS:
    """
                       )

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
    )

    ques_gen_chain = load_summarize_chain(llm=llm_ques_gen_pipeline,
                                          chain_type="refine",
                                          verbose=True,
                                          question_prompt=PROMPT_QUESTIONS,
                                          refine_prompt=REFINE_PROMPT_QUESTIONS)

    ques = ques_gen_chain.run(document_ques_gen)

    embeddings = HuggingFaceBgeEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2")

    vector_store = FAISS.from_documents(document_answer_gen, embeddings)

    llm_answer_gen = load_llm()

    ques_list = ques.split("\n")
    filtered_ques_list = [element for element in ques_list if element.endswith(
        '?') or element.endswith('.')]

    answer_generation_chain = RetrievalQA.from_chain_type(llm=llm_answer_gen,
                                                          chain_type="stuff",
                                                          retriever=vector_store.as_retriever())

    return answer_generation_chain, filtered_ques_list

# Save questions and answers into CSV


def get_csv(file_path):
    answer_generation_chain, ques_list = llm_pipeline(file_path)
    base_folder = 'output/'
    if not os.path.isdir(base_folder):
        os.mkdir(base_folder)
    output_file = base_folder+"QA.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Question", "Answer"])

        for question in ques_list:
            answer = answer_generation_chain.run(question)
            csv_writer.writerow([question, answer])

    return output_file


# Streamlit UI code
st.title('PDF QA Generator')

# File upload
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    file_path = os.path.join("docs/", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Button to generate questions and answers
    if st.button('Generate Questions and Answers'):
        with st.spinner('Processing...'):
            output_file = get_csv(file_path)
            st.success(f"Questions and Answers CSV generated: {output_file}")
            st.download_button('Download CSV', output_file,
                               file_name='QA.csv', mime='text/csv')

else:
    st.info('Please upload a PDF file to begin.')
