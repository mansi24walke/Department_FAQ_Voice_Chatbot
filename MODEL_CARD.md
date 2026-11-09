
# Model Card – Department FAQ Voice Chatbot

## 1. Project Overview

The Department FAQ Voice Chatbot is an AI-based application designed to answer student questions about academics, placements, internships, events and department facilities.

It supports both text and voice interactions and uses semantic retrieval with an LLM-based response generation system.

## 2. Models Used

### A. Sentence-BERT

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Purpose: Converts FAQ questions and user queries into numerical embeddings.
- Usage: Helps identify semantically similar FAQ questions.
- Integration: Used with FAISS for similarity-based retrieval.

### B. Google Gemini

- Model: Configured through the `GEMINI_MODEL` environment variable.
- Purpose: Generates natural-language responses.
- Usage: Receives retrieved FAQ context and generates an appropriate response.
- Safety: The application restricts responses to retrieved FAQ information.

### C. OpenAI Whisper

- Model: Whisper `base`
- Purpose: Converts voice input into text.
- Usage: Transcribes spoken student questions before processing them through the chatbot.

### D. Qwen LoRA Fine-Tuning Experiment

- Base model: `Qwen/Qwen2.5-0.5B-Instruct`
- Fine-tuning method: LoRA (Low-Rank Adaptation)
- Training version: V3
- Training dataset: 42 examples
- Training epochs: 5
- Purpose: Experimented with adapting a language model to department FAQ responses and out-of-scope questions.

**Note:** The LoRA experiment is separate from the current live chatbot response pipeline. The live application uses Gemini for response generation.

## 3. Retrieval System

The retrieval pipeline uses:

1. Sentence-BERT to generate embeddings.
2. FAISS to search for similar FAQ entries.
3. Similarity thresholds to identify relevant questions.
4. Scope checking to reject unrelated queries.
5. A safe fallback response when verified information is unavailable.

## 4. Evaluation

The hybrid retrieval system was tested using 10 questions.

| Metric | Result |
|---|---:|
| Total test questions | 10 |
| FAQ matches | 8 |
| Unsupported department questions | 0 |
| Out-of-scope questions | 2 |
| Scope classification accuracy | 100% |

The evaluation included eight department-related questions and two out-of-scope questions.

The system correctly classified all questions in this test set.

The results are preliminary and should not be interpreted as general-purpose model accuracy.

## 5. LoRA Experiment Evaluation

The Qwen LoRA V3 experiment was evaluated using a separate 10-question test.

- Manually assessed result: 9/10.
- Preliminary correctness: 90%.
- The model correctly refused most unrelated questions.
- One out-of-scope question about photosynthesis was answered instead of being refused.

This demonstrated why retrieval-based guardrails are important for reliable FAQ applications.

## 6. Limitations

- The chatbot depends on the quality and coverage of its FAQ dataset.
- It cannot guarantee correct answers for information that is missing or outdated.
- Speech recognition can make transcription errors.
- Gemini requires API access and an internet connection.
- The LoRA experiment is not integrated into the live response pipeline.
- Evaluation uses a small, manually selected test set.

## 7. Ethical Considerations

- Users are advised not to submit confidential or personal information.
- The system avoids inventing unsupported department information.
- Out-of-scope questions are rejected.
- Official information should be verified with the department.
- Third-party models and libraries are subject to their respective licenses and terms.

## 8. Intended Use

This project is intended for educational demonstration and as a prototype for department-level student assistance.

It is not an official university information service.

## 9. Future Improvements

- Expand and regularly update the FAQ dataset.
- Add multilingual support.
- Improve out-of-scope detection.
- Integrate the LoRA model into a controlled response pipeline if appropriate.
- Perform larger-scale evaluation using verified department questions.
