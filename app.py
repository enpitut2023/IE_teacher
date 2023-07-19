from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello 情報工学先生!!'

if __name__ == "__main__":
    app.run(debug=True)