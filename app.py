from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.String(256))
    image_url = db.Column(db.String(512))

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url
        }

    def json_with_questions(self):
        questions = Question.query.filter(Question.quizId == self.id)
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "questions": [question.json() for question in questions],
            "image_url": self.image_url
        }


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quizId = db.Column(db.Integer)
    question = db.Column(db.String(256))
    answer = db.Column(db.String(256))

    def json(self):
        return {
            "id": self.id,
            "quizId": self.quizId,
            "question": self.question,
            "answer": self.answer
        }


with app.app_context():
    db.create_all()


# Quiz section
@app.route('/quiz', methods=["GET"])
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([quiz.json() for quiz in quizzes])


@app.route('/quiz/<int:id>', methods=["GET", "DELETE", "PUT"])
@app.route('/quiz', methods=["POST"])
def quiz_func(id=None):
    if request.method == "POST":
        data = request.get_json(force=True)
        title = data["title"]
        description = data["description"]
        image_url = data["image_url"]
        quiz = Quiz(title=title, description=description, image_url=image_url)
        db.session.add(quiz)
        db.session.commit()
    else:
        quiz = Quiz.query.get(id)

        if request.method == "DELETE":
            db.session.delete(quiz)
            db.session.commit()
            return {
                "Message": f"Quiz with ID {id} has been deleted"
            }

        if request.method == "PUT":
            data = request.json

            if "title" in data:
                quiz.title = data["question"]
            if "description" in data:
                quiz.description = data["description"]
            if "image_url" in data:
                quiz.image_url = data["image_url"]

            db.session.commit()

    return quiz.json_with_questions()


# Question section
@app.route('/question', methods=["GET"])
def get_questions():
    questions = Question.query.all()
    return jsonify([question.json() for question in questions])


@app.route('/question/<int:id>', methods=["GET", "DELETE", "PUT"])
@app.route('/question', methods=["POST"])
def question_func(id=None):
    if request.method == "POST":
        data = request.get_json(force=True)
        question = data["question"]
        answer = data["answer"]
        quizId = data["quizId"]

        if Quiz.query.get(quizId) is None:
            return {
                "Message": f"Unable to create question, quiz ID {quizId} does not exist"
            }

        question = Question(quizId=quizId, question=question, answer=answer)
        db.session.add(question)
        db.session.commit()
    else:
        question = Question.query.get(id)

        if request.method == "DELETE":
            db.session.delete(question)
            db.session.commit()
            return {
                "Message": f"Question with ID {id} has been deleted"
            }

        if request.method == "PUT":
            data = request.json

            if "question" in data:
                question.question = data["question"]
            if "answer" in data:
                question.answer = data["answer"]

            db.session.commit()

    return question.json()


if __name__ == '__main__':
    app.run()
