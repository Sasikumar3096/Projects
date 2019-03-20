from bs4 import BeautifulSoup
import urllib
import requests
import json
import threading
from threading import Thread
import time

def get_page(url):
    while True:
        try:
            proxy_add = get_proxy()
            print(proxy_add)
            req = requests.get(url, proxies={'https': 'https://' + proxy_add}, timeout=15)
            return BeautifulSoup(req.text, 'html.parser')

        except Exception as e:
            print(e)
            continue

file = open("key.txt")
api_key = list(file)[0]
#Details for SQL
sql_file = open("sqlconfig.txt")
SQL_USER = sql_file.readline()[:-1].split(':')[1]
SQL_PASSWORD =  sql_file.readline()[:-1].split(':')[1]
sql_file.close()


file.close();

def store_data(artice_doi, citation_title, citation_date, author_name, author_email):
    print(artice_doi, citation_title, citation_date, author_name, author_email)
    conn = MySQLdb.connect("13.233.214.65", SQL_USER, SQL_PASSWORD, "plosone")
    conn.set_character_set('utf8')
    cur = conn.cursor()
    cur.execute("INSERT INTO author_new (artice_doi, citation_title, citation_date, author_name, author_email) VALUES (%s, %s, %s, %s, %s);", (artice_doi, citation_title, citation_date, author_name, author_email))
    conn.commit()

def get_detail(url):
    #url = 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210244'
    print(url)

    soup = get_page(url)

    # Finding the Document Doi
    start = url.find('journal.pone')
    artice_doi =  url[start:]
    #print(artice_doi)

    #Title
    citation_title = str(soup.find_all("meta", attrs={'name': "citation_title"}))
    start = citation_title.find('"')+1
    end = citation_title.find('"',start)
    citation_title = citation_title[start:end]
    #print(citation_title)
    # Date..
    citation_date = str(soup.find_all("meta", attrs={'name': "citation_date"}))
    start = citation_date.find('"') + 1
    end = citation_date.find('"', start)
    citation_date = citation_date[start:end]
    #print(citation_date)

    #Author Names
    li_tags = soup.find_all('li', {'data-js-tooltip': 'tooltip_trigger'})
    authors_count = len(li_tags)
    authors=[]
    for x in li_tags:
        temp=[]
        name = x.find_all('a')[0].text
        if ',' in name:
            name = name.replace(',', '')
        if '\n' in name:
            name = name.replace('\n', '')
        name = name.strip()
        temp.append(name)
        has_email = False
        all_p = str(x.find_all('p'))
        try:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str(x))
            temp.append(match.group(0))
            has_email = True
        except Exception as e:
            continue
        if not has_email:
            temp.append('')
        store_data(artice_doi, citation_title, citation_date, temp[0], temp[1])

def get_links(limit):
    global file
	#Write Log
    log = open("get_links_log.txt", 'a')
    for i in range(1, limit + 1):
        url = #Url of the page to Scrap
        print("Starting Page ", i)
        print(url)
        soap = get_page(url)
        soap.find_all('a', {'class': 'article-url'})
        a_tag = soap.find_all('a', {'class': 'article-url'})
        for x in range(len(a_tag)):
            link = str(a_tag[x])
            start = link.find('="', 15) + 2
            end = link.find('"', start)
            link = link[start:end]
            print(link)
            file.write('https://journals.plos.org' + link + "\n")
			
			start_threading('https://journals.plos.org' + link)
        log.write("Completed for Page " + str(i) + "\n")
    log.close()

#To run Mulltiple Threads
def start_threading(url):
    if threading.active_count() < 40:
        print("Starting a thread ", threading.active_count())
        th = Thread(target=get_detail, args=(url,))
        th.start()
    else:
        time.sleep(2)
        start_threading(url)


file = open("log.txt", "a")
#Number of Pages in the Site's Browse Pages is passed as parameter
get_links(16533)
file.close()
