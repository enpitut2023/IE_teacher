from flask import Flask, render_template
from data.papers import papers_data


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', papers=papers_data, keys=papers_data[0].keys())

if __name__ == "__main__":
    # app.run(debug=False, host="0.0.0.0",port=81)
    app.run(debug=False, host='localhost')