from flask import Flask, render_template, request, redirect, url_for, session
import json, sqlite3

app = Flask(__name__)
app.secret_key = 'admin'
level_scripts = []

DATABASE = 'database.db'

with open('./static/levels/levels.json', 'r') as infile:
    level_scripts = json.load(infile)
    infile.close()

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, completed_levels INTEGER, completed_difficulty INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS score (username TEXT PRIMARY KEY, score INTEGER, level_number INTEGER, level_difficulty INTEGER)')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    if(request.method == 'POST'):
        username = request.form['name']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password, completed_levels, completed_difficulty) VALUES (?, ?, ?, ?)', (username, password, 0, 0))
                conn.commit()
                return redirect(url_for('levels', name=username))
            except sqlite3.IntegrityError:
                #For when username is in DB
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()

                if user and user['password'] == password:
                    return redirect(url_for('levels', name=username))
                else:
                    return "Invalud username or password.", 400
    else:
        return render_template('./login.html')
    
@app.route('/levels', methods=['GET', 'POST'])
def levels():
    if(request.method == 'POST'):
        level = int(request.form['level'])
        difficulty = int(request.form['difficulty'])
        name = str(request.form['name'])
        session['current_level'] = level
        session['current_difficulty'] = difficulty
        data = {'script':level_scripts[level-1], 'difficulty':difficulty, 'name':name}
        return render_template('./index.html', data=data)
    else:
        if(request.args['name'] is None):
            return redirect(url_for('index'))
        return render_template('./levelselect.html', data={'name':request.args['name']})

@app.route('/score', methods=['GET', 'POST'])
def score():
    score = request.json['score']
    name = request.json['name']
    level_number = int(session.get('current_level'))
    difficulty = session.get('current_difficulty')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT score FROM score WHERE user_username = ? AND level_number = ?', (name, level_number))
        existing_score = cursor.fetchone()

        if existing_score is None:
            # If no existing score, insert the new score
            cursor.execute('''
                INSERT INTO score (user_username, score, level_number, level_difficulty)
                VALUES (?, ?, ?, ?)
                ''', (name, score, level_number, session.get('current_difficulty')))
        elif score > existing_score[0]:
            # If the new score is greater than the existing score, update it
            cursor.execute('''
                UPDATE score SET score = ? WHERE user_username = ? AND level_number = ?
                ''', (score, name, level_number))
        
        cursor.execute('SELECT completed_levels FROM users WHERE username = ?', (name,))
        completed_levels = cursor.fetchone()[0]

        if level_number == completed_levels + 1:
            cursor.execute('UPDATE users SET completed_levels = ? WHERE username = ?', (level_number, name))
        
        conn.commit()

    return render_template('./score_report.html', data={'name':name, 'score':score})

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)
