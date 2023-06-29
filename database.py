import urllib.parse as up
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
path_to_db_bot = os.getenv('path_to_db_bot')

up.uses_netloc.append("postgres")
url = up.urlparse(path_to_db_bot)
connection = psycopg2.connect(database=url.path[1:],
                              user=url.username,
                              password=url.password,
                              host=url.hostname,
                              port=url.port)

cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id BIGINT, balance INT)')
connection.commit()
cursor.close()
