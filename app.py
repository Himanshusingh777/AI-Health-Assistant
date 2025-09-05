import os
from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from sentence_transformers import SentenceTransformer, util

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "hacknavation.csv")

app = Flask(__name__)
app.secret_key = "supersecret"  # Needed to store conversation state

# Load dataset (expects columns: 'example', 'response', optional: 'follow_up_yes', 'follow_up_no')
df = pd.read_csv(DATA_PATH).dropna()
required_cols = {"example", "response"}
if not required_cols.issubset(df.columns):
    raise ValueError("Expected columns 'example' and 'response' in hacknavation.csv")

# Load embedding model (small + fast, good accuracy)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute embeddings for all examples
corpus = df["example"].astype(str).tolist()
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)


def retrieve_response(query: str):
    """Retrieve best matching response from dataset using semantic similarity"""
    if not query or not query.strip():
        return {"answer": "Please say or type something.", "score": 0.0, "match": ""}

    # Encode query
    query_emb = embedder.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(query_emb, corpus_embeddings)[0]

    # Get best match
    idx = int(scores.argmax())
    score = float(scores[idx])

    # Fallback if confidence is too low
    if score < 0.55:
        return {
            "answer": "I’m not fully sure I understood that. Could you rephrase?",
            "score": round(score, 4),
            "match": "",
        }

    answer = str(df.iloc[idx]["response"])
    match = str(df.iloc[idx]["example"])

    # Save context if follow-up columns exist
    follow_up_yes = str(df.iloc[idx].get("follow_up_yes", "")).strip() if "follow_up_yes" in df.columns else ""
    follow_up_no = str(df.iloc[idx].get("follow_up_no", "")).strip() if "follow_up_no" in df.columns else ""

    if follow_up_yes or follow_up_no:
        session["pending_followup"] = {
            "yes": follow_up_yes,
            "no": follow_up_no,
        }
        # Append follow-up question
        answer = f"{answer} Would you like me to help with this?"
    else:
        session.pop("pending_followup", None)

    return {"answer": answer, "score": round(score, 4), "match": match}


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip().lower()

    # ✅ Handle follow-ups if pending
    if session.get("pending_followup"):
        followup = session["pending_followup"]

        yes_words = {"yes", "yeah", "y", "sure", "ok", "okay"}
        no_words = {"no", "nah", "nope", "not now"}

        # Flexible matching (contains yes/no anywhere in input)
        if any(word in query for word in yes_words):
            answer = followup.get("yes", "Alright, let’s continue.")
            session.pop("pending_followup", None)
            return jsonify({"answer": answer, "score": 1.0, "match": "followup_yes"})

        elif any(word in query for word in no_words):
            answer = followup.get("no", "Okay, I understand.")
            session.pop("pending_followup", None)
            return jsonify({"answer": answer, "score": 1.0, "match": "followup_no"})

        # If not recognized as yes/no, clear follow-up and fall back
        session.pop("pending_followup", None)

    # ✅ Otherwise, do normal retrieval
    result = retrieve_response(query)
    return jsonify(result)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.route("/followup", methods=["POST"])
def followup():
    data = request.json
    choice = data.get("choice")

    if "pending_followup" not in session:
        return {"answer": "No follow-up pending."}

    followup_data = session.pop("pending_followup")

    if choice == "yes" and followup_data.get("yes"):
        return {"answer": followup_data["yes"]}
    elif choice == "no" and followup_data.get("no"):
        return {"answer": followup_data["no"]}
    else:
        return {"answer": "Okay, moving on."}


if __name__ == "__main__":
    app.run(debug=True)
