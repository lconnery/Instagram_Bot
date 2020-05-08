import psycopg2 as pg
import sys

if (len(sys.argv) < 2):
    print(
        "Usage: python3 ConfigureDatabase [argument init or drop]\n       - init establishes database tables\n       - drop removes database tables"
    )
    exit()

command = sys.argv[1]

if (command != "init" and command != "drop"):
    print(
        "Usage: python3 ConfigureDatabase [argument init or drop]\n       -init establishes database tables\n       -drop removes database tables"
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
else:
    # drop tables
    sql_file = open('./DatabaseScripts/dropTables.sql', 'r')

try:
    cursor.execute(sql_file.read())
except:
    print("SQL query failed")

connection.commit()  # <--- makes sure the change is shown in the database
connection.close()
cursor.close()