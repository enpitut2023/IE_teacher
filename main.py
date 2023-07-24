import sqlite3
from flask import Flask, render_template, request, url_for, redirect, g
from data.papers import get_papers_data
from data.call_meta_paper import PaperCaller

app = Flask(__name__)
pc = PaperCaller()


def get_db():
    if 'db' not in g:
         g.db = sqlite3.connect('TestDB.db')
    return g.db

@app.route('/', methods=["GET", "POST"])
def index():
  if request.method == 'POST':
    keyword = request.form["keyword"]

    return redirect(url_for("papers" , keyword = keyword))

  return render_template('index.html')

@app.route("/papers/<string:keyword>", methods=["GET", "POST"])
def papers(keyword):
  num_get=1000
  _, papers_data = pc.get_metainfo_from_title(keyword, num_get, num_get)

  if len(papers_data) != 0:
    keys = papers_data[0].keys()
    return render_template("papers.html", n=len(keys), papers=papers_data, keys=keys)
  
  return render_template("papers.html")


"""
Localでhtmlを表示する場合はhost="localhost"
Replit上でhtmlを表示する場合はhost="0.0.0.0",port=81を
使用する
"""
if __name__ == "__main__":
  # app.run(debug=False, host="0.0.0.0", port=81)
  app.run(debug=False, host='localhost')
