import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


# Download NLTK data only if not already downloaded

def index_page(webpage, webpage_url):
   
    
    # Initialize NLTK components    
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    #Collect title and description
    title_tag = webpage.find('title')
    title = title_tag.get_text().strip() if title_tag else 'No Title'
    
    #Collect description
    description = ''
    meta_description = webpage.find('meta', attrs={'name': 'description'})
    if meta_description and 'content' in meta_description.attrs:
        description = meta_description['content']
    else:
        text_content = webpage.get_text(separator=" ", strip=True)
        description = text_content[:200] + "..." if len(text_content) > 200 else text_content
    
    
    # Grab ALL the words in the page.
    text_content = webpage.get_text(separator=' ', strip=True)
    #Splitting them into the individual words
    tokens = word_tokenize(text_content.lower())
    #Big brain techniques 2 and 3
    #Stemming the words and removing stop words.
    filtered_words = [
        ps.stem(word) for word in tokens if word.isalpha() and word not in stop_words
    ]
    
    #Add the information to the index
    indexed_page = {
        "url": webpage_url,
        "title": title,
        "description": description,
        "words": filtered_words
    }
    #If you want to print the results
    #print(f"Indexed: {webpage_url}. \n Here's the info:  \n title: {title} \n description: {description} \n number of words: {len(filtered_words)} \n")
    return indexed_page