# Configuration File with stored constants

# Define the login URL and the thread URL:
login_url = 'https://waronline.org/fora/index.php?login/login'
thread_url = 'https://waronline.org/fora/index.php?threads/warbot-playground.17636/'
post_url = "https://waronline.org/fora/index.php?threads/warbot-playground.17636/add-reply"

# SSH settings
ssh_host = '129.159.146.88'
ssh_user = 'ubuntu'
ssh_key_path = 'C:/Users/kerts/OneDrive/Documents/Keys/Ubuntu_Oracle/ssh-key-2023-02-12.key'
#ssh_key_path = 'ssh-key-2023-02-12.key'

# MySQL settings:
mysql_host = 'localhost'  # because we will connect through the SSH tunnel
mysql_port = 3306  # the default MySQL port
mysql_user = 'root'
mysql_password = 'naP2tion'
mysql_db = 'warbot'
ssh_port = 22
dbTableName = 'conversations' # messages data table

# WarBot Server Settings:
HOST = '129.159.146.88'
PORT = 5000

# Define the login credentials:
username = 'WarBot'
password = 'naP2tion'

# Maximum number of words in message:
MaxWords = 50 # The server is relatively weak to fast-process the long messages

# Maximum conversation pairs in the Database
remaining_messages = 2

# Time between the reply sessions:
timeout = 5 # min