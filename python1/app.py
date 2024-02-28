from flask import Flask, render_template, request, redirect, url_for, session
import json
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Fungsi untuk menyimpan dan membaca data pengguna, kuis, dan materi pembelajaran ke/dari file JSON
def save_data():
    with open('data.json', 'w') as json_file:
        json.dump({'users': users_data, 'quiz': quiz_data, 'materials': learning_materials}, json_file)

def load_data():
    try:
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
            return data.get('users', {}), data.get('quiz', []), data.get('materials', [])
    except FileNotFoundError:
        return {}, [], []

def save_users_data():
    with open('data.json', 'w') as json_file:
        json.dump({'users': users_data, 'quiz': quiz_data, 'materials': learning_materials}, json_file)

def save_quiz_data():
    with open('quiz_data.json', 'w') as json_file:
        json.dump(quiz_data, json_file)

def save_learning_materials():
    with open('learning_materials.json', 'w') as json_file:
        json.dump(learning_materials, json_file)

# Load data saat aplikasi dimulai
users_data, quiz_data, learning_materials = load_data()

# Definisi data pengguna jika belum ada
if not users_data:
    users_data = {
        'admin': {'password': 'admin123', 'role': 'guru'},
        'student': {'password': 'student123', 'role': 'siswa'}
        # Tambahkan data pengguna lainnya jika diperlukan
    }

# Fungsi untuk menyimpan data kuis ke file JSON
def save_quiz_data():
    with open('quiz_data.json', 'w') as json_file:
        json.dump(quiz_data, json_file)

# Fungsi untuk menyimpan data materi pembelajaran ke file JSON
def save_learning_materials():
    with open('learning_materials.json', 'w') as json_file:
        json.dump(learning_materials, json_file)


# Data kuis
quiz_data = [
    {"question": "Apa fungsi dari perintah 'print' dalam Python?", "options": ["Menampilkan output", "Menerima input", "Melakukan perulangan", "Membuat fungsi"], "answer": "Menampilkan output"},
    {"question": "Apa hasil dari 3 * 4?", "options": ["5", "8", "10", "12"], "answer": "12"},
    # Tambahkan soal kuis lainnya jika diperlukan
]

# Data materi pembelajaran
learning_materials = [
    {"title": "Pengenalan Dasar Pemrograman Python", "content": "Python adalah bahasa pemrograman tingkat tinggi..."},
    # Tambahkan materi pembelajaran lainnya jika diperlukan
]

# Dictionary untuk menyimpan skor pengguna
user_scores = {}


@app.route('/')
def home():
    if 'username' in session:
        if session['role'] == 'guru':
            return redirect(url_for('guru_dashboard'))
        elif session['role'] == 'siswa':
            return redirect(url_for('siswa_dashboard'))
    return render_template('login.html')

# Fungsi login
def login_user(username, password):
    return username in users_data and password == users_data[username]['password']

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if login_user(username, password):
        session['username'] = username
        session['role'] = users_data[username]['role']
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='Username atau password salah')


@app.route('/guru/dashboard')
def guru_dashboard():
    if 'username' in session and session['role'] == 'guru':
        return render_template('guru_dashboard.html')
    else:
        return redirect(url_for('home'))

@app.route('/guru/delete_quiz', methods=['GET', 'POST'])
def delete_quiz():
    if 'username' in session and session['role'] == 'guru':
        if request.method == 'POST':
            question_to_delete = request.form['question_to_delete']

            # Implement logic to delete the quiz
            global quiz_data
            quiz_data = [quiz for quiz in quiz_data if quiz['question'] != question_to_delete]

            return redirect(url_for('guru_dashboard'))
        else:
            return render_template('delete_quiz.html')
    else:
        return redirect(url_for('home'))

