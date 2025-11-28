# ---- seed.py ----
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")

# 🚨 Reset the whole database (drops ALL collections + indexes)
client.drop_database("EduAssessDB")

db = client["EduAssessDB"]

# --- Collections ---
users                = db["users"]
institutions         = db["institutions"] #display as admin
educators            = db["educators"] #display as instructors
students             = db["students"]
faculties            = db["faculties"]
courses              = db["courses"]
enrollments          = db["enrollments"]

# Exams (open-ended)
exams                = db["exams"]
exam_schedules       = db["exam_schedules"]
exam_students        = db["exam_students"]
pause_exams          = db["pause_exams"]
exam_chats           = db["exam_chats"]
exam_submissions     = db["exam_submissions"]
exam_answers         = db["exam_answers"]
exam_results         = db["exam_results"]

# Question bank
questions            = db["questions"]
exam_questions       = db["exam_questions"]  # Bridge table: exam -> questions

# Invigilation + Incidents
invigilators         = db["invigilators"]
incidents            = db["incidents"]

# Student Academic Records (Semester GPA/CGPA)
student_semester_records = db["student_semester_records"]

# Course Final Grades (combines all assessments)
course_results = db["course_results"]

# Academic Semesters (for consistency)
semesters = db["semesters"]

all_colls = [
    users, institutions, educators, students, faculties, courses, enrollments, exams, exam_schedules, exam_students, pause_exams, exam_chats, exam_submissions,
    exam_answers, exam_results, invigilators, incidents, questions, exam_questions,
    student_semester_records, course_results, semesters
]

# Clear old data (not strictly necessary after drop_database, but harmless)
for c in all_colls:
    c.delete_many({})

# Helper for audit fields
def audit(user_id=1, created=None):
    now = datetime.now() if created is None else created
    return {
        "last_modification_user_id": user_id,
        "last_modification_time": now,
        "creation_time": now,
        "is_active": True,
        "is_deleted": False
    }

# --- Core Users (base class) ---
user_docs = [
    {
        "name": "System Admin",
        "email": "admin@eduassess.edu",
        "password": "hashed-admin-pass",
        "role": "ADMIN",
        "date_of_birth": datetime(1990, 1, 1),
        "phone_number": "+60123456789",
        **audit(1)
    },
    {
        "name": "Registrar Inst One",
        "email": "registrar@inst1.edu",
        "password": "hashed-registrar-pass",
        "role": "INSTITUTION",
        "date_of_birth": datetime(1985, 5, 20),
        "phone_number": "+60111222333",
        **audit(1)
    },
    {
        "name": "Dr. Alice Johnson",
        "email": "alice@inst1.edu",
        "password": "hashed-pass",
        "role": "EDUCATOR",
        "date_of_birth": datetime(1980, 7, 12),
        "phone_number": "+60193334455",
        **audit(1)
    },
    {
        "name": "Prof. Bob Smith",
        "email": "bob@inst1.edu",
        "password": "hashed-pass",
        "role": "EDUCATOR",
        "date_of_birth": datetime(1978, 2, 2),
        "phone_number": "+60195556677",
        **audit(1)
    },
    {
        "name": "Carol Lee",
        "email": "carol@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2004, 9, 9),
        "phone_number": "+60197778899",
        **audit(1)
    },
    {
        "name": "David Tan",
        "email": "david@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2003, 12, 25),
        "phone_number": "+60198889900",
        **audit(1)
    },
    {
        "name": "Emma Wilson",
        "email": "emma@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2004, 3, 15),
        "phone_number": "+60191112233",
        **audit(1)
    },
    {
        "name": "Frank Chen",
        "email": "frank@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2003, 7, 8),
        "phone_number": "+60192223344",
        **audit(1)
    },
    {
        "name": "Grace Martinez",
        "email": "grace@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2004, 11, 20),
        "phone_number": "+60193334455",
        **audit(1)
    },
    {
        "name": "Henry Kim",
        "email": "henry@student.inst1.edu",
        "password": "hashed-student-pass",
        "role": "STUDENT",
        "date_of_birth": datetime(2003, 5, 2),
        "phone_number": "+60194445566",
        **audit(1)
    }
]
user_ids = users.insert_many(user_docs).inserted_ids

