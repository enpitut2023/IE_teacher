from flask import Flask, render_template, request
from data.papers import get_papers_data
from data.call_meta_paper import PaperCaller

app = Flask(__name__)
pc = PaperCaller()


@app.route('/', methods=["GET", "POST"])
def index():
  if request.method == 'POST':
    keyword = request.form["keyword"]
    # APIにキーワードと表示する論文数を渡す
    papers_data = pc.get_metainfo_from_title(keyword, 100, 5)
    print(keyword)

    if len(papers_data) != 0:
      keys = papers_data[0].keys()
      return render_template('index.html',
                             n=len(keys),
                             papers=papers_data,
                             keys=keys)

  return render_template('index.html')

"""
Localでhtmlを表示する場合はhost="localhost"
Replit上でhtmlを表示する場合はhost="0.0.0.0",port=81を
使用する
"""
if __name__ == "__main__":
  app.run(debug=False, host="0.0.0.0", port=81)
  #app.run(debug=False, host='localhost')
