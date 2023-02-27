# This is an quote and post library for a specific thread in the WarOnline forum.

import WarClient
import conversationDB
import requests
import re
from bs4 import BeautifulSoup
import urllib.request as urllib
import warnings
import time
import config # Here the constants are stored

warnings.filterwarnings("ignore")

# Start a session to persist the login cookie across requests
session = requests.Session()

def fixString(S):
    # This is a helper function to overcome the bugs of tokenizer
    S = S.replace(",+", ",")
    S = S.replace("!.", "!")
    S = S.replace(".?", "?")
    S = S.replace(",,", ",")
    S = S.replace("?.", "?")
    S = S.replace("??", "?")
    S = S.replace(" ?", "?")
    S = S.replace(" .", ".")
    S = S.replace(",!", "!")
    S = S.replace(",.", ",")
    S = S.replace(".]", ".")
    S = S.replace(",\)", ")")
    S = S.replace("&", "")
    S = S.replace("&", "")
    S = S.replace("ен,ицхак", "ен-ицхак")
    S = S.replace("СШа", "США")
    S = S.replace("(,", "(")
    S = S.replace("?.", "?")
    S = S.replace("#", "")
    S = S.replace("()", "")
    S = S.strip(',')
    S = S.strip()
    return S

def compare_pages(url1, url2):
    #Compares 2 pages and returns True if they are the same
    return urllib.urlopen(url1).geturl() == urllib.urlopen(url2).geturl()

def remove_non_english_russian_chars(s):
    # Regular expression to match all characters that are not in English or Russian
    pattern = '[^A-Za-zА-Яа-яЁё(),.!?"\s-]'
    # Replace all matched characters with an empty string
    return re.sub(pattern, '', s)

def remove_extra_spaces(s):
    s = re.sub(r"\s+", " ", s)  # replace all sequences of whitespace with a single space
    s = re.sub(r"\s+([.,])", r"\1", s)  # remove spaces before period or comma
    return(s)

def getLastPage(thread_url=config.thread_url):
    # Returns the number of the last page
    page = 1  # Starting page
    lastPage = False

    while not lastPage:
        if not compare_pages(thread_url + 'page-' + str(page), thread_url + 'page-' + str(page + 1)):
            page += 1
        else:
            lastPage = True
    return page


def login(username=config.username, password=config.password, thread_url=config.thread_url):
    # Log-In to the forum and redirect to thread

    # Retrieve the login page HTML to get the CSRF token
    login_page_response = session.get(config.login_url)
    soup = BeautifulSoup(login_page_response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '_xfToken'})['value']

    # Login to the website
    login_data = {
        'login': username,
        'password': password,
        'remember': '1',
        '_xfRedirect': thread_url,
        '_xfToken': csrf_token
    }
    response = session.post(config.login_url, data=login_data)

    # Check if the login was successful
    if 'Invalid login' in response.text:
        print('Login failed!')
        exit()

def post(message="", thread_url=config.thread_url, post_url=config.post_url, quoted_by="",quote_text="",quote_source=""):
    #Post a message to the forum (with or without the quote
    #quote_source is in format 'post-3920992'
    quote_source = quote_source.split('-')[-1] # Take the numbers only

    if quoted_by:
        message = f'[QUOTE="{quoted_by}, post: {quote_source}"]{quote_text}[/QUOTE]{message}'

    # Retrieve the thread page HTML
    response = session.get(thread_url)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the _xfToken value from the hidden form field
    xf_token = soup.find('input', {'name': '_xfToken'}).get('value')

    # Construct the message data for the POST request
    message_data = {
        '_xfToken': xf_token,
        'message': message,
        'attachment_hash': '',
        'last_date': '',
        '_xfRequestUri': post_url,
        '_xfWithData': '1',
        '_xfResponseType': 'json'
    }

    response = session.post(post_url, data=message_data)

    # Check if the post was successful
    if not response.ok:
        print('Post failed!')
        exit()

    print('Post submitted successfully.')

def getMessages(thread_url=config.thread_url, quotedUser="", startingPage=1):
    # Returns all the quotes for #username in the specific multi-page thread url
    allquotes =[]

    page = startingPage  # Counter
    lastPage = False

    # Initial values for messangerName and the message ID
    messengerName = ""
    messageID = ""
    quotedID = ""

    # Patterns to search in the last quote.
    namePattern = re.compile('data-lb-caption-desc="(.*?) ·')
    messageIDPattern = re.compile('data-lb-id="(.*?)"')
    quotedIDPattern = re.compile('data-source="(.*?)"')
    quotedNamePattern = re.compile('data-quote="(.*?)"')

    while not lastPage:
        response = requests.get(thread_url + 'page-' + str(page))
        if response.status_code == 200:

            # Core of the function
            html_content = response.content

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all the message in the thread page
            messageData = soup.find_all('div', {'class': 'message-userContent lbContainer js-lbContainer'})

            for data in messageData:
                try:
                    # Get the messager username
                    matchName = namePattern.search(str(data))
                    if matchName:
                        messengerName = matchName.group(1)

                    # Get the quoted ID
                    matchID = quotedIDPattern.search(str(data))
                    if matchID:
                        quotedID = matchID.group(1)

                    # Get the message ID
                    matchID = messageIDPattern.search(str(data))
                    if matchID:
                        messageID = matchID.group(1)

                    # Match the QuotedName
                    matchQuotedName = quotedNamePattern.search(str(data))
                    if matchQuotedName:
                        quotedName = matchQuotedName.group(1)
                    if quotedUser and (quotedUser != quotedName):
                        continue

                    # Make sure that the messages have a quote inside
                    blockquote = data.find('blockquote')
                    if blockquote:
                        # Extract the text
                        text = data.find('div', {'class': 'bbWrapper'})
                        for bq in text.find_all('blockquote'):
                            bq.extract()
                        reply = text.get_text().replace('\n', ' ').strip()

                        allquotes.append({'reply': reply, 'messengerName': messengerName, 'messageID': messageID, 'quotedID': quotedID})

                except:
                    continue # There was no text in this quote, move to the next

            #check if that is not a last page
            if not compare_pages(thread_url + 'page-' + str(page), thread_url + 'page-' + str(page + 1)):
                page += 1
            else:
                lastPage = True
        else:
            lastPage = True

    return allquotes