# --- Role wrappers ---

institution_id = institutions.insert_one({
    "name": "EduAssess Institute of Software",
    "user": user_ids[1],
    **audit(user_ids[1])
}).inserted_id

educator_ids = educators.insert_many([
    {"educator_id": "E-ALICE", "department": "Software Engineering", "user": user_ids[2], "status": "ACTIVE", **audit(user_ids[2])},
    {"educator_id": "E-BOB",   "department": "Computer Science",     "user": user_ids[3], "status": "ACTIVE", **audit(user_ids[3])}
]).inserted_ids

student_ids = students.insert_many([
    {"student_id": "S-CAROL", "grade_level": "UG-Year3", "user": user_ids[4], **audit(user_ids[4])},
    {"student_id": "S-DAVID", "grade_level": "UG-Year3", "user": user_ids[5], **audit(user_ids[5])},
    {"student_id": "S-EMMA", "grade_level": "UG-Year2", "user": user_ids[6], **audit(user_ids[6])},
    {"student_id": "S-FRANK", "grade_level": "UG-Year3", "user": user_ids[7], **audit(user_ids[7])},
    {"student_id": "S-GRACE", "grade_level": "UG-Year2", "user": user_ids[8], **audit(user_ids[8])},
    {"student_id": "S-HENRY", "grade_level": "UG-Year3", "user": user_ids[9], **audit(user_ids[9])}
]).inserted_ids

# --- Faculty & Courses ---
faculty_ids = faculties.insert_many([
    {"name": "Faculty of Computing", "description": "All CS/SE programs", **audit(user_ids[1])}
]).inserted_ids

course_ids = courses.insert_many([
    {"name": "Software Engineering", "code": "CS301", "course_id": "CS301", "faculty": faculty_ids[0], "description": "SE fundamentals", "status": "ACTIVE", **audit(user_ids[2])},
    {"name": "Software Testing",     "code": "CS302", "course_id": "CS302", "faculty": faculty_ids[0], "description": "Testing theory",  "status": "ACTIVE", **audit(user_ids[2])},
    {"name": "Software Security",    "code": "CS303", "course_id": "CS303", "faculty": faculty_ids[0], "description": "AppSec & threat modeling", "status": "ACTIVE", **audit(user_ids[3])}
]).inserted_ids

# --- Enrollment (Course <-> Student) ---
enrollments.insert_many([
    {"course": course_ids[0], "student": student_ids[0], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[4])},
    {"course": course_ids[1], "student": student_ids[0], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[4])},
    {"course": course_ids[2], "student": student_ids[0], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[4])},
    {"course": course_ids[2], "student": student_ids[1], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[5])},
    {"course": course_ids[0], "student": student_ids[2], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[6])},
    {"course": course_ids[1], "student": student_ids[3], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[7])},
    {"course": course_ids[2], "student": student_ids[4], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[8])},
    {"course": course_ids[0], "student": student_ids[5], "enrollment_date": datetime(2025, 8, 25), "status": "ACTIVE", **audit(user_ids[9])}
])

