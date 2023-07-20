from flask import Flask, render_template, request
from data.papers import get_papers_data


app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        keyword = request.form["keyword"]
        # APIにキーワードと表示する論文数を渡す
        papers_data = get_papers_data(keyword)
        print(keyword)

        if len(papers_data) != 0:  
            return render_template('index.html', papers=papers_data, keys=papers_data[0].keys())
    
    return render_template('index.html')

if __name__ == "__main__":
    # app.run(debug=False, host="0.0.0.0",port=81)
    app.run(debug=False, host='localhost')