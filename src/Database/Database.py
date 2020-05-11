import psycopg2 as pg


class Database(object):

    connection: any = None
    cursor: any = None

    def __init__(self) -> None:

        # establish connection
        self.connection = pg.connect(database="database",
                                     user='postgres',
                                     password='password',
                                     host="localhost",
                                     port=5432)

        self.cursor = self.connection.cursor()

    def execute_query(self, query, values) -> bool:
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except Exception as exception:
            print("Problem with execution of query: \n\n", exception)
            return False

        return True

    def insert_new_photo(self, photo_url, content_source_id) -> bool:

        sql_file = open('./DatabaseScripts/insertNewPhoto.sql', 'r')
        query = sql_file.read()
        values = (photo_url, content_source_id)

        result = self.execute_query(query, values)

        return result

    def insert_new_content_source(self, content_source_username) -> str:
        sql_file = open('./DatabaseScripts/insertNewContentSource.sql', 'r')
        query = sql_file.read()
        values = (content_source_username, )

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_id = self.cursor.fetchone()[0]
            return content_source_id

        return None

    def insert_new_caption(self, caption) -> str:
        sql_file = open('./DatabaseScripts/insertNewCaption.sql', 'r')
        query = sql_file.read()
        values = (caption, )

        query_result = self.execute_query(query, values)

        if (query_result):
            caption_id = self.cursor.fetchone()[0]
            return caption_id

        return None

    def get_content_source_id(self, content_source_username):
        sql_file = open('./DatabaseScripts/Select/selectContentSourceID.sql',
                        'r')
        query = sql_file.read()
        values = (content_source_username, )

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_id = self.cursor.fetchone()[0]
            return content_source_id

        return None