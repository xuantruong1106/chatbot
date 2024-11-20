import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet

def quick_comparison(str1, str2):
    """So sánh nhanh dựa trên ký tự và từ chung"""
    set1, set2 = set(str1), set(str2)
    char_similarity = len(set1.intersection(set2)) / len(set1.union(set2))

    words1, words2 = set(str1.split()), set(str2.split())
    word_similarity = len(words1.intersection(words2)) / len(words1.union(words2))

    return (char_similarity + word_similarity) / 2


def levenshtein_distance_similarity(str1, str2):
    """Tính độ tương tự dựa trên khoảng cách Levenshtein"""
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    edit_distance = dp[m][n]
    max_length = max(len(str1), len(str2))
    return 1 - edit_distance / max_length


def semantic_analysis(str1, str2):
    """Phân tích ngữ nghĩa bằng cách so sánh từ đồng nghĩa"""
    def get_synonyms(word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return synonyms

    words1, words2 = str1.split(), str2.split()
    match_count = 0

    for word1 in words1:
        synonyms1 = get_synonyms(word1)
        for word2 in words2:
            if word2 in synonyms1 or word1 == word2:
                match_count += 1
                break

    total_words = max(len(words1), len(words2))
    return match_count / total_words if total_words > 0 else 0


def compare_strings_highest_score(str1, str2):
    # Chạy tất cả các phương pháp so sánh
    quick_score = quick_comparison(str1, str2)
    precise_score = levenshtein_distance_similarity(str1, str2)
    semantic_score = semantic_analysis(str1, str2)

    # Lấy điểm số cao nhất
    highest_score = max(quick_score, precise_score, semantic_score)

    result = {
        "quick_score": quick_score ,
        "precise_score": precise_score,
        "semantic_score": semantic_score,
        "highest_score": highest_score,
        "method": (
            "Quick Comparison" if highest_score == quick_score else
            "Levenshtein Distance" if highest_score == precise_score else
            "Semantic Analysis"
        )
    }
    
    for key, value in result.items():
        print(f"{key}: {value} \n")
        


# Ví dụ chạy thử
string1 = "Tôi thích lập trình  "
string2 = "Tôi yêu viết code"

result = compare_strings_highest_score(string1, string2)
print(result)
