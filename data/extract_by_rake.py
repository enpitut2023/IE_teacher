from rake_nltk import Rake


class Rake_Keyword_Extractor():
    def __init__(self):
        pass
    def get_keywords(self,doc:str,num_extract=5)->list:
        # Uses stopwords for english from NLTK, and all puntuation characters by
        # default
        if doc==None:
            return ['' for i in range(num_extract)]
        r = Rake()
        #Extraction given the text.
        r.extract_keywords_from_text(doc)
        
        # To get keyword phrases ranked highest to lowest with scores.        
        ret=[]
        #top_results=r.get_ranked_phrases_with_scores()[0:num_extract]
        result=r.get_ranked_phrases_with_scores()
        for i in range(num_extract):
            if i<=len(result)-1:
                ret.append(result[i][1])
            else:
                ret.append("")
        return ret


"""
#usage
RE=Rake_Keyword_Extractor()
res=RE.get_keywords("input your favorite doc",7)
print(res)
"""