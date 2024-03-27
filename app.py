from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():

    if(request.method == 'POST'):
        return render_template('./levelselect.html')
    else:
        return render_template('./login.html')

@app.route('/game', methods=['GET'])
def game():
    return render_template('./index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)