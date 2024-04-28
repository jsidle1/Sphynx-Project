from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
        cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, completed_levels INTEGER DEFAULT 0, completed_difficulty INTEGER DEFAULT 0, total_score INTEGER DEFAULT 0)')
        cursor.execute('CREATE TABLE IF NOT EXISTS score (ID INTEGER PRIMARY KEY autoincrement, user_username TEXT, score INTEGER DEFAULT 0, level_number INTEGER DEFAULT 0, level_difficulty INTEGER DEFAULT 0)')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    data = {"err_msg":""}
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
                    data["err_msg"] = f"Invalid password for account: {username}"
                    return render_template('./login.html', data=data)
    else:
        return render_template('./login.html', data=data)
    
@app.route('/levels', methods=['GET', 'POST'])
def levels():

    if(request.method == 'POST'):
        level = int(request.form['level'])
        difficulty = int(request.form['difficulty'])
        name = str(request.form['name'])
        session['current_level'] = level
        session['current_difficulty'] = difficulty

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT completed_levels from users WHERE username=?', (name,))
            completed_levels = cursor.fetchone()[0]

            if(level > completed_levels + 1):
                return redirect(url_for('levels', name=name))
            if(difficulty > 1 and level > completed_levels):
                return redirect(url_for('levels', name=name))

        data = {'script':level_scripts[level-1], 'difficulty':difficulty, 'name':name, 'level':level}
        return render_template('./index.html', data=data)
    else:
        if(request.args['name'] is None):
            return redirect(url_for('index'))
        
        name = request.args['name']
        level_tags = []
        total_score = 0
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT completed_levels from users WHERE username=?', (name,))
            completed_levels = cursor.fetchone()[0]
            cursor.execute('SELECT completed_difficulty from users WHERE username=?', (name,))
            completed_difficulty = cursor.fetchone()[0]
            cursor.execute('SELECT total_score from users WHERE username=?', (name,))
            total_score = cursor.fetchone()[0]

            for i in range(1,4):
                if(i - completed_levels < 1):
                    level_tags.append('level-completed')
                elif(i - completed_levels == 1):
                    level_tags.append('level-unlocked')
                else:
                    level_tags.append('level-locked')
            for i in range(1,4):
                if(i - completed_levels <= 0):
                    if(i - completed_difficulty < 1):
                        level_tags.append('level-completed')
                    else:
                        level_tags.append('level-unlocked')
                else:
                    level_tags.append('level-locked')

        return render_template('./levelselect.html', data={'name':name, 'level_tags':level_tags, 'score':str(total_score)})

@app.route('/score', methods=['GET', 'POST'])
def score():
    score = request.json['score']
    name = request.json['name']
    level_number = request.json['level']
    level_difficulty = request.json['difficulty']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT score FROM score WHERE user_username = ? AND level_number = ? AND level_difficulty = ?', (name, level_number, level_difficulty))
        existing_score = cursor.fetchone()

        if existing_score is None:
            # If no existing score, insert the new score
            cursor.execute('''
                INSERT INTO score (user_username, score, level_number, level_difficulty)
                VALUES (?, ?, ?, ?)
                ''', (name, score, level_number, level_difficulty))
            
            cursor.execute('SELECT total_score FROM users where username = ?', (name,))
            total_score = cursor.fetchone()[0]
            if total_score is not None:
                score = total_score + score

            cursor.execute('UPDATE users SET total_score = ? WHERE username = ?', (score, name,))
        elif score > existing_score[0]:
            # If the new score is greater than the existing score, update it
            cursor.execute('''
                UPDATE score SET score = ? WHERE user_username = ? AND level_number = ? AND level_difficulty = ?
                ''', (score, name, level_number, level_difficulty))
            cursor.execute('SELECT total_score FROM users where username = ?', (name,))
            new_score = cursor.fetchone()[0] + (score - existing_score[0])
            cursor.execute('UPDATE users SET total_score = ? WHERE username = ?', (new_score, name,))
        
        cursor.execute('SELECT completed_levels FROM users WHERE username = ?', (name,))
        completed_levels = cursor.fetchone()[0]

        if level_number > completed_levels:
            cursor.execute('UPDATE users SET completed_levels = ? WHERE username = ?', (level_number, name))

        cursor.execute('SELECT completed_difficulty FROM users WHERE username = ?', (name,))
        completed_difficulty = cursor.fetchone()[0]

        if completed_levels >= level_number and 2 == level_difficulty and completed_difficulty < level_number:
            cursor.execute('UPDATE users SET completed_difficulty = ? WHERE username = ?', ((level_number), name))
        
        conn.commit()

    return render_template('./score_report.html', data={'name':name, 'score':score})

@app.route('/getscores', methods=['GET'])
def getscores():
    data = {
      "data":
        [{
          "Group": "Sphynx",
          "Title": "Top 5 Scores"
        }]
    }
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username,total_score FROM users ORDER BY total_score DESC')
        results = cursor.fetchall()[:5]
        for res in results:
            data['data'][0][res[0]] = res[1]

    return jsonify(data)

if __name__ == "__main__":
    init_db()
    app.run(port=8000, debug=True)