# --- Academic Semesters ---
semester_ids = semesters.insert_many([
    {
        "semester_code": "2023/2024-1",
        "semester_name": "Academic Year 2023/2024 - Semester 1",
        "start_date": datetime(2023, 9, 1),
        "end_date": datetime(2024, 1, 15),
        "status": "COMPLETED",
        **audit(user_ids[1])
    },
    {
        "semester_code": "2023/2024-2",
        "semester_name": "Academic Year 2023/2024 - Semester 2",
        "start_date": datetime(2024, 2, 1),
        "end_date": datetime(2024, 6, 15),
        "status": "COMPLETED",
        **audit(user_ids[1])
    },
    {
        "semester_code": "2024/2025-1",
        "semester_name": "Academic Year 2024/2025 - Semester 1",
        "start_date": datetime(2024, 9, 1),
        "end_date": datetime(2025, 1, 15),
        "status": "COMPLETED",
        **audit(user_ids[1])
    },
    {
        "semester_code": "2024/2025-2",
        "semester_name": "Academic Year 2024/2025 - Semester 2",
        "start_date": datetime(2025, 2, 1),
        "end_date": datetime(2025, 6, 15),
        "status": "COMPLETED",
        **audit(user_ids[1])
    },
    {
        "semester_code": "2025/2026-1",
        "semester_name": "Academic Year 2025/2026 - Semester 1",
        "start_date": datetime(2025, 9, 1),
        "end_date": datetime(2026, 1, 15),
        "status": "ACTIVE",  # Current semester
        **audit(user_ids[1])
    },
    {
        "semester_code": "2025/2026-2",
        "semester_name": "Academic Year 2025/2026 - Semester 2",
        "start_date": datetime(2026, 2, 1),
        "end_date": datetime(2026, 6, 15),
        "status": "UPCOMING",
        **audit(user_ids[1])
    }
]).inserted_ids

# --- Exams (open-ended) end-to-end ---
exam_id = exams.insert_one({
    "title": "Midterm Software Testing",
    "duration": 90,
    "status": "SCHEDULED",
    "academic_semester": "2025/2026-1",
    **audit(user_ids[3])
}).inserted_id

sched_id = exam_schedules.insert_one({
    "exam": exam_id,
    "date": datetime(2025, 10, 30, 0, 0, 0),
    "time": "10:00",
    "venue": "Hall A",
    **audit(user_ids[3])
}).inserted_id

invigilators.insert_one({
    "invigilator": educator_ids[0], "exam_schedule": sched_id, "assigned_date": datetime(2025, 10, 1),
    **audit(user_ids[3])
})

exam_students.insert_many([
    {"exam": exam_id, "student": student_ids[0], "attendance": "PRESENT", "attendanceTimestamp": str(datetime(2025, 10, 30, 9, 55)), "enrollment_date": datetime(2025, 9, 15), **audit(user_ids[4])},
    {"exam": exam_id, "student": student_ids[1], "attendance": "PRESENT", "attendanceTimestamp": str(datetime(2025, 10, 30, 9, 57)), "enrollment_date": datetime(2025, 9, 15), **audit(user_ids[5])}
])

pause_exams.insert_one({
    "exam_student": {"exam": exam_id, "student": student_ids[1]},
    "paused_by": educator_ids[0],
    "reason": "Network issue",
    "pause_timestamp": datetime(2025, 10, 30, 10, 30),
    **audit(user_ids[2])
})

exam_chats.insert_one({
    "exam": exam_id, "student": student_ids[0], "educator": educator_ids[0],
    "content": "Clarify Q2 wording?", "timestamp": datetime(2025, 10, 30, 10, 10), **audit(user_ids[4])
})

exam_sub_id = exam_submissions.insert_one({
    "exam": exam_id, "student": student_ids[0], "submission_date": datetime(2025, 10, 30, 11, 35), **audit(user_ids[4])
}).inserted_id

exam_results.insert_one({
    "exam": exam_id, "student": student_ids[0], "marks": 85, "grade": "A", "recorded_date": datetime(2025, 10, 31, 9, 0), "status": "FINALIZED", **audit(user_ids[3])
})

