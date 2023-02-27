import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder
import config # Here the constants are stored

# SSH settings
ssh_host = config.ssh_host
ssh_user = config.ssh_user
ssh_key_path = config.ssh_key_path

# MySQL settings
mysql_host = config.mysql_host
mysql_port = config.mysql_port
mysql_user = config.mysql_user
mysql_password = config.mysql_password
mysql_db = config.mysql_db
ssh_port = config.ssh_port
dbTableName = config.dbTableName

class DataBase():
    # manages mySQL connection and send-receive
    def __init__(db, ssh_key_path = ssh_key_path, ssh_host=ssh_host, ssh_port=ssh_port, ssh_user=ssh_user,
                 mysql_host=mysql_host,mysql_port=mysql_port,mysql_user=mysql_user,mysql_password=mysql_password,mysql_db=mysql_db):
        # create an SSH client and load the private key
        db.ssh_client = paramiko.SSHClient()
        db.ssh_client.load_system_host_keys()
        db.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        db.private_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)
        db.ssh_key_path = ssh_key_path
        db.ssh_host=ssh_host
        db.ssh_port=ssh_port
        db.ssh_user=ssh_user
        db.mysql_host=mysql_host
        db.mysql_port=mysql_port
        db.mysql_user=mysql_user
        db.mysql_password=mysql_password
        db.mysql_db=mysql_db
    def getmessages(db,username = ""):
        # get the entire conversation with the specific user
        with SSHTunnelForwarder(
                (db.ssh_host, db.ssh_port),
                ssh_username=db.ssh_user,
                ssh_pkey=db.private_key,
                remote_bind_address=(db.mysql_host, db.mysql_port)) as tunnel:
            # connect to the MySQL server through the SSH tunnel
            mysql_conn = pymysql.connect(
                host='localhost', # will be due to the SSH tunneling issue
                port=tunnel.local_bind_port,
                user=db.mysql_user,
                password=db.mysql_password,
                db=db.mysql_db
            )

            # send a query to the MySQL database and print the response table
            with mysql_conn.cursor() as cursor:
                query = f'SELECT * FROM {dbTableName} WHERE username = "{username}";'
                cursor.execute(query)
                rows = cursor.fetchall()

                messages = [(message[2],message[3]) for message in rows]

            # close the MySQL connection
            mysql_conn.close()

        # close the SSH client
        db.ssh_client.close()
        return messages
    def setmessages(db,username, message_text="", bot_reply=""):
        # Adding the record into the database
        with SSHTunnelForwarder(
                (db.ssh_host, db.ssh_port),
                ssh_username=db.ssh_user,
                ssh_pkey=db.private_key,
                remote_bind_address=(db.mysql_host, db.mysql_port)) as tunnel:
            # connect to the MySQL server through the SSH tunnel
            mysql_conn = pymysql.connect(
                host='localhost', # will be due to the SSH tunneling issue
                port=tunnel.local_bind_port,
                user=db.mysql_user,
                password=db.mysql_password,
                db=db.mysql_db
            )

            # send a query to the MySQL database and print the response table
            with mysql_conn.cursor() as cursor:
                query = f"INSERT INTO {dbTableName} (username,message_text,bot_reply) " \
                        f"VALUES ('{username}','{message_text}','{bot_reply}');"
                cursor.execute(query)
                mysql_conn.commit()

            # close the MySQL connection
            mysql_conn.close()

        # close the SSH client
        db.ssh_client.close()
    def cleanup(db, username = "", remaining_messages = config.remaining_messages):
        # Cleanup the records, except the last N rows
        with SSHTunnelForwarder(
                (db.ssh_host, db.ssh_port),
                ssh_username=db.ssh_user,
                ssh_pkey=db.private_key,
                remote_bind_address=(db.mysql_host, db.mysql_port)) as tunnel:
            # connect to the MySQL server through the SSH tunnel
            mysql_conn = pymysql.connect(
                host='localhost',  # will be due to the SSH tunneling issue
                port=tunnel.local_bind_port,
                user=db.mysql_user,
                password=db.mysql_password,
                db=db.mysql_db
            )

            # send a query to the MySQL database to delete the records except the last ones
            with mysql_conn.cursor() as cursor:

                query = f"DELETE FROM {dbTableName} WHERE username = '{username}' AND id NOT IN " \
                        f"(SELECT id FROM (SELECT id FROM (SELECT id FROM {dbTableName} " \
                        f"WHERE username = '{username}' ORDER BY id DESC LIMIT {remaining_messages}) " \
                        f"subquery) subsubquery)"
                cursor.execute(query)
                mysql_conn.commit()

            # close the MySQL connection
            mysql_conn.close()

        # close the SSH client
        db.ssh_client.close()

    def deleteDuplicates(db):
        # Deletes all the duplicate records
        with SSHTunnelForwarder(
                (db.ssh_host, db.ssh_port),
                ssh_username=db.ssh_user,
                ssh_pkey=db.private_key,
                remote_bind_address=(db.mysql_host, db.mysql_port)) as tunnel:
            # connect to the MySQL server through the SSH tunnel
            mysql_conn = pymysql.connect(
                host='localhost',  # will be due to the SSH tunneling issue
                port=tunnel.local_bind_port,
                user=db.mysql_user,
                password=db.mysql_password,
                db=db.mysql_db
            )

            # send a query to the MySQL database to delete the records except the last ones
            with mysql_conn.cursor() as cursor:

                query = f"DELETE c1 FROM {dbTableName} c1, {dbTableName} c2 WHERE " \
                        f"c1.id > c2.id AND c1.username = c2.username " \
                        f"AND c1.message_text = c2.message_text;"
                cursor.execute(query)
                mysql_conn.commit()

            # close the MySQL connection
            mysql_conn.close()

        # close the SSH client
        db.ssh_client.close()

if __name__ == '__main__':
    pass
    """
    #This is for testing purpose only:
    username = 'u1'
    db = DataBase()
    db.setmessages(username='user2',message_text='some message',bot_reply='some reply')
    db.cleanup(username='user2',remaining_messages=1)
    db.deleteDuplicates()
    messages = db.getmessages(username)
    for message in messages:
        print(message[0]+' '+message[0]+' ')
    """