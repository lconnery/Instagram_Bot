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

        sql_file = open('./DatabaseScripts/Insert/insertNewPhoto.sql', 'r')
        query = sql_file.read()
        values = (photo_url, content_source_id)

        result = self.execute_query(query, values)

        return result

    def insert_new_content_source(self, content_source_username) -> str:
        sql_file = open('./DatabaseScripts/Insert/insertNewContentSource.sql',
                        'r')
        query = sql_file.read()
        values = (content_source_username, )

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_id = self.cursor.fetchone()[0]
            return content_source_id

        return None

    def insert_new_caption(self, caption) -> str:
        sql_file = open('./DatabaseScripts/Insert/insertNewCaption.sql', 'r')
        query = sql_file.read()
        values = (caption, )

        query_result = self.execute_query(query, values)

        if (query_result):
            caption_id = self.cursor.fetchone()[0]
            return caption_id

        return None

    def insert_new_hashtag(self, hashtag) -> str:
        sql_file = open('./DatabaseScripts/Insert/insertNewHashtag.sql', 'r')
        query = sql_file.read()
        values = (hashtag, )

        query_result = self.execute_query(query, values)

        if (query_result):
            hashtag_id = self.cursor.fetchone()[0]
            return hashtag_id

        return None

    def insert_url_issue(self, photo_id, issue_desc):
        sql_file = open('./DatabaseScripts/Insert/insertURLIssue.sql', 'r')
        query = sql_file.read()
        values = (photo_id, issue_desc)

        query_result = self.execute_query(query, values)

    def insert_new_post(self, instagram_id, photo_id, content_source_id,
                        caption_id) -> str:
        sql_file = open('./DatabaseScripts/Insert/insertNewPost.sql', 'r')
        query = sql_file.read()
        values = (instagram_id, photo_id, content_source_id, caption_id)

        query_result = self.execute_query(query, values)

        if (query_result):
            new_post_id = self.cursor.fetchone()
            if (new_post_id):
                return new_post_id[0]

        return None

    def insert_new_hashtag_log(self, photo_id, hashtag_id) -> bool:
        sql_file = open('./DatabaseScripts/Insert/insertHashtagLog.sql', 'r')
        query = sql_file.read()
        values = (photo_id, hashtag_id)

        query_result = self.execute_query(query, values)

        if (query_result):
            return True

        return False

    def insert_new_follower(self, instagram_uuid, follower_username,
                            num_followers, num_following, is_public) -> str:
        sql_file = open(
            './DatabaseScripts/Insert/Followers/insertNewFollower.sql', 'r')
        query = sql_file.read()
        values = (instagram_uuid, follower_username, num_followers,
                  num_following, is_public)

        query_result = self.execute_query(query, values)

        if (query_result):
            follower_id = self.cursor.fetchall()
            if (follower_id):
                return follower_id[0]

        return None

    def insert_new_follower_request(self, follower_id) -> bool:
        sql_file = open(
            './DatabaseScripts/Insert/Followers/insertNewFollowRequest.sql',
            'r')
        query = sql_file.read()
        values = (follower_id, )

        query_result = self.execute_query(query, values)

        if (query_result):
            return True

        return False

    def insert_new_follower_success(self, follower_id) -> bool:
        sql_file = open(
            './DatabaseScripts/Insert/Followers/insertNewFollowSuccess.sql',
            'r')
        query = sql_file.read()
        values = (follower_id, )

        query_result = self.execute_query(query, values)

        if (query_result):
            return True

        return False

    def get_content_source_id(self, content_source_username):
        sql_file = open('./DatabaseScripts/Select/selectContentSourceID.sql',
                        'r')
        query = sql_file.read()
        values = (content_source_username, )

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_id = self.cursor.fetchone()
            if (content_source_id):
                content_source_id = content_source_id[0]
                return content_source_id

        return None

    def select_content_sources(self):
        sql_file = open(
            './DatabaseScripts/Select/Content/selectContentSource.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_info = self.cursor.fetchall()

            return content_source_info

        return None

    def select_limit_content_source_rand(self, amount):
        sql_file = open(
            './DatabaseScripts/Select/Content/selectContentSourceRand.sql',
            'r')
        query = sql_file.read()
        values = (amount, )

        query_result = self.execute_query(query, values)

        if (query_result):
            content_source_info = self.cursor.fetchall()

            return content_source_info[0]

        return None

    def get_photo_for_posting(self):

        # select row from photos table
        sql_file = open('./DatabaseScripts/Select/selectPhotoForPosting.sql',
                        'r')
        query = sql_file.read()

        query_result = self.execute_query(query, None)

        post_photo_info = None
        if (query_result):
            post_photo_info = self.cursor.fetchall()
            if (post_photo_info):
                post_photo_info = post_photo_info[0]
            else:
                return None
        else:
            return post_photo_info

        # update photos table to show this picture has be used
        photo_id = post_photo_info[0]

        sql_file = open('./DatabaseScripts/Update/updatePostedPhotoFlag.sql',
                        'r')
        query = sql_file.read()
        values = (photo_id, )

        query_result = self.execute_query(query, values)

        return post_photo_info

    def select_daily_follows(self, batch_size):
        sql_file = open(
            './DatabaseScripts/Select/Followers/selectDailyFollows.sql', 'r')
        query = sql_file.read()
        values = (batch_size, )

        query_result = self.execute_query(query, values)

        if (query_result):
            daily_follow_info = self.cursor.fetchall()
            if (daily_follow_info):
                return daily_follow_info

        return None

    def select_past_follow_requests(self, day, month, year):
        sql_file = open(
            './DatabaseScripts/Select/Followers/selectFollowersFromDate.sql',
            'r')
        query = sql_file.read()
        values = (year, month, day)

        query_result = self.execute_query(query, values)

        if (query_result):
            past_follow_info = self.cursor.fetchall()
            if (past_follow_info):
                return past_follow_info

        return None

    def select_caption(self):
        sql_file = open('./DatabaseScripts/Select/selectCaptionRand.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        caption_info = None
        if (query_result):
            caption_info = self.cursor.fetchall()
            if (caption_info):
                caption_info = caption_info[0]
            else:
                return None
        else:
            return None

        caption_id = caption_info[0]

        # need to mark that the caption has been used
        sql_file = open('./DatabaseScripts/Update/updatePostedCaptionFlag.sql',
                        'r')
        query = sql_file.read()
        values = (caption_id, )

        query_result = self.execute_query(query, values)

        return caption_info

    def select_hashtag_cluster(self):
        sql_file = open('./DatabaseScripts/Select/selectHashtagsRand.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        if (query_result):
            hashtag_info = self.cursor.fetchall()
            if (hashtag_info):
                return hashtag_info

        return None

    def getPhotoSupply(self):
        sql_file = open('./DatabaseScripts/Metrics/getPhotoSupply.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        if (query_result):
            supply_info = self.cursor.fetchone()
            if (supply_info):
                return supply_info[0]

        return None

    def getCaptionSupply(self):
        sql_file = open('./DatabaseScripts/Metrics/getCaptionSupply.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        if (query_result):
            supply_info = self.cursor.fetchone()
            if (supply_info):
                return supply_info[0]

    def getFollowerSupply(self):
        sql_file = open('./DatabaseScripts/Metrics/getFollowerSupply.sql', 'r')
        query = sql_file.read()
        values = None

        query_result = self.execute_query(query, values)

        if (query_result):
            supply_info = self.cursor.fetchone()
            if (supply_info):
                return supply_info[0]

    def getPreviousDayFollowers(self, day, month, year):
        sql_file = open('./DatabaseScripts/Metrics/getPreviousDayFollower.sql',
                        'r')
        query = sql_file.read()
        values = (year, month, day)

        query_result = self.execute_query(query, values)

        if (query_result):
            supply_info = self.cursor.fetchone()
            if (supply_info):
                return supply_info[0]