# --- Question Bank (OPEN-ENDED for exams) + Exam Question Set + Minimal Bridge ---
open_q_ids = questions.insert_many([
    {
        "question": "Explain the difference between verification and validation in software engineering with an example.",
        "marks": 10,
        "educator": educator_ids[0],
        "course": course_ids[1],
        "model_answer": "Verification checks we built the product right (meets spec); validation checks we built the right product (meets user needs). Example: code review vs. UAT.",
        "rubric": "Defines both terms (4), contrasts focus (4), gives example (2).",
        "created_date": datetime(2025, 9, 1, 10, 0),
        **audit(user_ids[2])
    },
    {
        "question": "Describe the steps of a basic threat modeling process (e.g., STRIDE) for a web application login flow.",
        "marks": 12,
        "educator": educator_ids[0],
        "course": course_ids[2],
        "model_answer": "Identify assets, decompose login flow, enumerate threats (STRIDE), rate risks, propose mitigations (e.g., MFA, rate limiting, secure session).",
        "rubric": "Covers steps (6), applies to login flow (4), at least two mitigations (2).",
        "created_date": datetime(2025, 9, 10, 9, 15),
        **audit(user_ids[2])
    }
]).inserted_ids

exam_id_with_qset = exams.insert_one({
    "title": "Final Exam - Testing & Security",
    "duration": 120,
    "status": "SCHEDULED",
    "academic_semester": semester_ids[4],
    **audit(user_ids[2])
}).inserted_id

sched_id_qset = exam_schedules.insert_one({
    "exam": exam_id_with_qset,
    "date": datetime(2025, 11, 15, 0, 0, 0),
    "time": "14:00",
    "venue": "Hall B",
    **audit(user_ids[2])
}).inserted_id

invigilators.insert_one({
    "invigilator": educator_ids[0],
    "exam_schedule": sched_id_qset,
    "assigned_date": datetime(2025, 10, 15),
    **audit(user_ids[2])
})

exam_students.insert_many([
    {"exam": exam_id_with_qset, "student": student_ids[0], "attendance": "PRESENT", "attendanceTimestamp": str(datetime(2025, 11, 15, 13, 55)), "enrollment_date": datetime(2025, 10, 1), **audit(user_ids[4])},
    {"exam": exam_id_with_qset, "student": student_ids[1], "attendance": "PRESENT", "attendanceTimestamp": str(datetime(2025, 11, 15, 13, 57)), "enrollment_date": datetime(2025, 10, 1), **audit(user_ids[5])},
    {"exam": exam_id_with_qset, "student": student_ids[2], "attendance": "ABSENT", "attendanceTimestamp": None, "enrollment_date": datetime(2025, 10, 1), **audit(user_ids[6])}
])

exam_sub_id_qset = exam_submissions.insert_one({
    "exam": exam_id_with_qset,
    "student": student_ids[0],
    "total_marks": 95,
    "submission_date": datetime(2025, 11, 15, 15, 50),
    **audit(user_ids[4])
}).inserted_id

exam_answers.insert_many([
    {
        "submission": exam_sub_id_qset,
        "question": open_q_ids[0],
        "answer": "Verification ensures the product is built correctly according to specifications, while validation ensures we built the right product that meets user needs. Example: Code review (verification) vs User Acceptance Testing (validation).",
        "marks_awarded": 10,
        "feedback": "Excellent explanation with clear example.",
        **audit(user_ids[4])
    },
    {
        "submission": exam_sub_id_qset,
        "question": open_q_ids[1],
        "answer": "STRIDE stands for Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. For login flow: identify assets (credentials, sessions), decompose flow, enumerate threats, rate risks, propose mitigations like MFA and rate limiting.",
        "marks_awarded": 10,
        "feedback": "Great coverage of STRIDE with practical application.",
        **audit(user_ids[4])
    }
])

# --- Link questions directly to exams using exam_questions bridge table ---
exam_questions = db['exam_questions']

# Update the existing exam_id_with_qset to include exam fields
db['exams'].update_one(
    {'_id': exam_id_with_qset},
    {'$set': {
        'course': open_q_ids and db['questions'].find_one({'_id': open_q_ids[0]}).get('course') or course_ids[0],
        'educator': educator_ids[0],
        'exam_date': '2025-11-15',
        'exam_start_time': '14:00',
        'exam_end_time': '16:00',
        'total_marks': 0
    }}
)

