import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import trafilatura
array_links = [
    "http://www.commonlii.org/lk/cases/LKCA/1872/1.html"
]
array_text = []
for l in array_links:
    html = trafilatura.fetch_url(l)
    text = trafilatura.extract(html)
    text_clean = text.replace("\n", " ").replace("\'", "")
    array_text.append(text_clean[0:5000])
from pytopicrank import TopicRank
for j in range(len(array_text)):
    tr = TopicRank(array_text[j])
    print("Keywords of article", str(j+1), "\n", tr.get_top_n(n=5, extract_strategy='first'))