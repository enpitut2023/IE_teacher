""" SemanticScholarのAPIを利用して論文を取得する。
OpenAPIの仕様
https://api.semanticscholar.org/api-docs/
"""

import requests
import json
# from data.extract_by_rake import Rake_Keyword_Extractor

class PaperCaller:
    def __init__(self):
        self.fields = ('title', 'year', 'citationCount','authors',"abstract", "tldr")

    def empty_rdata(self):
        return {"title":"error","abstract":"may_be_error","citationCount":-1}, [{"title":"error","abstract":"may_be_error","citationCount":-1}]
    
    def get_metainfo_from_keyword(self, keyword, num_get, num_extract)->dict:
        def check_api_result(r_dict):
            if "message" in r_dict.keys() or "error" in r_dict.keys():
                return False
            if r_dict['total']==0:
                return False
            return True
        num_get_max = 100
        if num_get > num_get_max:
            num_get = num_get_max
        if num_get < num_extract:
            num_extract = num_get
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        keyword = keyword
        params = {
            'query': keyword,
            'fields': ','.join(self.fields),
            'limit': num_get
        }
        r = requests.get(url=endpoint, params=params)
        r_dict = json.loads(r.text)
        if check_api_result(r_dict)==False:
            return []
        data = r_dict['data']

        if len(data) < num_extract:
            num_extract = len(data)

        self.extract_names(data)
        self.extract_tldr(data)
        
        for dt in data:
            dt.pop("abstract")
            dt.pop("authors")
            
        return data[0:num_extract]

    def get_metainfo_from_paperId(self, paperId, num_get, num_extract)->dict:
        def check_api_result(r_dict):
            if "message" in r_dict.keys() or "error" in r_dict.keys():
                return False
            if r_dict['total']==0:
                return False
            return True
        
        num_get_max = 100
        if num_get > num_get_max:
            num_get = num_get_max
        if num_get < num_extract:
            num_extract = num_get
        
        endpoint = "https://api.semanticscholar.org/graph/v1/paper/batch"
        fields = ('title', 'year', 'citationCount', 'authors', "abstract", "tldr")

        params = {
            "fields": ','.join(fields)
        }

        r = requests.post(endpoint, params=params, json={"ids": [paperId]})
        r = '{"data": ' + r.text[:-1] + "}"
        r_dict = json.loads(r)["data"]
        if len(r_dict) == 0:
            main_data = []
        main_data = r_dict
        self.extract_tldr(main_data)

        data = self.get_main_paper_reference_dict(paperId)
        if len(data) == 0:
            return main_data[0], []

        if len(data) < num_extract:
            num_extract = len(data)

        paperIds = self.extract_paperIds(data)
        data = self.get_paper_data_tldr(paperIds[:num_extract])
        self.culcurate_importance(data, 0)
        data = self.sort_metainfo_by_importance(data)

        self.extract_names(data)
        self.extract_tldr(data)
        
        for dt in data:
            dt.pop("abstract")
            dt.pop("authors")
            
        return main_data[0],  data[0:num_extract]
 
    def get_metainfo_from_title(self,name_of_paper,num_get,num_extract)->dict:
        """ 
        入力論文タイトルでAPIを叩き、検索する。検索した中から完全一致する論文名を探しだし、その参考文献メタデータのリストを返す。
        Args:
            name_of_paper(str):入力論文タイトル
            num_get(int):検索件数を指定
            num_extract(int):検索結果から抽出する論文数
        Return:
            main_paper(dict):入力論文に関するメタデータ
            data(list<-dict):入力論文の参考文献メタデータのリスト、ソートされている
        """
        def check_api_result(r_dict):
            if "message" in r_dict.keys() or "error" in r_dict.keys():
                return False
            if r_dict['total']==0:
                return False
            return True
            
        num_get_max = 100
        if num_get > num_get_max:
            num_get = num_get_max
        if num_get < num_extract:
            num_extract = num_get

        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        keyword = name_of_paper
        params = {
            'query': keyword,
            'fields': ','.join(self.fields),
            'limit': num_get
        }
        r = requests.get(url=endpoint, params=params)
        
        r_dict = json.loads(r.text)
        if check_api_result(r_dict)==False:
            return self.empty_rdata()
        
        data = r_dict['data']

        if self.keyword_or_title(keyword, data):
            # タイトルが入力された場合
            main_paper = self.get_main_paper(keyword, data)
            main_paper_id = main_paper.pop("paperId")
            data = self.get_main_paper_reference_dict(main_paper_id)
        else:
            main_paper = []

        if len(data) < num_extract:
            num_extract = len(data)

        self.culcurate_importance(data, 0)
        data = self.sort_metainfo_by_importance(data)
        paperIds = self.extract_paperIds(data)
        data = self.get_paper_data_tldr(paperIds[:num_extract])
        self.culcurate_importance(data, 0)
        data = self.sort_metainfo_by_importance(data)

        self.extract_names(data)
        self.extract_tldr(data)
        
        for dt in data:
            dt.pop("paperId")
            dt.pop("abstract")
            dt.pop("authors")
            
        return data[0:num_extract]
    
    def sort_metainfo(self, list_dict):
        """ 
        論文メタデータのリストをcitationCountの降順にソートして返す関数
        Args:
            list_dict(list<-dict):論文メタデータの辞書のリスト
        Return:
            list_dict_sorted(list<-dict):ソートされた論文メタデータの辞書のリスト
        """
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['citationCount'],reverse=True)
        return list_dict_sorted
    
    def sort_metainfo_by_importance(self, list_dict):
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

    def culcurate_importance(self, list_dict, alpha):
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

    def extract_names(self, list_dict):
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

    def extract_tldr(self, list_dict):
        for dt in list_dict:
            if dt["tldr"] != None:
                tldr = dt["tldr"]["text"]
                dt["tldr"] = tldr

    def extract_paperIds(self, list_dict):
        paperIDs = []
        for paper in list_dict:
            if paper["paperId"] == None:
                continue
            paperIDs.append(paper["paperId"])

        return paperIDs

    def get_main_paper(self, title, list_dict):
        """ 
        論文メタデータの中から、入力論文タイトルを探す。
        Args:
            title(str):入力された論文タイトル
            list_dict(list<-dict):論文メタデータの辞書のリスト
        Return:
            paper(dict):入力論文のメタデータを返す。見つからなかった場合は-1を返す。
        """
        title = title.replace(" ", "").lower()
        for paper in list_dict:
            if title == paper["title"].replace(" ", "").lower():
                break
        return paper
    
    def keyword_or_title(self, title, list_dict):
        title = title.replace(" ", "").lower()
        for paper in list_dict:
            if title == paper["title"].replace(" ", "").lower():
                return True
        
        # Not Found
        return False
    
    def get_main_paper_reference_dict(self, paperID):
        """ 
        paperIDの参考文献のメタデータを返す
        Args:
            paperID(?):検索論文のID
        Return:
            result(list<-dict):参考文献のメタデータ
        """
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/{}/references'.format(paperID)
        #fields = ('title', 'year', 'citationCount', 'authors', "abstract", "tldr")
        fields = ('title', 'year', 'citationCount', 'authors', "abstract")
        params = {
            'fields': ','.join(fields),
            "limit": 1000
        }
        
        r = requests.get(url=endpoint, params=params)
        r_dict = json.loads(r.text)["data"]
        
        result = []
        for paper in r_dict:
            result.append(paper["citedPaper"])
            
        return result
    """ 
    def get_papers_from_rake(self,abst,num_get=100,num_keywords=5):
        rake_ext=Rake_Keyword_Extractor()
        keywords=rake_ext.get_keywords(abst,num_keywords)
        print(keywords)
        ret=[]
        #各keywordで検索。上位1件を追加。
        for keyword in keywords:
            endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
            params = {
                'query': keyword,
                'fields': ','.join(self.fields),
                'limit': num_get
            }
            r = requests.get(url=endpoint, params=params)
            r_dict = json.loads(r.text)
            data = r_dict['data']
            ret=ret+data[0:num_get]
        return ret 
    """
    
    def get_paper_data_tldr(self, paperIDs):
        endpoint = "https://api.semanticscholar.org/graph/v1/paper/batch"
        fields = ('title', 'year', 'citationCount', 'authors', "abstract", "tldr")

        params = {
            "fields": ','.join(fields)
        }

        r = requests.post(endpoint, params=params, json={"ids": paperIDs})
        r = '{"data": ' + r.text[:-1] + "}"
        r_dict = json.loads(r)["data"]

        return r_dict
                
if __name__ == "__main__":
    pc=PaperCaller()
    input_txt = input("keyを入力:")
    data=pc.get_metainfo_from_keyword(input_txt,1000,50)
    data = pc.get_metainfo_from_paperId(data[0]['paperId'], 10, 10)
    for d in data:
        print(d)

