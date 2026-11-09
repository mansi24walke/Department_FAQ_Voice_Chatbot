
# Department FAQ Voice Chatbot

An AI-powered Department FAQ Voice Chatbot that helps students get information about academics, placements, internships, events and department facilities through text and voice conversations.

The system uses semantic FAQ retrieval, an LLM for natural responses, speech recognition and text-to-speech to provide a conversational experience while avoiding unsupported information.

## Features

- **Text-based Chat:** Ask department-related questions.
- **Voice Input:** Speak questions using the microphone.
- **Speech Recognition:** Uses OpenAI Whisper to convert speech into text.
- **Semantic FAQ Retrieval:** Uses Sentence-BERT and FAISS to retrieve relevant FAQ entries.
- **LLM-based Responses:** Uses Google Gemini to generate natural responses from verified FAQ context.
- **Conversation Memory:** Maintains context across multiple turns.
- **Text-to-Speech:** Uses pyttsx3 to generate spoken responses.
- **Hybrid Guardrails:** Separates department-related questions from unrelated questions and rejects unsupported queries.
- **Event Poster Generator:** Creates downloadable event posters using Python and Pillow.

## Project Architecture

1. User enters a question through text or voice.
2. Whisper transcribes voice input into text.
3. Sentence-BERT generates semantic embeddings.
4. FAISS retrieves the most relevant FAQ.
5. The hybrid retrieval system checks department scope and FAQ similarity.
6. Gemini generates a natural answer using the retrieved FAQ context.
7. pyttsx3 converts the response into speech.
8. The application displays the text and audio response.

## Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| LLM | Google Gemini |
| Embedding Model | Sentence-BERT (all-MiniLM-L6-v2) |
| Vector Search | FAISS |
| Speech Recognition | OpenAI Whisper |
| Text-to-Speech | pyttsx3 |
| Poster Generation | Pillow |
| Environment Variables | python-dotenv |

## Project Structure

```text
Department_FAQ_Voice_Chatbot/
│
├── app.py
├── chatbot.py
├── retrieval.py
├── faq_data.py
├── system_prompt.py
├── evaluation.py
├── poster_generator.py
├── requirements.txt
├── evaluation_results.csv
├── .env
├── .gitignore
│
└── pages/
    └── 2_Event_Poster_Generator.py
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Department_FAQ_Voice_Chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Gemini API key

Create a `.env` file in the project directory:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_supported_gemini_model
```

Do not upload your API key to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

## Evaluation Results

The hybrid retrieval system was evaluated using 10 test questions.

| Evaluation Metric | Result |
|---|---:|
| Total Questions | 10 |
| FAQ Matches | 8 |
| Unsupported Department Questions | 0 |
| Out-of-Scope Questions | 2 |
| Scope Classification Accuracy | 100% |

The test included department-related questions and out-of-scope questions.

The system successfully rejected unrelated queries and retrieved relevant FAQ entries for all eight department-related test questions.

These results apply to the selected test set and do not represent general model accuracy.

## Responsible AI and Safety

- Answers are generated using retrieved FAQ information.
- Unsupported questions receive a safe response.
- Questions outside the department scope are rejected.
- Users are advised not to enter personal or confidential information.
- API keys are stored in environment variables.
- Department information should be verified using official sources.

## Limitations

- Answer quality depends on the FAQ dataset.
- The system cannot provide information that is not included in its verified FAQ knowledge base.
- Speech recognition may occasionally misinterpret spoken questions.
- Gemini API access requires a valid API key and internet connection.
- Poster generation uses a programmatic design template rather than text-to-image AI.

## Future Improvements

- Expand the FAQ dataset with verified department information.
- Improve multilingual speech recognition.
- Add an administrator interface to manage FAQs.
- Integrate AI-based text-to-image poster generation.
- Deploy the application for public access.

## License

This project is developed for academic and educational purposes.

Third-party models, libraries and APIs remain subject to their respective licenses and terms of use.

## Author

Developed as an academic AI project.
