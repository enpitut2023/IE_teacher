""" SemanticScholarのAPIを利用して論文を取得する。
OpenAPIの仕様
https://api.semanticscholar.org/api-docs/
"""

import requests
import json
from requests import Session
import os
from typing import Generator, TypeVar

S2_API_KEY = os.environ.get('S2_API_KEY', '')

T = TypeVar('T')


def batched(items: list[T], batch_size: int) -> list[T]:
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

def get_paper_batch(session: Session, ids: list[str], fields: str = 'paperId,title', **kwargs) -> list[dict]:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        'x-api-key': S2_API_KEY,
    }
    body = {
        'ids': ids,
    }

    # https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers
    with session.post(url='https://api.semanticscholar.org/graph/v1/paper/batch',
                    params=params,
                    headers=headers,
                    json=body) as response:
        
        response.raise_for_status()
        return response.json()
    
def get_papers(ids: list[str], batch_size: int = 100, **kwargs) -> Generator[dict, None, None]:
    # use a session to reuse the same TCP connection
    with Session() as session:
        # take advantage of S2 batch paper endpoint
        for ids_batch in batched(ids, batch_size=batch_size):
            yield from get_paper_batch(session, ids_batch, **kwargs)

class PaperCaller:
    def __init__(self):
        self.fields = ('title', 'year', 'citationCount', 'authors', "abstract", "tldr")

    def check_api_result(self, data):
        if type(data) == dict:
            try:
                if "total" in data.keys():
                    if data["total"] == 0:
                        return False
                if "message" in data.keys() or "error" in data.keys():
                    return False
            except:
                return False
        elif type(data) == list:
            if len(data) == 0:
                return False
        else:
            return False
        
        return True
    
    def get_papers_by_keyword(self, keyword, limit=100)->list:
        # 論文データ取得用のパラメータ設定
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        params = {
            'query': keyword,
            'fields': ','.join(self.fields),
            'limit': limit
        }
        
        # 論文データ取得
        r = requests.get(url=endpoint, params=params)
        r_dict = json.loads(r.text)
        print(r_dict)

        # 結果を確認
        if not self.check_api_result(r_dict):
            return []
        data = self._cut_none(r_dict['data'])

        self._extract_author_names(data)
        self._extract_tldr(data)
        
        for dt in data:
            dt.pop("abstract")
            dt.pop("authors")
            
        return data
      
    #getメソッドで論文1個を取得するメソッド
    def get_paper_by_paperId(self, paperID)->dict:
        endpoint = "https://api.semanticscholar.org/graph/v1/paper/{}?fields={}".format(paperID, "title,year,citationCount,tldr,url")
        r=requests.get(endpoint)
        r = '{"data": ' + r.text.replace("\n", "") + "}"
        r_dict = json.loads(r)["data"]

        if not self.check_api_result(r_dict):
            return {}
        
        papers = [r_dict]
        self._extract_tldr(papers)
        
        return papers[0]
    
    def get_papers_by_paperIds(self, paperIDs, limit=500)->list:
        # 論文データ取得用のパラメータ設定
        fields = 'title,year,citationCount,authors,abstract,tldr,url'
        paperIDs = paperIDs[:limit]

        r_dict = []
        # 論文データ取得
        print("papers取得")
        for paper in get_papers(paperIDs, fields=fields):
            if not paper:
                continue
            
            r_dict.append(paper)


        # 結果を確認
        if not self.check_api_result(r_dict):
            print("ERROR!")
            return []
        
        r_dict = self._cut_none(r_dict)
        print(len(r_dict))
        self._culcurate_importance(r_dict, alpha=0.0)
        self._extract_tldr(r_dict)

        return r_dict
    
    def get_papers_by_paperIds_for_result(self, paperIDs, limit=500)->list:
        # 論文データ取得用のパラメータ設定
        fields = 'title,year,citationCount,authors,abstract,tldr,url,journal,venue,fieldsOfStudy'
        paperIDs = paperIDs[:limit]

        r_dict = []
        # 論文データ取得
        print("papers取得")
        for paper in get_papers(paperIDs, fields=fields):
            if not paper:
                continue
            
            r_dict.append(paper)


        # 結果を確認
        if not self.check_api_result(r_dict):
            print("ERROR!")
            return []
        
        r_dict = self._cut_none(r_dict)
        print(len(r_dict))
        self._culcurate_importance(r_dict, alpha=0.0)
        self._extract_tldr(r_dict)

        return r_dict
    
    def get_papers_by_paperIds_using_for_loop(self, paperIDs, limit=10):
        papers=[]
        for paperID in paperIDs[:limit]:
            res=self.get_paper_by_paperId(paperID)
            papers.append(res)

        papers = self._cut_none(papers)
        self._extract_tldr(papers)

        return papers
    
    def get_reference_papers_ids_by_main_paper_id(self, paperID, limit=1000):
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/{}/references'.format(paperID)
        fields = ("paperId",)
        params = {
            'fields': ','.join(fields),
            "limit": limit
        }
        
        # 論文データ取得
        r = requests.get(url=endpoint, params=params)
        r_dict = json.loads(r.text)

        # 結果を確認
        if not self.check_api_result(r_dict):
            return []
        
        # データを取り出す
        r_dict = self._cut_none(r_dict["data"])
        
        reference_papers = []
        for paper in r_dict:
            reference_papers.append(paper["citedPaper"])

        # 参考文献0だったら空リストを返す
        if len(reference_papers) == 0:
            return []

        # paperIdsのリストを受け取る
        paperIds = self._extract_paperIds(reference_papers)

        # うまく見つけられなかったら空リストを返す
        if len(paperIds) == 0:
            return []
        
        return paperIds

    def _sort_papers_by_importance(self, list_dict):
        """ 
        論文メタデータのリストをimportanceの降順にソートして返す関数
        Args:
            list_dict(list<-dict):論文メタデータの辞書のリスト
        Return:
            list_dict_sorted(list<-dict):ソートされた論文メタデータの辞書のリスト
        """
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['importance'],reverse=True)
        return list_dict_sorted

    def _culcurate_importance(self, list_dict, alpha):
        """
        各論文データに対して、重要度を計算し辞書に登録
        importance = alpha * CitationCount + (1 - alpha) * Yearで計算
        Noneのデータは全体平均を用いて計算
        Args:
            list_dict(list<-dict):論文メタデータの辞書のリスト
            alpha(float,int):重要度計算の重み
        """
        citationCount = []
        year = []
        for dt in list_dict:
            if (dt['citationCount'] != None):
                citationCount.append(int(dt['citationCount']))
            if (dt['year'] != None):
                year.append(int(dt['year']))
                
        #CitationCountの最大最小と平均を計算
        if (len(citationCount) != 0):
            citationCount_max = max(citationCount)
            citationCount_min = min(citationCount)
            citationCount_avg = sum(citationCount) / len(citationCount)
        else:
            citationCount_max = 0
            citationCount_min = 0
            citationCount_avg = 0
            alpha = 0
            
        #Yearの最大最小と平均を計算
        if (len(year) != 0):
            year_max = max(year)
            year_min = min(year)
            year_avg = sum(year) / len(year)
        else:
            year_max = 0
            year_min = 0
            year_avg = 0
            alpha = 1
        
        #各論文に対してimportanceを計算し辞書に登録
        for dt in list_dict:
            if (dt['citationCount'] != None):
                c = ((int(dt['citationCount']) - citationCount_min) / (citationCount_max - citationCount_min + 0.01))  #　0除算回避
            else:
                c = ((citationCount_avg - citationCount_min) / (citationCount_max - citationCount_min + 0.01))
            if (dt['year'] != None):
                y = ((int(dt['year']) - year_min) / (year_max - year_min + 0.01))
            else:
                y = ((year_avg - year_min) / (year_max - year_min + 0.01))
            i = alpha * c + (1 - alpha) * y
            dt['importance'] = i

    def _extract_author_names(self, list_dict):
        """
        論文データの著者名のdictををStringに変換
        Args:
            list_dict(list<-dict):論文メタデータの辞書のリスト
        """
        for dt in list_dict:
            authors = dt['authors']
            string = ""
            for index, author in enumerate(authors):
                if (index == 0):
                    string += author['name']
                else:
                    string += ", " + author['name']
            if not string:
                string = None
            dt['authors'] = string

    def _extract_tldr(self, list_dict):
        for dt in list_dict:
            if dt["tldr"] != None:
                if type(dt["tldr"]) == dict:
                    tldr = dt["tldr"]["text"]
                else:
                    tldr = dt["tldr"]
        
                dt["tldr"] = tldr

    def _extract_paperIds(self, list_dict):
        paperIDs = []
        for paper in list_dict:
            if paper["paperId"] == None:
                continue
            paperIDs.append(paper["paperId"])

        return paperIDs
    

    def _cut_none(self, list_dict):
        list_dict = list(filter(None, list_dict))

        return list_dict
    
"""
if __name__ == "__main__":
    pc=PaperCaller()
    input_txt = input("keyを入力:")
    data=pc.get_metainfo_from_keyword(input_txt,1000,50)
    data = pc.get_metainfo_from_paperId(data[0]['paperId'], 10, 10)
    for d in data:
        print(d)
"""