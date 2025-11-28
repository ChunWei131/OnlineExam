from flask import Flask
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["EduAssessDB"]

# Collections
exams_collection = db["exams"]
exam_results_collection = db["exam_results"]

# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------
def calculate_score(questions, answers):
    """Calculate score based on correct answers."""
    score = 0
    for i, q in enumerate(questions):
        if i < len(answers) and answers[i] == q.get("answer"):
            score += 1
    return score

def get_exam_status(start_time, end_time):
    """Return exam status: Upcoming, Active, or Ended"""
    now = datetime.now()
    if now < start_time:
        return "Upcoming"
    elif start_time <= now <= end_time:
        return "Active"
    else:
        return "Ended"

def remaining_seconds(end_time):
    """Return number of seconds left for the exam."""
    now = datetime.now()
    remaining = (end_time - now).total_seconds()
    return max(int(remaining), 0)

# Import routes after app and db are initialized
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