# Core Engine of the Client
def WarOnlineBot():

    lookUpPages = 5 # How many pages back to look in the thread
    startingPage = getLastPage(thread_url=config.thread_url) - lookUpPages
    if startingPage < 1:
        startingPage = 1 # Starting page cannot be less than 1

    login(username=config.username, password=config.password, thread_url=config.thread_url)
    #print("logged in")

    # All messages (with quotes) by ALL users:
    allMessages = getMessages(thread_url=config.thread_url, quotedUser='', startingPage=startingPage)

    # IDs of the quoted messages, replied by the bot:
    messages_by_bot_IDs = []

    for msg in allMessages:
        # Set a list of replied messages IDs
        if msg['messengerName'] == config.username: #message posted by the WarBot
            messages_by_bot_IDs.append(msg['quotedID'].split(': ')[-1])
    # remove empty and repeated elements
    messages_by_bot_IDs = list(set([elem for elem in messages_by_bot_IDs if elem]))

    # All messages (with quotes) sent _FOR_ the Bot:
    messagesForBot = getMessages(thread_url=config.thread_url, quotedUser=config.username, startingPage=startingPage)

    # IDs of the messages, quoting the bot:
    messages_for_bot_IDs = []

    for msg in messagesForBot:
        # Set a list of posted message IDs
        messages_for_bot_IDs.append(msg['messageID'].split('-')[-1])
    # remove empty elements
    messages_for_bot_IDs = [elem for elem in messages_for_bot_IDs if elem]

    # Filter to leave just the unanswered messages IDs:
    messages_for_bot_IDs = [ID for ID in messages_for_bot_IDs if ID not in messages_by_bot_IDs]

    # Reply the unanswered messages:
    for msg in messagesForBot:
        if msg['messageID'].split('-')[-1] in messages_for_bot_IDs:

            originalQuote = msg['reply']
            if originalQuote == "": # Just images, no text
                continue
            else:
                quote = remove_non_english_russian_chars(msg['reply'])
                quote = remove_extra_spaces(quote)

            message = "" #Initiating the reply message by Bot
            previous_dialogue = "" #Initiating the previous dialogue

            print('Quote: ', originalQuote)

            # Init Connection
            db = conversationDB.DataBase()
            # Get the previous dialogue from the database
            dbmessages = db.getmessages(msg['messengerName'])
            for dbmessage in dbmessages:
                previous_dialogue += dbmessage[0]+' '+dbmessage[1]+' '
            # Update the string and preprocess it
            quote = previous_dialogue + quote
            quote = remove_non_english_russian_chars(quote)
            quote = remove_extra_spaces(quote)
            # Truncate the quote to return only the last MaxWords of words:
            quote = " ".join(quote.split()[-config.MaxWords:])

            # Fix the quote string, to eliminate errors:
            quote = fixString(quote)

            FailureCounter = 0 # In case there is a bug in the model
            while (not message) and (FailureCounter<3):
                message = WarClient.getReply(message=quote)
                # Strange error in message if there is '02' in the message text.
                if '02' in message:
                    message = ""
                FailureCounter+=1

            if FailureCounter == 3:
                continue # Skip that answer

            # Post-processing fixes:
            message = fixString(message)
            print('Reply: ', message)

            # Add the new conversation pair to the database
            db.setmessages(username=msg['messengerName'], message_text=originalQuote, bot_reply=message)
            # Clean up the excessive records, leaving only the remaining messages
            db.cleanup(username=msg['messengerName'], remaining_messages=config.remaining_messages)
            # Delete the duplicate records
            db.deleteDuplicates()

            login(username=config.username, password=config.password, thread_url=config.thread_url)
            time.sleep(1)
            post(message=message, thread_url=config.thread_url, post_url=config.post_url, quoted_by=msg['messengerName'], quote_text=originalQuote, quote_source=msg['messageID'])

            time.sleep(10)  # Standby time for server load release


if __name__ == '__main__':

    # Start the scheduler
    while True:
        print('Starting Session')
        WarOnlineBot()

        timer = range(60 * config.timeout)
        for t in timer:
            time.sleep(1)
