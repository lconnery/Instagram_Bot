import psycopg2 as pg
import sys
import os
import glob
from src.Database.Database import Database


def upload_content():
    content_source_file = open('./utils/ig_users.txt')
    content_sources = content_source_file.read().split("\n")

    # captions
    caption_source_file = open('./utils/captions.csv', 'r')
    caption_source = caption_source_file.read().split(',\n')

    # hashtags
    hashtag_source_file = open('./utils/hashtags.csv', 'r')
    hashtag_source = hashtag_source_file.read().split(' ')

    # establish connection to the database
    database = None

    try:
        database = Database()
    except Exception as exception:
        print("Error Establishing Connection to Database:\n\n", exception)
        return

    # upload content sources to database
    for source in content_sources:
        database.insert_new_content_source(source)

    for caption in caption_source:
        database.insert_new_caption(caption)

    for hashtag in hashtag_source:
        database.insert_new_hashtag(hashtag)


# clear PostStaging folder for testing
files_to_delete = glob.glob('./PostStaging/DailyContent/*')
for file in files_to_delete:
    os.remove(file)

if (len(sys.argv) < 2):
    print(
        "Usage: python3 ConfigureDatabase [argument init, drop, or content]\n       - init establishes database tables (also runs 'content')\n       - drop removes database tables\n       - content uploads content sources found in './utils/ig_users.txt' to the database"
    )
    exit()

command = sys.argv[1]

if (command != "init" and command != "drop" and command != "content"):
    print(
        "Usage: python3 ConfigureDatabase [argument init or drop]\n       - init establishes database tables (also runs 'content')\n       - drop removes database tables\n       - content uploads content sources found in './utils/ig_users.txt' to the database"
    )
    exit()

try:
    connection = pg.connect(database="database",
                            user='postgres',
                            password='password',
                            host="localhost",
                            port=5432)
except:
    print("Unable to connect to 'database' on port '5432")

cursor = connection.cursor()

sql_file = None

if (command == "init"):
    # initialize tables
    sql_file = open('./DatabaseScripts/initializeTables.sql', 'r')

elif (command == "content"):
    upload_content()
    exit()

else:
    # drop tables
    sql_file = open('./DatabaseScripts/dropTables.sql', 'r')

try:
    cursor.execute(sql_file.read())
except:
    print("Drop/Init SQL query failed")

connection.commit()  # <--- makes sure the change is shown in the database
connection.close()
cursor.close()

if (command == "init"):
    upload_content()