# Link the open questions directly to the exam
order_idx = 1
for qid in open_q_ids:
    exam_questions.insert_one({
        'exam': exam_id_with_qset,
        'question': qid,
        'order_index': order_idx,
        'section': 'A',
        'marks_override': None,
        'question_text_override': None,
        'model_answer_override': None,
        'rubric_override': None,
        'snapshot': None,
        'last_modification_time': datetime.now(),
        'last_modification_user_id': educator_ids[0],
        'creation_time': datetime.now(),
        'is_active': True,
        'is_deleted': False
    })
    order_idx += 1


exam_sub_id_qset2 = exam_submissions.insert_one({
    "exam": exam_id_with_qset,
    "student": student_ids[1],
    "total_marks": None,
    "submission_date": datetime(2025, 11, 15, 15, 55),
    **audit(user_ids[5])
}).inserted_id

exam_answers.insert_many([
    {
        "submission": exam_sub_id_qset2,
        "question": open_q_ids[0],
        "answer": "Verification and validation are both important quality assurance activities...",
        "marks_awarded": None,
        "feedback": "",
        **audit(user_ids[5])
    },
    {
        "submission": exam_sub_id_qset2,
        "question": open_q_ids[1],
        "answer": "STRIDE is a threat modeling framework...",
        "marks_awarded": None,
        "feedback": "",
        **audit(user_ids[5])
    }
])


