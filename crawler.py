import requests
from bs4 import BeautifulSoup
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random
from indexPage import index_page
import csv
from urllib.parse import urlparse

# can_crawl respects robots.txt of the website

def can_crawl(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Checking robots.txt for: {robots_url}")
  
    try:
        response = requests.get(robots_url)
        response.raise_for_status()
        disallowed_paths = []
        for line in response.text.splitlines():
            if line.startswith("Disallow"):
                parts = line.split()
                if len(parts) > 1:
                    disallowed_paths.append(parts[1])
        for path in disallowed_paths:
            if urlparse(url).path.startswith(path):
                print(f"Disallowed by robots.txt: {url}")
                return False
        return True
    except requests.RequestException:
        print(f"Failed to access robots.txt: {robots_url}")
        return False  # If we can't access robots.txt, assume we can't crawl (we're being nice here)


def crawl(args):
    queue = args['urls_to_crawl']
    visited_urls = args['visited_urls']
    stop_crawl = args['stop_crawl']
    CRAWL_LIMIT = args['CRAWL_LIMIT']
    crawl_count = args['crawl_count']
    lock = args['lock']
    links_queue = args['links_queue']
    index = args['index']
    webpage_id_counter = args['webpage_id_counter']
    webpage_info  =args['webpage_info']

    while not stop_crawl.is_set():
        try:
            current_url = queue.get(timeout=5)
            print("Time to crawl:", current_url)
        except:
            break

        if not can_crawl(current_url):
                queue.task_done()
                continue

        with lock:
           

            if crawl_count[0] >= CRAWL_LIMIT:
                print("Crawl limit reached. Exiting.....")
                stop_crawl.set()
                queue.task_done()
                break

            if current_url in visited_urls:
                queue.task_done()
                continue

            visited_urls.add(current_url)

        time.sleep(random.uniform(0.5, 1.5))

        try:
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()

            webpage = BeautifulSoup(response.content, "html.parser")
            indexed_page = index_page(webpage, current_url)

          
            """
            indexed_page = {
                url: current_url,
                title: title,
                description: discription of website
                words: array of stemmed words with no stop words..
            }
            
            """

            #inverted index

            """
            the -> doc1 , doc2

            quick -> doc1
            """
            
            #creating the index

            with lock:
                for word in indexed_page['words']:
                    if word not in index:
                        index[word] = set()
                    index[word].add(webpage_id_counter[0])

                webpage_info[webpage_id_counter[0]] = indexed_page
                webpage_id_counter[0] += 1

            hyperlinks = webpage.select("a[href]")
            new_urls = parse_links(hyperlinks, current_url)

            with lock:
                for new_url in new_urls:
                    if new_url not in visited_urls:
                        queue.put(new_url)
                crawl_count[0] += 1
           

        except requests.RequestException as e:
            print(f"Failed: {current_url} → {e}")

        finally:
            queue.task_done()
            
def parse_links(hyperlinks, current_url):
    urls = []
    for hyperlink in hyperlinks:
        url = hyperlink["href"]

        # Format the URL into a proper URL
        if url.startswith("#"):
            continue  # Skip same-page anchors
        if url.startswith("//"):
            url = "https:" + url  # Add scheme to protocol-relative URLs
        elif url.startswith("/"):
            # Construct full URL for relative links
            base_url = "{0.scheme}://{0.netloc}".format(requests.utils.urlparse(current_url))
            url = base_url + url
        elif not url.startswith("http"):
            continue  # Skip non-HTTP links
        url = url.split("#")[0]  # Remove anchor
        urls.append(url)
    return urls

def bot():
    starting_urls = [
        "https://www.wikipedia.org/wiki/Google",
        "https://www.bbc.com/news/world",
        "https://news.ycombinator.com/",
    ]

    urls_to_crawl = Queue()
    for seed_url in starting_urls:
        urls_to_crawl.put(seed_url)
    MAX_WORKERS = 10
    CRAWL_LIMIT = 200
    links_queue = Queue()
    visited_urls = set()
    stop_crawl = threading.Event()
    crawl_count = [0]
    lock = threading.Lock()
    webpage_info = {}
    webpage_id_counter = [0]
    index =  {}

    args = {
        'urls_to_crawl': urls_to_crawl,
        'stop_crawl': stop_crawl,
        'visited_urls': visited_urls,
        'CRAWL_LIMIT': CRAWL_LIMIT,
        'crawl_count': crawl_count,
        'lock': lock,
        'links_queue': links_queue,
        'index': index,
        'webpage_info': webpage_info,
        'webpage_id_counter': webpage_id_counter
    }


    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(MAX_WORKERS):
            executor.submit(crawl, args)

    print("all urls have been crawled")

    with open('advanced_inverted_index.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['word', 'doc_ids']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for word, doc_ids in index.items():
            writer.writerow({'word': word, 'doc_ids': list(doc_ids)})

    with open('advanced_doc_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['doc_id', 'url', 'title', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for doc_id, info in webpage_info.items():
            writer.writerow({
                'doc_id': doc_id,
                'url': info['url'],
                'title': info['title'],
                'description': info['description']
            })

bot()