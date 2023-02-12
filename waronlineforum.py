# -*- coding: utf-8 -*-
"""WarOnlineForum.ipynb"""

# Extracting messages from forum

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import urllib.request as urllib
import warnings
warnings.filterwarnings("ignore")

# initiate the corpus of Quote->Response texts
corpus = pd.DataFrame(columns=['Quote', 'Response'])

def remove_substring(string, substring):
    index = string.find(substring)
    if index != -1:
        start_index = string.rfind(" ", 0, index) + 1
        end_index = string.find(" ", index)
        if end_index == -1:
            end_index = len(string)
        return string[:start_index] + string[end_index:]
    return string

def remove_attachments(string, substring='Посмотреть вложение'):
  index = string.find(substring)
  if index != -1:
    end_index = string.find(" ", index)
    if end_index == -1:
      end_index = len(string)
      return string[:index] + string[end_index:]
  return string

def collectDataFromPage(url):
  # specify the URL of the XenForo forum page you want to extract messages from

  # send a request to the URL and get the HTML response
  response = requests.get(url)
  html = response.content

  # parse the HTML using BeautifulSoup
  soup = BeautifulSoup(response.content, "html.parser")

  # Find all elements with class "messageContent"
  message_contents = soup.find_all("div", class_="bbWrapper")

  # Loop through each messageContent element
  for message_content in message_contents:
    # Find the text within the messageContent element
    message_text = message_content.text.strip()
    
    # Find the quoted text within the messageContent element
    try:
      quoted_text = message_content.find("blockquote").text.strip()
      quoted_text = ''.join(BeautifulSoup(quoted_text, "html.parser").findAll(string=True))
      quoted_text = quoted_text.replace('Нажмите для раскрытия...', '')
      message_text = message_text.replace('Нажмите для раскрытия...', '')
      # Remove the text in between "bbCodeBlock-expandLink js-expandLink" and "</div>"
      
      
      # Print the message text and quoted text
      Quote = re.sub(r'http\S+', '', ' '.join(quoted_text.split()).partition('(а): ')[2])
      Quote = remove_substring(Quote,".com")
      Quote = remove_attachments(Quote)
      Quote = ' '.join(remove_substring(Quote,"@").split())
      
      Message = ' '.join(message_text.replace(quoted_text,'').split())
      Message = remove_substring(Message,".com")
      Message = remove_attachments(Message)
      Message = ' '.join(remove_substring(Message,"@").split())

      if Message and Quote:
        # corpus is a dataframe (global)
        corpus.loc[len(corpus)]=[Quote,Message]
        #print("Quoted Text:", Quote)
        #print("Message Text:", Message)
        #print('________________________')
    except:
      pass

def compare_pages(url1, url2):
    page1 = requests.get(url1).text
    page2 = requests.get(url2).text
    # Stupid, but must be working
    return len(page1) == len(page2)

def compare_pages2(url1, url2):
  return urllib.urlopen(url1).geturl() == urllib.urlopen(url2).geturl()


def pages_of_thread(thread,startingPage=1):
  page = startingPage
  lastPage = False
  while not lastPage:
    response = requests.get(thread+'/page-'+str(page))
    if response.status_code == 200:
      collectDataFromPage(url = thread+'/page-'+str(page))
      print(f'finished page #{page}')
      if not compare_pages2(thread+'/page-'+str(page),thread+'/page-'+str(page+1)):
        page+=1
      else:
        lastPage = True
    else:
      lastPage = True

  # Usage Example:
  #pages_of_thread(0,800) # Thread #0, starting page 800

"""______________________________________ Main Code __________________________________________"""

# Define the URLs to be crawled
base_url = 'https://waronline.org'
# Pehota base subforum
#url = "https://waronline.org/fora/index.php?forums/%D0%9F%D0%B5%D1%85%D0%BE%D1%82%D0%B0.3/"
# Obshevoyskovie base subforum
#url = "https://waronline.org/fora/index.php?forums/%D0%9E%D0%B1%D1%89%D0%B5%D0%B2%D0%BE%D0%B9%D1%81%D0%BA%D0%BE%D0%B2%D1%8B%D0%B5-%D1%82%D0%B5%D0%BC%D1%8B.4/"
# VMF
url = "https://waronline.org/fora/index.php?forums/%D0%92%D0%9C%D0%A4-%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B9-%D1%84%D0%BB%D0%BE%D1%82.12/"

base_page = 1 #Starting with page-1
lastSubForumPage = False

while not lastSubForumPage:

  # Send a GET request to the URL
  response = requests.get(url+'page-'+str(base_page))
  forum_threads = [] #threads on this page of subforum

  # Check if the request was successful
  if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")
      
    # Get all the thread-links on the page
    links = soup.find_all("a")
      
    # Get the links
    for link in links:
      lnk = link.get("href")
      if lnk:
        if 'threads' in lnk:
          forum_threads.append((base_url+lnk).rsplit("/", 1)[0])

    # Clear the duplicate links
    forum_threads = list(set(forum_threads))
      
    for trd in forum_threads:
      pages_of_thread(trd) # Starting at page=1
      print(f'finished thread: {trd}')

    if not compare_pages2(url+'page-'+str(base_page),url+'page-'+str(base_page+1)):
      print(f'finished subforum page #{base_page}')
      base_page+=1
    else:
      lastSubForumPage = True

  else:
    print("Failed to load the page")
    lastSubForumPage = True

# Lowercase all
corpus['Quote'] = corpus['Quote'].apply(lambda x: x.lower() if isinstance(x,str) else x)
corpus['Response'] = corpus['Response'].apply(lambda x: x.lower() if isinstance(x,str) else x)

# Remove all non-alphanumericals
corpus.Quote.str.replace('[^a-zA-Z]', '')
corpus.Response.str.replace('[^a-zA-Z]', '')

#Export to csv
pathToDrive = ''
filename = 'part5.csv'
corpus.to_csv(pathToDrive+filename,index=False)