exam_results.insert_many([
    {
        "exam": exam_id_with_qset,
        "student": student_ids[0],
        "score": 20,
        "total_marks": 20,
        "grade": "A",
        "grade_point": 4.0,
        "recorded_date": datetime(2025, 11, 16, 10, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_with_qset,
        "student": student_ids[1],
        "score": 17,
        "total_marks": 20,
        "grade": "B",
        "grade_point": 3.0,
        "recorded_date": datetime(2025, 11, 16, 10, 30),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_with_qset,
        "student": student_ids[3],
        "score": 14,
        "total_marks": 20,
        "grade": "C",
        "grade_point": 2.0,
        "recorded_date": datetime(2025, 11, 16, 11, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_with_qset,
        "student": student_ids[4],
        "score": 11,
        "total_marks": 20,
        "grade": "D",
        "grade_point": 1.0,
        "recorded_date": datetime(2025, 11, 16, 11, 30),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_with_qset,
        "student": student_ids[5],
        "score": 8,
        "total_marks": 20,
        "grade": "F",
        "grade_point": 0.0,
        "recorded_date": datetime(2025, 11, 16, 12, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    }
])

exam_id_prev_sem = exams.insert_one({
    "title": "Midterm Exam - Testing (2024/2025-2)",
    "duration": 120,
    "status": "COMPLETED",
    "academic_semester": semester_ids[3],
    **audit(user_ids[2])
}).inserted_id

exam_results.insert_many([
    {
        "exam": exam_id_prev_sem,
        "student": student_ids[0],
        "score": 18,
        "total_marks": 20,
        "grade": "A",
        "grade_point": 4.0,
        "recorded_date": datetime(2025, 3, 15, 10, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_prev_sem,
        "student": student_ids[1],
        "score": 15,
        "total_marks": 20,
        "grade": "B",
        "grade_point": 3.0,
        "recorded_date": datetime(2025, 3, 15, 10, 30),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_prev_sem,
        "student": student_ids[3],
        "score": 12,
        "total_marks": 20,
        "grade": "C",
        "grade_point": 2.0,
        "recorded_date": datetime(2025, 3, 15, 11, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_prev_sem,
        "student": student_ids[4],
        "score": 10,
        "total_marks": 20,
        "grade": "D",
        "grade_point": 1.0,
        "recorded_date": datetime(2025, 3, 15, 11, 30),
        "status": "FINALIZED",
        **audit(user_ids[2])
    }
])

exam_id_older_sem = exams.insert_one({
    "title": "Final Exam - Testing (2024/2025-1)",
    "duration": 90,
    "status": "COMPLETED",
    "academic_semester": semester_ids[2],
    **audit(user_ids[2])
}).inserted_id

exam_results.insert_many([
    {
        "exam": exam_id_older_sem,
        "student": student_ids[0],
        "score": 8,
        "total_marks": 10,
        "grade": "B",
        "grade_point": 3.0,
        "recorded_date": datetime(2025, 1, 10, 10, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_older_sem,
        "student": student_ids[1],
        "score": 6,
        "total_marks": 10,
        "grade": "C",
        "grade_point": 2.0,
        "recorded_date": datetime(2025, 1, 10, 10, 30),
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "exam": exam_id_older_sem,
        "student": student_ids[3],
        "score": 5,
        "total_marks": 10,
        "grade": "D",
        "grade_point": 1.0,
        "recorded_date": datetime(2025, 1, 10, 11, 0),
        "status": "FINALIZED",
        **audit(user_ids[2])
    }
])

course_results.insert_many([
    {
        "student": student_ids[0], 
        "course": course_ids[0],  
        "academic_semester": semester_ids[3],
        "components": [
            {"name": "Coursework", "percentage": 30, "score": 27, "max_score": 30, "grade": "A"},
            {"name": "Midterm Exam", "percentage": 30, "score": 25, "max_score": 30, "grade": "B+"},
            {"name": "Final Exam", "percentage": 40, "score": 38, "max_score": 40, "grade": "A"}
        ],
        "final_grade": "A",
        "final_percentage": 90.0,
        "grade_point": 4.0,
        "credit_hours": 3,
        "entered_by": educator_ids[0],
        "entered_at": datetime(2025, 6, 15, 10, 0),
        "remarks": "Excellent performance throughout the semester",
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "student": student_ids[0],
        "course": course_ids[1], 
        "academic_semester": semester_ids[3], 
        "components": [
            {"name": "Assignments", "percentage": 20, "score": 18, "max_score": 20, "grade": "A"},
            {"name": "Midterm Exam", "percentage": 30, "score": 27, "max_score": 30, "grade": "A"},
            {"name": "Final Exam", "percentage": 40, "score": 36, "max_score": 40, "grade": "A"},
            {"name": "Lab Work", "percentage": 10, "score": 9, "max_score": 10, "grade": "A"}
        ],
        "final_grade": "A",
        "final_percentage": 90.0,
        "grade_point": 4.0,
        "credit_hours": 3,
        "entered_by": educator_ids[0],
        "entered_at": datetime(2025, 6, 15, 11, 0),
        "remarks": "Outstanding test coverage and analysis skills",
        "status": "FINALIZED",
        **audit(user_ids[2])
    },
    {
        "student": student_ids[0],
        "course": course_ids[2],
        "academic_semester": semester_ids[3],
        "components": [
            {"name": "Security Project", "percentage": 30, "score": 27, "max_score": 30, "grade": "A"},
            {"name": "Midterm Exam", "percentage": 30, "score": 24, "max_score": 30, "grade": "B"},
            {"name": "Final Exam", "percentage": 40, "score": 36, "max_score": 40, "grade": "A"}
        ],
        "final_grade": "A",
        "final_percentage": 87.0,
        "grade_point": 4.0,
        "credit_hours": 3,
        "entered_by": educator_ids[1],
        "entered_at": datetime(2025, 6, 16, 9, 0),
        "remarks": "Strong grasp of security principles",
        "status": "FINALIZED",
        **audit(user_ids[3])
    },

    {
        "student": student_ids[0],
        "course": course_ids[1], 
        "academic_semester": semester_ids[4],
        "components": [
            {"name": "Assignments", "percentage": 20, "score": 20, "max_score": 20, "grade": "A"},
            {"name": "Midterm Exam", "percentage": 30, "score": 30, "max_score": 30, "grade": "A"},
            {"name": "Final Exam", "percentage": 40, "score": None, "max_score": 40, "grade": None},
            {"name": "Lab Work", "percentage": 10, "score": 10, "max_score": 10, "grade": "A"}
        ],
        "final_grade": None, 
        "final_percentage": None,
        "grade_point": None,
        "credit_hours": 3,
        "entered_by": educator_ids[0],
        "entered_at": datetime(2025, 11, 5, 14, 0),
        "remarks": "In progress - final exam pending",
        "status": "IN_PROGRESS",
        **audit(user_ids[2])
    }
])


student_semester_records.insert_many([
    {
        "student": student_ids[0],
        "academic_semester": semester_ids[3], 
        "semester_gpa": 3.67,
        "semester_credits": 9,
        "semester_grade_points": 33.0,
        "cumulative_gpa": 3.67,
        "total_credits": 9,
        "total_grade_points": 33.0,
        "course_grades": [
            {
                "course": course_ids[0],
                "course_name": "Software Engineering",
                "credits": 3,
                "grade": "A",
                "grade_point": 4.0
            },
            {
                "course": course_ids[1],
                "course_name": "Software Testing",
                "credits": 3,
                "grade": "B",
                "grade_point": 3.0
            },
            {
                "course": course_ids[2],
                "course_name": "Software Security",
                "credits": 3,
                "grade": "A",
                "grade_point": 4.0
            }
        ],
        "status": "FINALIZED",
        "finalized_date": datetime(2025, 6, 30),
        "finalized_by": educator_ids[0],
        **audit(user_ids[2], created=datetime(2025, 6, 30))
    },
    {
        "student": student_ids[1],
        "academic_semester": "2024/2025-2",
        "semester_gpa": 3.33,
        "semester_credits": 6,
        "semester_grade_points": 20.0,
        "cumulative_gpa": 3.33,
        "total_credits": 6,
        "total_grade_points": 20.0,
        "course_grades": [
            {
                "course": course_ids[1],
                "course_name": "Software Testing",
                "credits": 3,
                "grade": "A",
                "grade_point": 4.0
            },
            {
                "course": course_ids[2],
                "course_name": "Software Security",
                "credits": 3,
                "grade": "B",
                "grade_point": 3.0
            }
        ],
        "status": "FINALIZED",
        "finalized_date": datetime(2025, 6, 30),
        "finalized_by": educator_ids[0],
        **audit(user_ids[2], created=datetime(2025, 6, 30))
    }
])

# --- Incidents ---
incidents.insert_one({
    "exam": exam_id, "student": student_ids[1], "reported_by": educator_ids[0],
    "details": "Potential collab observed; verified as false alarm.",
    "timestamp": datetime(2025, 10, 30, 10, 40),
    **audit(user_ids[2])
})

# ---- Recommended indexes (run once) ----
# Users
users.create_index("email", unique=True)
users.create_index("role")

# Courses
courses.create_index([("name", 1)])

# Open-ended questions (for exams)
questions.create_index([("course", 1), ("educator", 1)])

# Exam runtime data
exam_schedules.create_index([("exam", 1)])
exam_students.create_index([("exam", 1), ("student", 1)])
exam_results.create_index([("exam", 1), ("student", 1)])
invigilators.create_index([("exam_schedule", 1)])

# Student semester records (GPA/CGPA history)
student_semester_records.create_index([("student", 1), ("academic_semester", 1)], unique=True)
student_semester_records.create_index([("status", 1)])
student_semester_records.create_index([("student", 1), ("finalized_date", -1)])

# Course results (final course grades)
course_results.create_index([("student", 1), ("course", 1), ("academic_semester", 1)], unique=True)
course_results.create_index([("course", 1), ("academic_semester", 1), ("status", 1)])
course_results.create_index([("student", 1), ("academic_semester", 1)])
course_results.create_index([("status", 1)])

# Academic semesters
semesters.create_index([("semester_code", 1)], unique=True)
semesters.create_index([("status", 1)])
semesters.create_index([("start_date", 1)])

print("\n✅ Done seeding database!")
print(f"\n📝 Sample Educator ID (use this in exam.html): {educator_ids[0]}")
print(f"📝 Sample Exam ID: {exam_id_with_qset}")