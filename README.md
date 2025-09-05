# AI Agent (Voice + Text) from Your CSV

This project turns your `hacknavation.csv` into a lightweight retrieval-based AI agent
with both **text** and **voice** (browser) support.

- Dataset format expected: two columns — `example` (prompt) and `response` (answer).
- Backend: Flask + scikit-learn TF-IDF for semantic matching.
- Frontend: Web Speech API for speech-to-text and speech synthesis (Chrome), plus text chat UI.

## Quickstart

1) Create a virtual environment and install requirements:
```bash
python -m venv .venv
. .venv/Scripts/activate  # on Windows
# or: source .venv/bin/activate  # on macOS/Linux

pip install -r requirements.txt
```

2) Run the server:
```bash
python app.py
```
Then visit http://localhost:5000

## How it works

- On startup, the app loads `data/hacknavation.csv` and builds a TF-IDF model on the `example` text.
- When you ask (typed or voice), the backend retrieves the closest `example` by cosine similarity
  and returns its paired `response`.
- The UI can speak the answer aloud using `speechSynthesis` (toggle on/off).

## Updating the Knowledge Base

- Just edit `data/hacknavation.csv` and restart the app.
- Keep the two-column structure with headers `example,response`.

## Notes

- Voice input/output relies on browser Web Speech APIs. Use Chrome for best support.
- For offline server-side voice, consider libraries like `vosk` (STT) and `pyttsx3` (TTS),
  and replace the Web Speech parts in `static/script.js` with backend endpoints.

## Project Structure

```
ai-agent/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── hacknavation.csv
├── templates/
│   └── index.html
└── static/
    ├── script.js
    └── style.css
```