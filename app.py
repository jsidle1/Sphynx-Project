from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)
level_scripts = []

with open('./static/levels/levels.json', 'r') as infile:
    level_scripts = json.load(infile)
    infile.close()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():

    if(request.method == 'POST'):
        name = request.form['name']
        return redirect(url_for('levels', name=name))
    else:
        return render_template('./login.html')
    
@app.route('/levels', methods=['GET', 'POST'])
def levels():
    if(request.method == 'POST'):
        level = int(request.form['level'])
        difficulty = int(request.form['difficulty'])
        name = str(request.form['name'])
        data = {'script':level_scripts[level-1], 'difficulty':difficulty, 'name':name, 'level':level}
        return render_template('./index.html', data=data)
    else:
        if(request.args['name'] is None):
            return redirect(url_for('index'))
        return render_template('./levelselect.html', data={'name':request.args['name']})

@app.route('/score', methods=['GET', 'POST'])
def score():
    score = request.json['score']
    name = request.json['name']
    return render_template('./score_report.html', data={'name':name, 'score':score})

if __name__ == "__main__":
    app.run(port=8000, debug=True)