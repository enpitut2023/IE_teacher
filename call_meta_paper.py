import requests
import json

class PaperCaller:
    def __init__(self):
        pass
    def get_metainfo_from_title(self,name_of_paper,num_paper)->dict:
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
data=pc.get_metainfo_from_title('Lenia - Biology of Artificial Life',1)
print(data)
"""