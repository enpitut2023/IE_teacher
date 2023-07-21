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
        
        data = r_dict['data']

        reference_data = []
        main_paper = self.get_main_paper(keyword, data)
        main_paper_id = main_paper.pop("paperId")
        if main_paper_id == -1:
            return reference_data
        else:
            reference_data = self.get_main_paper_reference_dict(main_paper_id)

        if len(reference_data) < num_extract:#
            num_extract = len(reference_data)

        # reference_data=self.sort_metainfo(reference_data)
        for dt in reference_data:
            dt.pop("paperId")
        return main_paper, reference_data[:num_extract]
    
    def sort_metainfo(self,list_dict):
        print(list_dict)
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['citationCount'],reverse=True)
        return list_dict_sorted

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


#usage
if __name__ == "__main__":
    pc=PaperCaller()
    data=pc.get_metainfo_from_title('Deep Learning in Neural Networks: An Overview',1000,50)