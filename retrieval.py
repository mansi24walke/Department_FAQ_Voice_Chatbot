
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from faq_data import faq_data


# -----------------------------------------
# 1. CONFIGURATION
# -----------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"

# Initial thresholds; validate them with evaluation questions.
FAQ_THRESHOLD = 0.60
SCOPE_THRESHOLD = 0.30


# -----------------------------------------
# 2. LOAD SENTENCE-BERT MODEL
# -----------------------------------------

model = SentenceTransformer(MODEL_NAME)


# -----------------------------------------
# 3. DEPARTMENT SCOPE TOPICS
# -----------------------------------------

scope_topics = [
    "Questions about department academics, courses, programs, "
    "subjects, syllabus, curriculum and examinations.",

    "Questions about student placements, campus recruitment, "
    "placement support and placement opportunities.",

    "Questions about internships, internship opportunities "
    "and internship guidance.",

    "Questions about department events, activities, seminars "
    "and workshops.",

    "Questions about department facilities, laboratories, "
    "infrastructure and equipment.",

    "Questions about department faculty, HOD, coordinators "
    "and official department contact information."
]


# -----------------------------------------
# 4. VALIDATE FAQ DATA
# -----------------------------------------

if not faq_data:
    raise ValueError("FAQ dataset is empty!")

questions = [
    item["question"] for item in faq_data
]


# -----------------------------------------
# 5. GENERATE FAQ EMBEDDINGS
# -----------------------------------------

faq_embeddings = model.encode(
    questions,
    convert_to_numpy=True
).astype("float32")

faiss.normalize_L2(faq_embeddings)


# -----------------------------------------
# 6. GENERATE SCOPE EMBEDDINGS
# -----------------------------------------

scope_embeddings = model.encode(
    scope_topics,
    convert_to_numpy=True
).astype("float32")

faiss.normalize_L2(scope_embeddings)


# -----------------------------------------
# 7. CREATE FAISS INDEXES
# -----------------------------------------

dimension = faq_embeddings.shape[1]

faq_index = faiss.IndexFlatIP(dimension)
faq_index.add(faq_embeddings)

scope_index = faiss.IndexFlatIP(dimension)
scope_index.add(scope_embeddings)


# -----------------------------------------
# 8. CHECK DEPARTMENT QUESTION SCOPE
# -----------------------------------------

def check_department_scope(user_question):

    if not user_question or not user_question.strip():
        return False, 0.0

    query_embedding = model.encode(
        [user_question],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = scope_index.search(
        query_embedding,
        k=1
    )

    scope_score = float(scores[0][0])

    return (
        scope_score >= SCOPE_THRESHOLD,
        scope_score
    )


# -----------------------------------------
# 9. FAQ RETRIEVAL FUNCTION
# -----------------------------------------

def retrieve_faq(user_question):

    if not user_question or not user_question.strip():
        return {
            "status": "invalid"
        }

    # First check whether the question is department-related.
    is_in_scope, scope_score = check_department_scope(
        user_question
    )

    if not is_in_scope:
        return {
            "status": "out_of_scope",
            "scope_score": scope_score
        }

    # Generate query embedding.
    query_embedding = model.encode(
        [user_question],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    # Retrieve the closest FAQ.
    scores, indices = faq_index.search(
        query_embedding,
        k=1
    )

    best_index = int(indices[0][0])
    similarity_score = float(scores[0][0])

    if best_index < 0:
        return {
            "status": "unsupported",
            "scope_score": scope_score
        }

    # Department-related, but no sufficiently similar FAQ.
    if similarity_score < FAQ_THRESHOLD:
        return {
            "status": "unsupported",
            "scope_score": scope_score,
            "faq_score": similarity_score
        }

    # Return the verified FAQ.
    return {
        "status": "matched",
        "question": faq_data[best_index]["question"],
        "answer": faq_data[best_index]["answer"],
        "category": faq_data[best_index]["category"],
        "scope_score": scope_score,
        "faq_score": similarity_score
    }


# -----------------------------------------
# 10. TEST RETRIEVAL
# -----------------------------------------

if __name__ == "__main__":

    print("Department FAQ Hybrid Retrieval System")

    query = input("\nAsk your department question: ")

    result = retrieve_faq(query)

    print("\nRetrieval Result:", result["status"])

    if result["status"] == "matched":

        print("Category:", result["category"])
        print("Matched FAQ:", result["question"])
        print("Answer:", result["answer"])
        print("FAQ Similarity:", result["faq_score"])
        print("Scope Similarity:", result["scope_score"])

    elif result["status"] == "unsupported":

        print("Department-related question, but no matching FAQ.")
        print("Scope Similarity:", result["scope_score"])
        print("FAQ Similarity:", result["faq_score"])

    elif result["status"] == "out_of_scope":

        print("This question is outside the department FAQ scope.")
        print("Scope Similarity:", result["scope_score"])

    else:

        print("Please enter a valid question.")
