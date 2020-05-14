from instabot import Bot
import random
import os
from src.Database.Database import Database
import urllib.request
import schedule
import datetime


class InstagramBot(object):

    database = None

    def __init__(self):
        try:
            self.database = Database()
        except Exception as exception:
            print("Issue initializing database: ", exception)

        self.setup_schedule()

    def setup_schedule(self):
        num_posts = self.decide_num_posts()
        print("Number of Posts: ", num_posts)

        post_times = []

        # select n post times
        for i in range(0, num_posts):
            post_time = self.get_post_time()

            # ensure that each new post time is not within min minutes of another post time
            MIN_POST_PERIOD: int = int(os.getenv('MIN_POST_PERIOD', 20))
            for x in post_times:

                current_post_time_compare = int(post_time.replace(":", ""))
                temp_post_time_compare = int(x.replace(":", ""))

                while (abs(current_post_time_compare - temp_post_time_compare)
                       < MIN_POST_PERIOD):
                    post_time = self.get_post_time()
                    current_post_time_compare = int(post_time.replace(":", ""))

            post_times.append(post_time)

        for post_time in post_times:

            # download selected photo, tuple in the form (photo_id, photo_url, content_source_id, photo_credits)
            photo_info = self.select_photo()
            photo_id = photo_info[0]
            photo_credits = photo_info[3]

            #(caption_id, caption)
            caption_info = self.get_caption()
            caption = caption_info[1]

            # select hashtags
            # array of tuples in the form (hashtag_id, hashtag)
            hashtag_info = self.get_hashtags()
            hashtag_string = ""
            for x in hashtag_info:
                hashtag_string = hashtag_string + x[1]

            # combine caption, credit, and hastags into txt file titled with photo id
            base_caption_file = open('./PostStaging/captionBase.txt', 'r')
            base_caption = base_caption_file.read()
            base_caption_file.close()

            final_caption = base_caption.replace("%c", caption)
            final_caption = final_caption.replace("%r", photo_credits)
            final_caption = final_caption.replace("%h", hashtag_string)

            final_caption_file_location = "./PostStaging/DailyContent/" + photo_id + ".txt"
            final_caption_file = open(final_caption_file_location, 'w')

            final_caption_file.write(final_caption)
            final_caption_file.close()

            # schedule job at post_time[i] with argument of photo_id
            schedule.every().day.at(post_time).do(self.post_photo, photo_info,
                                                  caption_info, hashtag_info)

            print("Post Time: ", post_time)

    # number between 1 and n
    def decide_num_posts(self) -> int:
        # default number of posts a day is 3
        MAX_NUM_POSTS: int = int(os.getenv('NUM_DAILY_POSTS_MAX', 3))
        MIN_NUM_POSTS: int = int(os.getenv('NUM_DAILY_POSTS_MIN', 3))

        number_of_posts = random.randint(MIN_NUM_POSTS, MAX_NUM_POSTS)

        return number_of_posts

    # get urls from database
    # returns tuple in the form of (photo_id, photo_url, content_source_username)
    def select_photo(self):

        # tuple format (photo_id, photo_url, content_source_id, content_source_username)
        post_content = self.database.get_photo_for_posting()

        if (post_content == None):
            print("Couldn't find URLs")
            exit()

        photo_id = post_content[0]
        photo_url = post_content[1]

        # attempt to download photo, if it fails get another photo and try again
        while (self.download_photo(photo_id, photo_url) == False):

            # upon failure of download, register issue in database table (url_invalid)
            issue_desc = "Problem downloading URL"
            self.database.insert_url_issue(photo_id, issue_desc)

            post_content = self.database.get_photo_for_posting()

            if (post_content == None):
                # raise alert
                print("Couldn't find any more URLs")
                return None

            photo_id = post_content[0]
            photo_url = post_content[1]

        return post_content

    # download photo via urls to staging directory
    def download_photo(self, photo_id, photo_url) -> bool:

        photo_location = "./PostStaging/DailyContent/" + photo_id + ".jpg"
        try:
            urllib.request.urlretrieve(photo_url, photo_location)
        except Exception as exception:
            print("Error with downloading URL: \n\n", exception)
            return False

        return True

    # get caption from database
    # returns tuple in the form of (caption_id, caption)
    def get_caption(self):
        caption_info = self.database.select_caption()
        if (caption_info):
            return caption_info

        return None

    # returns a string for the scheduled time for the post
    # format is 'HH:MM' where HH is in range 0-24
    def get_post_time(self) -> str:
        peak_post_base = os.getenv('PEAK_HOURS_START', '10:00')
        base_split = peak_post_base.split(':')

        hours_place = int(base_split[0])
        minutes_place = int(base_split[1])

        post_offset = self.decide_post_time_offset()
        hours_offset = int(post_offset / 60)
        minutes_offset = int(post_offset % 60)

        hours_place = hours_place + hours_offset
        minutes_place = minutes_place + minutes_offset

        # add leading 0 to minutes values less than 10
        if (minutes_place < 10):
            minutes_place = "0" + str(minutes_place)

        post_time = str(hours_place) + ":" + str(minutes_place) + ":00"

        return post_time

    # randomly decide on number between 0 and length of peak hours in minutes
    def decide_post_time_offset(self) -> int:
        duration_of_peak = int(os.getenv('PEAK_LEN_MIN', 540))

        return random.randint(0, duration_of_peak)

    def get_hashtags(self):
        hashtag_info = self.database.select_hashtag_cluster()
        if (hashtag_info):
            return hashtag_info

        return None

    # post photo via instabot
    def post_photo(self, photo_info, caption_info, hashtag_info):

        print(datetime.datetime.now(), " begin posting photo...")

        photo_id = photo_info[0]
        photo_address = "./PostStaging/DailyContent/" + photo_id + ".jpg"

        caption_file_address = "./PostStaging/DailyContent/" + photo_id + ".txt"
        caption_file = open(caption_file_address, 'r')
        caption = caption_file.read()

        # instabot does its thing here
        # bot = InstaBot()
        # bot.login()
        # some_id = bot.post(photo, caption)

        instagram_id = "TEST_INSTAGRAM_ID"

        # add post information into post
        # returns the uuid for that specific post, used in hashtag_log
        # (uuid, instagram_id, timestamp, photo_id, content_source_id, caption_id)
        content_source_id = photo_info[2]
        caption_id = caption_info[0]

        post_id = self.database.insert_new_post(instagram_id, photo_id,
                                                content_source_id, caption_id)

        # add hashtag log information
        # (hashtag_id, photo_id)
        for hashtag in hashtag_info:
            hashtag_id = hashtag[0]
            insert_result = self.database.insert_new_hashtag_log(
                photo_id, hashtag_id)

            if (insert_result == False):
                print("Issue logging hashtag: ", hashtag_id, hashtag[1])

        return schedule.CancelJob