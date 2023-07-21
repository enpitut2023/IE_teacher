import requests
import json

class PaperCaller:
    def __init__(self):
        pass

    def empty_rdata(self):
        return [{"title":"error","abstract":"may_be_error","citationCount":-1}]

    def get_metainfo_from_title(self,name_of_paper,num_get,num_extract)->dict:        
        def check_too_many_requests(r_dict):
            if "message" in r_dict.keys():
                return False
            else:
                return True
        
        if num_get>100:
            num_get=100
        if num_get<num_extract:#
            num_extract=num_get

        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        keyword = name_of_paper
        fields = ('title', 'year', 'citationCount','authors',"abstract")
        params = {
            'query': keyword,
            'fields': ','.join(fields),
            'limit': num_get
        }
        r = requests.get(url=endpoint, params=params)
        
        r_dict = json.loads(r.text)
        if check_too_many_requests(r_dict)==False:
            return self.empty_rdata()
        
        total = r_dict['total']   
        data = r_dict['data']
        if len(data)<num_extract:#
            num_extract=len(data)
        self.extract_names(data)
        self.culcurate_importance(data,0.5)
        data=self.sort_metainfo_by_importance(data)
        for dt in data:
            dt.pop("paperId")
            dt.pop("importance")
        return data[0:num_extract]
    
    def sort_metainfo(self,list_dict):
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['citationCount'],reverse=True)
        return list_dict_sorted
    
    def sort_metainfo_by_importance(self, list_dict):
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['importance'],reverse=True)
        return list_dict_sorted

    """
    i = alpha * c + (1 - alpha) * yで計算
    Noneのデータは平均を用いて計算
    """
    def culcurate_importance(self, list_dict, alpha):
        citationCount = []
        year = []
        for dt in list_dict:
            if (dt['citationCount'] != None):
                citationCount.append(int(dt['citationCount']))
            if (dt['year'] != None):
                year.append(int(dt['year']))

        if (len(citationCount) != 0):
            citationCount_max = max(citationCount)
            citationCount_min = min(citationCount)
            citationCount_avg = sum(citationCount) / len(citationCount)
        else:
            citationCount_max = 0
            citationCount_min = 0
            citationCount_avg = 0
            alpha = 0
        if (len(year) != 0):
            year_max = max(year)
            year_min = min(year)
            year_avg = sum(year) / len(year)
        else:
            year_max = 0
            year_min = 0
            year_avg = 0
            alpha = 1
        
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

    """
    Convert List of Dict to String
    論文データの著者名をStringに変換
    """
    def extract_names(self, list_dict):
        for dt in list_dict:
            authors = dt['authors']
            string = ""
            for index, author in enumerate(authors):
                if (index == 0):
                    string += author['name']
                else:
                    string += ", " + author['name']
            dt['authors'] = string

        

    def get_metainfo_from_title_legacy(self,name_of_paper,num_paper)->dict:
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        keyword = name_of_paper
        fields = ('title', 'year', 'referenceCount', 'citationCount',
            'influentialCitationCount', 'isOpenAccess', 'fieldsOfStudy', 'authors','abstract')
        params = {
            'query': keyword,
            'fields': ','.join(fields),
            'limit': num_paper
        }
        r = requests.get(url=endpoint, params=params)
        
        r_dict = json.loads(r.text)
        total = r_dict['total']
        print(f'Total search result: {total}')
        
        data = r_dict['data']
        return data    

    """
        for d in data:
            print('---------------')
            for fi in fields:
                if fi == 'authors':
                    print(f'{fi}: {list(map(lambda a: a["name"], d[fi]))}')
                else:
                    print(f'{fi}: {d[fi]}')
    """

"""
#usage
keyword = input("Please input keywords ")
pc=PaperCaller()
data=pc.get_metainfo_from_title(keyword,50,50)
for dt in data:
    print(dt['importance'])
"""


