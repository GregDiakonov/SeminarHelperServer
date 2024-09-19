from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import redis
import json
from waitress import serve


class Seminar:
    def __init__(self, number):
        self.number = number
        self.students = []

    def findStudent(self, student_name):
        for student in self.students:
            if student.name == student_name:
                return student
            
        return None
    
class Student:
    def __init__(self, name      ):
        self.name = name
        self.position = 0

app = Flask(__name__)
CORS(app)

database = redis.Redis(host="localhost", port=6379, db=0)
registeredSeminars = 0

seminars = []

@app.route('/')
def home():
    return "Welcome to the Seminar Helper Server. Use other handles."

# Регистрация нового семинара.
@app.route('/sem', methods=['POST'])
def newSeminar():
    try:
        global registeredSeminars
        newSem = Seminar(registeredSeminars)
        seminars.append(newSem)

        registeredSeminars += 1

        return str(registeredSeminars)
    except:
        return '-1'

# Регистрация нового студента.
@app.route('/sem/new/<int:sem_number>/<string:student_name>', methods=['POST'])
def newStudent(student_name, sem_number):
    try:
        newStudent = Student(student_name)

        seminars[sem_number - 1].students.append(newStudent)

        database.set(student_name, "")

        return "Good", 200
    except:
        return "Bad", 500

# Посмотреть позиции студентов
@app.route('/sem/<int:sem_number>', methods=['GET'])
def studentPositions(sem_number):
    try:
        positions = {}

        for student in seminars[sem_number - 1].students:
            positions[student.name] = student.position

        return jsonify(positions)
    except:
        return "Bad", 500

# Либо запись, либо чтение текстов того или иного студента.
@app.route('/sem/<int:sem_number>/<string:student_name>', methods=['GET', 'POST'])
def handleStudent(student_name, sem_number):
    if request.method == 'GET':
        try:
            task_texts = database.get('student_name')
            return task_texts           
        except:
            return "Bad", 500
        
    if request.method == 'POST':
        try:
            sent_data = request.get_json()

            sent_position = sent_data['position']
            sent_texts = sent_data['texts']

            database.set(student_name, sent_texts)
            seminars[sem_number - 1].findStudent(student_name).position = sent_position

            return "Good", 200
        except:
            return "Bad", 500

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
