import pandas as pd
import glob
import re

def clean(text):
    if type(text) == str:
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        www_pattern = re.compile(r'\b\w*www\.\w*\b')
        ftp_pattern = re.compile(r'ftp://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        file_pattern = re.compile(r'file://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        underscore_pattern = re.compile(r'\b\w*_\w*\b')
        quote_pattern = re.compile(r'""([^"]*)""')
        curly_brackets_pattern = re.compile(r'\{[^}]*\}')
        post_pattern = re.compile(r'#post')
        write_pattern = re.compile(r'(\b\w+)\sнаписал\(а\)\b')

        text = re.sub(url_pattern, '', text)
        text = re.sub(email_pattern, '', text)
        text = re.sub(ftp_pattern, '', text)
        text = re.sub(www_pattern, '', text)
        text = re.sub(underscore_pattern, '', text)
        #text = re.sub(quote_pattern, '', text)
        text = re.sub(curly_brackets_pattern, '', text)
        text = re.sub(file_pattern, '', text)
        text = re.sub(post_pattern, '', text)
        text = re.sub(write_pattern, '', text)

    return text

path = r'Data' # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

frame = frame.drop_duplicates()

#frame = frame[~frame.applymap(lambda x: x == 'nan').any(1)]
frame = frame.applymap(clean)
frame = frame.applymap(lambda x: str(x).replace("посмотреть вложение", ""))
#frame = frame.applymap(lambda x: str(x).replace('"', ''))

# And again:
frame = frame.drop_duplicates()
frame = frame[frame.apply(lambda x: 'nan' not in x.values, axis=1)]

frame.to_csv(path+'/combined.csv',index = False)