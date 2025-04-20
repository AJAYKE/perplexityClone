from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_sse import sse
from models import Chat, SearchResult, Session, db

from backend.services.llm import LLMService
from backend.services.search import SearchService

app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(sse, url_prefix="/stream")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:password@localhost:5432/perplexity"
)
db = SQLAlchemy(app)


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question_text = data.get("question")
    session_id = data.get("session_id")  # optionally pass existing session

    # Create or fetch session
    if session_id:
        session = Session.query.get(session_id)
    else:
        user_id = data.get("user_id")
        session = Session(user_id=user_id, timestamp=db.func.now())
        db.session.add(session)
        db.session.commit()

    # Persist chat question
    chat = Chat(
        session_id=session.id,
        question_text=question_text,
        asked_at=db.func.now(),
    )
    db.session.add(chat)
    db.session.commit()

    # Run search
    extracted_text = SearchService().search(question_text)
    sr = SearchResult(
        chat_id=chat.id,
        search_result=",".join([url for _, url in extracted_text]),
        timestamp=db.func.now(),
    )
    db.session.add(sr)
    db.session.commit()

    # kick off streaming
    answer_text = "".join(LLMService().stream_answer(question_text, extracted_text))
    chat.llm_result_text = answer_text
    chat.answered_at = db.func.now()
    db.session.add(chat)
    db.session.commit()

    return jsonify({"response": answer_text, "session_id": session.id})


if __name__ == "__main__":
    app.run(debug=True)
