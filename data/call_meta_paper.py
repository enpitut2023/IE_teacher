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
        num_get_max=100
        if num_get>num_get_max:
            num_get=num_get_max
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
        
        data = r_dict['data']
        reference_data = []
        main_paper = self.get_main_paper(keyword, data)
        main_paper_id = main_paper.pop("paperId")
        if main_paper_id == -1:
            return reference_data
        else:
            reference_data = self.get_main_paper_reference_dict(main_paper_id)
            #api
        if len(reference_data)<num_extract:#
            num_extract=len(reference_data)
        self.extract_names(reference_data)
        self.culcurate_importance(reference_data,0.5)
        reference_data=self.sort_metainfo_by_importance(reference_data)
        for dt in reference_data:
            dt.pop("paperId")
            dt.pop("importance")
        return main_paper,reference_data[0:num_extract]
    
    
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
            if not string:
                string = None
            dt['authors'] = string

        

    '''
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
    '''
    
    def get_main_paper(self, title, data):
        title = title.replace(" ", "").lower()
        for paper in data:
            if title == paper["title"].replace(" ", "").lower():
                return paper
        
        # Not Found
        return -1
    
    def get_main_paper_reference_dict(self, paperID):
        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/{}/references'.format(paperID)
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
data=pc.get_metainfo_from_title(keyword,100,100)
for dt in data:
    if not dt['authors']:
        print(dt['authors'])
    




if __name__ == "__main__":
    pc=PaperCaller()
    data=pc.get_metainfo_from_title('Deep Learning in Neural Networks: An Overview',1000,50)
    """

