from flask import render_template, request
from app import app, db
from datetime import datetime, timedelta
from bson.objectid import ObjectId

exams_collection = db["exams"]
exam_results_collection = db["exam_results"]

STUDENT_ID = "S-CAROL"  # Dummy student ID for demo

# Dashboard route
@app.route('/')
def dashboard():
    exams = list(exams_collection.find())
    now = datetime.now()

    for exam in exams:
        exam['_id'] = str(exam['_id'])

        # Use exam_date and exam_time from seed.py or defaults
        exam_date_str = exam.get('exam_date', now.strftime('%Y-%m-%d'))
        exam_time_str = exam.get('exam_time', '09:00')

        # Create a schedule dict for template
        exam['schedule'] = {
            "date": exam_date_str,
            "time": exam_time_str
        }

        # Convert to datetime objects
        exam_start = datetime.strptime(f"{exam_date_str} {exam_time_str}", "%Y-%m-%d %H:%M")
        exam_end = exam_start + timedelta(minutes=exam.get('duration', 60))

        exam['start_time'] = exam_start   # datetime object
        exam['end_time'] = exam_end       # datetime object

        # Determine status
        if exam_start <= now <= exam_end:
            exam['status'] = "Active"
        elif now < exam_start:
            exam['status'] = "Upcoming"
        else:
            exam['status'] = "Ended"

    return render_template('student_exam.html', exams=exams)

# Start exam route
@app.route('/exam/<exam_id>')
def start_exam(exam_id):
    try:
        oid = ObjectId(exam_id)
    except Exception:
        return "Invalid exam ID"

    exam_doc = exams_collection.find_one({"_id": oid})
    if not exam_doc:
        return "Exam not found!"

    now = datetime.now()
    exam_doc['_id'] = str(exam_doc['_id'])

    # Use exam_date and exam_time from seed.py or defaults
    exam_date_str = exam_doc.get('exam_date', now.strftime('%Y-%m-%d'))
    exam_time_str = exam_doc.get('exam_time', '09:00')

    # Schedule dict for template
    exam_doc['schedule'] = {
        "date": exam_date_str,
        "time": exam_time_str
    }

    # Convert to datetime objects
    exam_start = datetime.strptime(f"{exam_date_str} {exam_time_str}", "%Y-%m-%d %H:%M")
    # Support duration keys 'duration_minutes' or 'duration' in DB
    duration_minutes = int(exam_doc.get('duration_minutes', exam_doc.get('duration', 60)))
    # Expose both keys for template compatibility
    exam_doc['duration_minutes'] = duration_minutes
    exam_doc['duration'] = duration_minutes
    exam_end = exam_start + timedelta(minutes=duration_minutes)

    exam_doc['start_time'] = exam_start
    exam_doc['end_time'] = exam_end

    # Compute remaining seconds for timer; ensure non-negative integer
    remaining_seconds = int((exam_end - now).total_seconds())
    exam_doc['remaining_seconds'] = max(0, remaining_seconds)

    # Dummy questions if none in DB (replace with real questions)
    exam_doc['questions'] = exam_doc.get('questions', [
        {"question_text": "Sample Q1", "options": ["A", "B", "C"], "answer": "A"},
        {"question_text": "Sample Q2", "options": ["True", "False"], "answer": "True"}
    ])

    return render_template('start_exam.html', exam=exam_doc)

# Submit exam route
@app.route('/exam/<exam_id>/submit', methods=['POST'])
def submit_exam(exam_id):
    try:
        oid = ObjectId(exam_id)
    except Exception:
        return "Invalid exam ID"

    exam = exams_collection.find_one({"_id": oid})
    if not exam:
        return "Exam not found!"

    now = datetime.now()
    score = 0
    total = len(exam.get('questions', []))

    for idx, q in enumerate(exam.get('questions', []), start=1):
        submitted = request.form.get(f'q{idx}')
        correct = q.get('answer')
        if submitted is not None and str(submitted).strip() == str(correct).strip():
            score += 1

    # Save result
    exam_results_collection.insert_one({
        "exam": oid,
        "student": STUDENT_ID,
        "score": score,
        "total": total,
        "submitted_at": now,
        "status": "SUBMITTED"
    })

    return render_template('exam_result.html', score=score, total=total)
