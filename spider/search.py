import csv
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import json

inverted_index = {}
document_info = {}

def load_inverted_index(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['word']
            doc_ids_str = row['doc_ids'].strip("[]")  # Remove brackets
            doc_ids_list = doc_ids_str.split(', ') if doc_ids_str else []
            doc_ids = set(int(doc_id) for doc_id in doc_ids_list)
            inverted_index[word] = doc_ids
    return inverted_index


def load_document_info(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            doc_id = int(row['doc_id'])
            document_info[doc_id] = {
                'url': row['url'],
                'title': row['title'],
                'description': row['description'],
                # 'pagerank': float(row['pagerank'])
            }

    # print(document_info)
    return document_info

# Load the inverted index and document info
# If you are using a different file, replace the path with the path to your file
#If you're using a database, replace this with the code to connect to your database
# try:
#     inverted_index = load_inverted_index('advanced_pagerank_inverted_index.csv')
#     document_info = load_document_info('advanced_pagerank.csv')
# except FileNotFoundError:
#     try:
#         inverted_index = load_inverted_index("dvanced_pagerank_inverted_index.csv")
#         document_info = load_document_info("advanced_pagerank.csv")
#     except FileNotFoundError:
#         print("Error: Files not found, run the advanced_pagerank.py file first")
#         print("Exiting...")
#         exit()
        

def search() :
    query = input("enter a query to search for resulting docs")
    tokens = word_tokenize(query)

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))

    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmed_words = [stemmer.stem(word) for word in filtered_tokens]
    

    #we have inverted index and document info
    matched_doc_ids = set()

    for word in stemmed_words:
        if word in inverted_index:
            matched_doc_ids.update(inverted_index[word])

  

    if not matched_doc_ids:
        return []
    # Retrieve documents and their PageRank scores

    results = []

    for doc_id in matched_doc_ids:
        info = document_info[doc_id]
        results.append({
            'doc_id': doc_id,
            'url': info['url'],
            'title': info['title'],
            'description': info['description'],
            # 'pagerank': info['pagerank']
        })

    return results

load_document_info('advanced_doc_info.csv')
load_inverted_index('advanced_inverted_index.csv')

results = search()
print(json.dumps(results, indent=4))