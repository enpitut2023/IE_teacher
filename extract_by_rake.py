from rake_nltk import Rake


class Rake_Keyword_Extractor():
    def __init__(self):
        pass
    def get_keywords(self,doc:str,num_extract=5)->list:
        # Uses stopwords for english from NLTK, and all puntuation characters by
        # default
        r = Rake()
        #Extraction given the text.
        r.extract_keywords_from_text(doc)
        
        # To get keyword phrases ranked highest to lowest with scores.        
        ret=[]
        top_results=r.get_ranked_phrases_with_scores()[0:num_extract]
        for result in top_results:
            ret.append(result[1])
        print(ret)
        return ret

"""
#usage
RE=Rake_Keyword_Extractor()
RE.get_keywords("input your favorite doc",7)
"""