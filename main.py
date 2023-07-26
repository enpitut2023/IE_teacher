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

    return redirect(url_for("root" , keyword = keyword))

  return render_template('index.html')

@app.route("/root/<string:keyword>", methods=["GET", "POST"])
def root(keyword):
  if request.method == 'POST':
    if "keyword" in request.form.keys():
      keyword = request.form["keyword"]

      return redirect(url_for("root" , keyword = keyword))
    
    elif "paperId" in request.form.keys():
      paperId = request.form["paperId"]
      return redirect(url_for("papers" , paperId = paperId))

  num_get=1000
  papers_data = pc.get_metainfo_from_keyword(keyword, num_get, num_get)
  
  if len(papers_data) != 0:
    keys = papers_data[0].keys()
    return render_template("root_nontable.html", n=len(keys), papers=papers_data, keys=keys, keyword=keyword)
    # return render_template("root.html", n=len(keys), papers=papers_data, keys=keys)
  else:
    return render_template("notfound.html")

@app.route("/papers/<string:paperId>", methods=["GET", "POST"])
def papers(paperId):
  if request.method == 'POST':
    keyword = request.form["keyword"]

    return redirect(url_for("root" , keyword = keyword))
  
  num_get=1000
  paperIds=paperId.split('-')
  for id in paperIds:
    print(id)
  targ_paper=paperIds[-1]
  main_data, papers_data = pc.get_metainfo_from_paperId(targ_paper, num_get, num_get)

  if len(papers_data) != 0:
    keys = papers_data[0].keys()
    # return render_template("papers_nontable.html", n=len(keys), main_paper=main_data, papers=papers_data, keys=keys,
    #                        paperIds=paperId)
    return render_template("papers.html", n=len(keys), main_paper=main_data, papers=papers_data, keys=keys,
                           paperIds=paperId)
  else:
    # papers_data = pc.get_metainfo_from_paperIds(paperIds)

    # # return render_template("result_nontable.html", papers=papers_data)
    # return render_template("result.html", papers=papers_data)
    return redirect(url_for("result", paperId = paperId))

@app.route("/result/<string:paperId>", methods=["GET", "POST"])
def result(paperId):
  if request.method == 'POST':
    keyword = request.form["keyword"]

    return redirect(url_for("root" , keyword = keyword))
  
  paperIds=paperId.split('-')
  # for id in paperIds:
  #   print(id)
  papers_data = pc.get_metainfo_from_paperIds(paperIds)

  # return render_template("result_nontable.html", papers=papers_data)
  return render_template("result.html", papers=papers_data)

"""
Localでhtmlを表示する場合はhost="localhost"
Replit上でhtmlを表示する場合はhost="0.0.0.0",port=81を
使用する
"""
if __name__ == "__main__":
  # app.run(debug=False, host="0.0.0.0", port=81)
  app.run(debug=True, host='localhost')
