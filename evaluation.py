
import csv
from retrieval import retrieve_faq


# -----------------------------------------
# 1. TEST DATASET
# -----------------------------------------

test_questions = [
    {
        "question": "How can I get an internship?",
        "expected": "department"
    },
    {
        "question": "Where can students find internship opportunities?",
        "expected": "department"
    },
    {
        "question": "What facilities are available in the department?",
        "expected": "department"
    },
    {
        "question": "How can I know about department events?",
        "expected": "department"
    },
    {
        "question": "Who should I contact for placement information?",
        "expected": "department"
    },
    {
        "question": "Explain the department's academic programs.",
        "expected": "department"
    },
    {
        "question": "Where can I find information about the syllabus?",
        "expected": "department"
    },
    {
        "question": "What laboratories are available in the department?",
        "expected": "department"
    },
    {
        "question": "What is the capital of France?",
        "expected": "out_of_scope"
    },
    {
        "question": "Explain photosynthesis.",
        "expected": "out_of_scope"
    }
]


# -----------------------------------------
# 2. EVALUATION
# -----------------------------------------

results = []

correct = 0
matched = 0
unsupported = 0
out_of_scope = 0

print("\nDEPARTMENT FAQ CHATBOT")
print("HYBRID RETRIEVAL EVALUATION")
print("=" * 65)

for i, test in enumerate(test_questions, start=1):

    question = test["question"]
    expected = test["expected"]

    result = retrieve_faq(question)

    status = result["status"]

    # Department-related questions may be
    # matched or safely classified as unsupported.

    if expected == "department":

        passed = status in ["matched", "unsupported"]

    else:

        passed = status == "out_of_scope"

    if passed:
        correct += 1

    if status == "matched":
        matched += 1

    elif status == "unsupported":
        unsupported += 1

    elif status == "out_of_scope":
        out_of_scope += 1

    faq_score = result.get("faq_score", "")
    scope_score = result.get("scope_score", "")

    print(f"\nTest {i}")
    print("Question:", question)
    print("Expected:", expected)
    print("Actual:", status)
    print("FAQ Score:", faq_score)
    print("Scope Score:", scope_score)
    print("Result:", "PASS" if passed else "FAIL")

    results.append({
        "Test Number": i,
        "Question": question,
        "Expected": expected,
        "Actual": status,
        "FAQ Score": faq_score,
        "Scope Score": scope_score,
        "Result": "PASS" if passed else "FAIL"
    })


# -----------------------------------------
# 3. CALCULATE METRICS
# -----------------------------------------

total = len(test_questions)

accuracy = (correct / total) * 100

print("\n" + "=" * 65)
print("FINAL EVALUATION SUMMARY")
print("=" * 65)

print("Total Questions:", total)
print("Correct Scope Classifications:", correct)
print("FAQ Matches:", matched)
print("Unsupported Department Questions:", unsupported)
print("Out-of-Scope Questions:", out_of_scope)

print(f"Scope Classification Accuracy: {accuracy:.2f}%")

# -----------------------------------------
# 4. SAVE RESULTS TO CSV
# -----------------------------------------

with open(
    "evaluation_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)

print("\nResults saved to evaluation_results.csv")
