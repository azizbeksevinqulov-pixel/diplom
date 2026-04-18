from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def grade_answer(student_answer, correct_answer):
    if not student_answer or not correct_answer:
        return 0.0
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([student_answer, correct_answer])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(similarity * 100, 2)
