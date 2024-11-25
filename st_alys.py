from nltk.corpus import wordnet
import torch
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def quick_comparison(str1, str2):
    """So sánh nhanh dựa trên ký tự và từ chung"""
    set1, set2 = set(str1), set(str2)
    char_similarity = len(set1.intersection(set2)) / len(set1.union(set2))

    words1, words2 = set(str1.split()), set(str2.split())
    word_similarity = len(words1.intersection(words2)) / len(words1.union(words2))

    return (char_similarity + word_similarity) / 2

def sentence_transformers(str1, str2):
        emb1 = model.encode(str1, convert_to_tensor=True)
        emb2 = model.encode(str2, convert_to_tensor=True)
        similarity = util.cos_sim(emb1, emb2)
        return similarity.item()

def compare_strings_highest_score(str1, str2):
    quick_score = quick_comparison(str1, str2)
    sentence_transformers_score = sentence_transformers(str1, str2)
    if ( (quick_score or sentence_transformers_score)> 0.75):
        return True
    return False


