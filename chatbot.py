
import re
import os
from dotenv import load_dotenv
from google import genai

from system_prompt import get_system_prompt
from retrieval import retrieve_faq


# -----------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# -----------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# -----------------------------------------
# 2. INITIALIZE GEMINI CLIENT
# -----------------------------------------

client = genai.Client(api_key=API_KEY)


# -----------------------------------------
# 3. SAFE RESPONSE MESSAGES
# -----------------------------------------

OUT_OF_SCOPE_MESSAGE = (
    "Sorry, I can answer only questions related to department "
    "academics, placements, internships, events and facilities. "
    "Please ask a department-related question."
)

UNSUPPORTED_MESSAGE = (
    "Sorry, I don't have verified information about this topic. "
    "Please contact the department for accurate information."
)

INVALID_MESSAGE = "Please enter a valid department-related question."


# -----------------------------------------
# 4. FOLLOW-UP QUESTION HANDLING
# -----------------------------------------

def get_previous_faq(history):

    for step in reversed(history):

        if isinstance(step, dict):
            content = step.get("content", [])

        else:
            if hasattr(step, "model_dump"):
                step = step.model_dump()
            else:
                continue

            content = step.get("content", [])

        if isinstance(content, dict):
            content = [content]

        for item in content:

            if not isinstance(item, dict):
                continue

            if item.get("type") != "text":
                continue

            text = item.get("text", "")

            if "VERIFIED DEPARTMENT FAQ:" not in text:
                continue

            category_match = re.search(r"Category:\s*(.+)", text)
            question_match = re.search(r"Question:\s*(.+)", text)
            answer_match = re.search(r"Answer:\s*(.+)", text)

            if category_match and question_match and answer_match:

                return {
                    "category": category_match.group(1).strip(),
                    "question": question_match.group(1).strip(),
                    "answer": answer_match.group(1).strip()
                }

    return None


def is_follow_up_question(question):

    follow_up_patterns = [
        r"\bthose\b",
        r"\bthese\b",
        r"\bthem\b",
        r"\bthey\b",
        r"\btheir\b",
        r"\bthat\b",
        r"\bthis\b",
        r"\bit\b",
        r"\bthere\b",
        r"\bsuch\b"
    ]

    question = question.lower()

    return any(
        re.search(pattern, question)
        for pattern in follow_up_patterns
    )


def is_answerable_from_previous_faq(question, previous_faq):

    question = question.lower().strip()
    answer = previous_faq["answer"].lower()

    # Safe repetition requests
    repeat_patterns = [
        r"explain that again",
        r"explain it again",
        r"repeat that",
        r"repeat it",
        r"say that again",
        r"tell me again",
        r"could you repeat",
        r"can you repeat"
    ]

    if any(re.search(pattern, question) for pattern in repeat_patterns):
        return "repeat"

    # Where questions
    if question.startswith("where"):
        return any(
            word in answer
            for word in ["check", "find", "available", "announcements", "notices"]
        )

    # When questions
    if question.startswith("when"):
        return any(
            word in answer
            for word in ["when", "date", "schedule", "timing"]
        )

    # Who questions
    if question.startswith("who"):
        return any(
            word in answer
            for word in ["contact", "coordinator", "department", "office"]
        )

    # How questions
    if question.startswith("how"):
        return bool(answer)

    return False


# -----------------------------------------
# 5. CHATBOT RESPONSE FUNCTION
# -----------------------------------------

def get_bot_response(user_message, history=None):

    if history is None:
        history = []

    # STEP 1: VALIDATE INPUT

    if not isinstance(user_message, str) or not user_message.strip():
        return INVALID_MESSAGE, history

    user_message = user_message.strip()

    # STEP 2: NORMAL FAQ RETRIEVAL

    result = retrieve_faq(user_message)

    # STEP 3: FOLLOW-UP CONTEXT HANDLING

    previous_faq = get_previous_faq(history)

    if (
        previous_faq
        and is_follow_up_question(user_message)
        and result["status"] == "out_of_scope"
    ):

        print("Follow-up question detected.")

        follow_up_result = is_answerable_from_previous_faq(
            user_message,
            previous_faq
        )

        if follow_up_result == "repeat":

            print("Repeating previous verified FAQ answer.")

            return previous_faq["answer"], history

        elif follow_up_result:

            print("Previous verified FAQ context available.")

            result = retrieve_faq(previous_faq["question"])

            if result["status"] == "matched":

                print(
                    "Using previous FAQ:",
                    result["question"]
                )

        else:

            print(
                "Follow-up requires information "
                "not verified in the previous FAQ."
            )

            return UNSUPPORTED_MESSAGE, history

    # STEP 4: CHECK RETRIEVAL STATUS

    status = result["status"]

    if status == "invalid":
        return INVALID_MESSAGE, history

    if status == "out_of_scope":

        print("Question Status: Out of Scope")
        print("Scope Score:", result.get("scope_score"))

        return OUT_OF_SCOPE_MESSAGE, history

    if status == "unsupported":

        print("Question Status: Unsupported")
        print("Scope Score:", result.get("scope_score"))
        print("FAQ Score:", result.get("faq_score"))

        return UNSUPPORTED_MESSAGE, history

    # STEP 5: GENERATE VERIFIED FAQ ANSWER

    if status == "matched":

        print("Question Status: FAQ Matched")
        print("Matched FAQ:", result["question"])
        print("FAQ Score:", result["faq_score"])

        faq_context = f"""
VERIFIED DEPARTMENT FAQ:

Category: {result['category']}
Question: {result['question']}
Answer: {result['answer']}
"""

        prompt = f"""
{faq_context}

STUDENT QUESTION:
{user_message}

INSTRUCTIONS:

- Answer using only the verified FAQ information above.
- Give a clear and natural response.
- Use conversation history only to understand references.
- Do not invent department information.
- Do not add facts that are not present in the verified FAQ.
- Do not guess dates, names, emails, schedules or policies.
- If the FAQ does not contain the requested information,
  clearly state that verified information is unavailable.
"""

        # STEP 6: UPDATE CONVERSATION HISTORY

        new_user_step = {
            "type": "user_input",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }

        request_history = history + [new_user_step]

        # STEP 7: GENERATE GEMINI RESPONSE

        try:

            response = client.interactions.create(
                model=MODEL,
                input=request_history,
                system_instruction=get_system_prompt(),
                store=False
            )

            answer = response.output_text or (
                "Sorry, I could not generate a response."
            )

            updated_history = (
                request_history + list(response.steps)
            )

            return answer, updated_history

        except Exception as error:

            print("Gemini API Error:", error)

            return (
                "Sorry, I am unable to process your request right now. "
                "Please try again.",
                history
            )

    # STEP 8: UNEXPECTED RETRIEVAL STATUS

    return UNSUPPORTED_MESSAGE, history
