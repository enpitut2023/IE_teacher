import requests
import json

class PaperCaller:
    def __init__(self):
        pass

    def empty_rdata(self):
        return [{"title":"error","abstract":"may_be_error","citationCount":-1}]

    def get_metainfo_from_title(self,name_of_paper,num_get,num_extract)->dict:
        def check_num_get_ext(num_get,num_extract):
            if num_get>100:
                return False
            elif num_extract>num_get:
                return False
            else:
                return True
        
        def check_too_many_requests(r_dict):
            if "message" in r_dict.keys():
                return False
            else:
                return True
        
        if check_num_get_ext(num_get,num_extract)==False:
            return self.empty_rdata()

        endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        keyword = name_of_paper
        fields = ('title', 'year', 'referenceCount', 'citationCount',
            'influentialCitationCount', 'isOpenAccess', 'fieldsOfStudy', 'authors',"abstract")
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
        data=self.sort_metainfo(data)
        return data[0:num_extract]
    
    def sort_metainfo(self,list_dict):
        list_dict
        list_dict_sorted = sorted(list_dict,
                                   key=lambda x:x['citationCount'],reverse=True)
        return list_dict_sorted

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
pc=PaperCaller()
data=pc.get_metainfo_from_title('python',70,10)
for dt in data:
    print(dt['citationCount'])
"""