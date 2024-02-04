from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET", "POST"])
def do_reply():
    if request.method == "GET":
        return f"<p>This is a {request.method}</p>"
    if request.method == "POST":
        data = request.get_data()
        return data
    
@app.route("/questions/<int:question_id>")
def find_question(question_id):
    return ("you asked for question{0}".format(question_id))
        