@app.route('/guru/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session and session['role'] == 'guru':
        if request.method == 'POST':
            new_username = request.form['new_username']
            new_password = request.form['new_password']
            new_role = request.form['new_role']

            if new_username not in users_data:
                users_data[new_username] = {'password': new_password, 'role': new_role}
                save_users_data()  # Simpan data setelah perubahan
                return redirect(url_for('guru_dashboard'))
            else:
                return render_template('add_user.html', error='Username sudah ada')
        else:
            return render_template('add_user.html')
    else:
        return redirect(url_for('home'))


@app.route('/guru/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if 'username' in session and session['role'] == 'guru':
        if request.method == 'POST':
            question = request.form['question']
            options = request.form.getlist('options')
            answer = request.form['answer']

            quiz_data.append({"question": question, "options": options, "answer": answer})
            
            # Simpan data setelah menambahkan kuis
            save_data()
            
            return redirect(url_for('guru_dashboard'))
        else:
            return render_template('add_quiz.html')
    else:
        return redirect(url_for('home'))

@app.route('/guru/add_material', methods=['GET', 'POST'])
def add_material():
    if 'username' in session and session['role'] == 'guru':
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            learning_materials.append({"title": title, "content": content})
            
            # Simpan data setelah menambahkan materi
            save_data()
            
            return redirect(url_for('guru_dashboard'))
        else:
            return render_template('add_material.html')
    else:
        return redirect(url_for('home'))

    
@app.route('/siswa/dashboard')
def siswa_dashboard():
    if 'username' in session and session['role'] == 'siswa':
        return render_template('siswa_dashboard.html')
    else:
        return redirect(url_for('home'))


# Route untuk menampilkan soal kuis
@app.route('/quiz', methods=['GET', 'POST'])
def take_quiz():
    if 'username' in session and session['role'] == 'siswa':
        if request.method == 'GET':
            # Tampilkan soal kuis pertama
            question_index = 0
            return render_template('quiz_question.html', question=quiz_data[question_index], question_index=question_index)
        elif request.method == 'POST':
            # Tangani jawaban yang dikirim dan pindah ke soal berikutnya
            question_index = int(request.form['question_index'])
            user_answer = request.form['answer']

            # Simpan jawaban pengguna di sesi
            answer_key = f"user_answer_{question_index}"
            session[answer_key] = user_answer

            # Pindah ke soal berikutnya atau redirect ke halaman skor jika tidak ada lagi soal
            question_index += 1
            if question_index < len(quiz_data):
                return render_template('quiz_question.html', question=quiz_data[question_index], question_index=question_index)
            else:
                # Simpan data kuis ke file JSON
                save_quiz_data()
                return redirect(url_for('view_score'))
    else:
        return redirect(url_for('home'))

# Route untuk menampilkan skor
@app.route('/score')
def view_score():
    if 'username' in session and session['role'] == 'siswa':
        username = session['username']

        # Dapatkan skor untuk pengguna yang sedang login
        user_score = calculate_user_score(username)

        # Dapatkan jawaban yang sudah dijawab oleh pengguna
        user_answers = []  # Simpan jawaban dalam bentuk tuple (pertanyaan, jawaban pengguna, jawaban benar)
        for index, question in enumerate(quiz_data):
            answer_key = f"user_answer_{index}"
            if answer_key in session:
                user_answer = session[answer_key]
                correct_answer = question['answer']
                user_answers.append((question['question'], user_answer, correct_answer))

        # Simpan data kuis ke file Excel
        save_quiz_data_excel(username)

        return render_template('score.html', user_score=user_score, user_answers=user_answers)
    else:
        return redirect(url_for('home'))

# Fungsi untuk menghitung skor pengguna
def calculate_user_score(username):
    user_score = 0
    for index, question in enumerate(quiz_data):
        answer_key = f"user_answer_{index}"
        if answer_key in session:
            user_answer = session[answer_key]
            correct_answer = question['answer']
            if user_answer == correct_answer:
                user_score += 1

    # Simpan skor pengguna ke dalam dictionary user_scores
    user_scores[username] = user_score
    return user_score

def save_quiz_data_excel(username):
    quiz_responses = []

    for index, question in enumerate(quiz_data):
        answer_key = f"user_answer_{index}"
        if answer_key in session:
            user_answer = session[answer_key]
            correct_answer = question['answer']
            quiz_responses.append({
                'Username': username,
                'Quiz Number': index + 1,
                'Question': question['question'],
                'User Answer': user_answer,
                'Correct Answer': correct_answer
            })

    df = pd.DataFrame(quiz_responses)

    # Menyimpan DataFrame ke dalam file Excel
    excel_filename = f"quiz_responses_{username}.xlsx"
    df.to_excel(excel_filename, index=False)

# Route untuk menampilkan materi pembelajaran
@app.route('/materials')
def view_materials():
    if 'username' in session and session['role'] == 'siswa':
        return render_template('materials.html', learning_materials=learning_materials)
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)