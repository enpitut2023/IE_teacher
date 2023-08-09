from flask import Flask, render_template, request, url_for, redirect
from data.call_meta_paper import PaperCaller
from urllib import parse


app = Flask(__name__)
pc = PaperCaller()


"""
KEYWORD_SEARCH_GET_LIMIT

MAX: 100
"""
KEYWORD_SEARCH_GET_LIMIT = 100

PAPER_IDS_POST_LIMIT = 500

REFERENCE_PAPERS_GET_LIMIT = 500

GET_LIMIT_USING_FOR_LOOP = 10



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
  
  keyword = parse.unquote(keyword)
  papers_data = pc.get_papers_by_keyword(keyword, limit=KEYWORD_SEARCH_GET_LIMIT)
  
  if len(papers_data) != 0:
    keys = papers_data[0].keys()
    return render_template("root_nontable.html", n=len(keys), papers=papers_data, keys=keys, keyword=keyword)
  else:
    return render_template("notfound.html", keyword=keyword)

@app.route("/papers/<string:paperId>", methods=["GET", "POST"])
def papers(paperId):
  if request.method == 'POST':
    keyword = request.form["keyword"]

    return redirect(url_for("root" , keyword = keyword))
  
  paperIds=paperId.split('-')
  main_paper_id=paperIds[-1]

  main_data = pc.get_paper_by_paperId(main_paper_id)
  reference_paperIds = pc.get_reference_papers_ids_by_main_paper_id(main_paper_id, REFERENCE_PAPERS_GET_LIMIT)
  papers_data = pc.get_papers_by_paperIds(paperIDs=reference_paperIds, limit=PAPER_IDS_POST_LIMIT)
  # papers_data=pc.get_papers_by_paperIds_using_for_loop(paperIDs=reference_paperIds, limit=GET_LIMIT_USING_FOR_LOOP)

  """
  POSTが死んだら使う

  papers_data=pc.get_papers_by_paperIds_using_for_loop(paperIDs=reference_paperIds, limit=GET_LIMIT_USING_FOR_LOOP)
  """

  if len(papers_data) != 0:
    keys = papers_data[0].keys()
    return render_template("papers.html", n=len(keys), main_paper=main_data, papers=papers_data, keys=keys,
                           paperIds=paperId)
  else:
    
    return redirect(url_for("result", paperId = paperId))

@app.route("/result/<string:paperId>", methods=["GET", "POST"])
def result(paperId):
  if request.method == 'POST':
    keyword = request.form["keyword"]

    return redirect(url_for("root" , keyword = keyword))
  
  paperIds=paperId.split('-')

  papers_data=pc.get_papers_by_paperIds(paperIds, PAPER_IDS_POST_LIMIT)
  # papers_data=pc.get_papers_by_paperIds_using_for_loop(paperIDs=paperIds, limit=GET_LIMIT_USING_FOR_LOOP)

  """
  POSTが死んだら使う

  papers_data=pc.get_papers_by_paperIds_using_for_loop(paperIds,GET_LIMIT_USING_FOR_LOOP)
  """

  return render_template("result.html", papers=papers_data)

if __name__ == "__main__":
  # app.run(debug=False, host="0.0.0.0", port=81)
  app.run(debug=True, host='localhost')

