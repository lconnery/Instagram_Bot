from instabot import Bot
import random
import os
from src.Database.Database import Database
import urllib.request
import schedule
from datetime import datetime, timedelta


class InstagramBot(object):

    database = None
    bot = None

    def __init__(self):
        try:
            self.database = Database()
        except Exception as exception:
            print("Issue initializing database: ", exception)

        num_follows = int(os.getenv('NUM_DAILY_FOLLOWS', 100))

        self.bot = Bot(max_follows_per_day=num_follows,
                       max_unfollows_per_day=num_follows)
        self.bot.login()

    def setup_schedule(self):
        self.start_content_posting()
        self.start_follow_routine()

    def start_follow_routine(self):

        # looking back
        num_days = os.getenv('FOLLOW_WAIT_PERIOD_IN_DAYS', 2)
        num_days = 0
        past_requested_users_info = self.get_past_requests_to_follow(num_days)

        # get a list of the current users following the account
        current_followers_uuid = self.get_current_followers()

        num_unfollows = len(past_requested_users_info)
        unfollow_times = self.follow_routine_schedule(num_unfollows)

        # insert follow backs to follow_success in the database
        for follower_info in past_requested_users_info:
            follower_id = follower_info[0]
            instagram_uuid = follower_info[1]

            if (instagram_uuid in current_followers_uuid):
                self.database.insert_new_follower_success(follower_id)

            # unfollow each of the users that were requested n days ago
            unfollow_instance = unfollow_times.pop()

            schedule.every().day.at(unfollow_instance).do(
                self.unfollow_user, instagram_uuid)

        # Next Batch: Get number of follows for the day and list of users to follow
        NUM_DAILY_FOLLOWS = int(os.getenv('NUM_DAILY_FOLLOWS', 300))
        daily_follow_info = self.database.select_daily_follows(
            NUM_DAILY_FOLLOWS)

        # get an time at which to follow each of the users
        follow_instances = self.follow_routine_schedule(NUM_DAILY_FOLLOWS)

        # schedule a job to follow each user and record in the database that
        # they have been requested
        for account, instance in zip(daily_follow_info, follow_instances):
            follower_id = account[0]
            instagram_uuid = account[1]
            bot.follow(instagram_uuid)
            schedule.every().day.at(instance).do(self.follow_user, follower_id,
                                                 instagram_uuid)

    def follow_user(self, follower_id, instagram_uuid):
        bot.follow(instagram_uuid)
        self.database.insert_new_follower_request(follower_id)

        return schedule.CancelJob

    def unfollow_user(self, instagram_uuid):
        bot.unfollow(instagram_id)
        return schedule.CancelJob

    # returns [] with instagram_uuid's of current followers of the account
    def get_current_followers(self):
        current_followers = self.bot.followers

        return current_followers

    def get_past_requests_to_follow(self, num_days_ago):
        target_date = datetime.today() - timedelta(days=int(num_days_ago))
        target_year = target_date.year
        target_month = target_date.month
        target_day = target_date.day

        past_follow_info = self.database.select_past_follow_requests(
            target_day, target_month, target_year)

        return past_follow_info

    # returns list of str in the format 'HH:MM:SS'
    def follow_routine_schedule(self, num_instances):
        instances = []
        FOLLOW_PERIOD_START = os.getenv('FOLLOW_PERIOD_BEGIN', '05:00:00')
        period_start_parts = FOLLOW_PERIOD_START.split(":")
        hours_base = int(period_start_parts[0])
        minute_base = int(period_start_parts[1])
        seconds_base = int(period_start_parts[2])

        FOLLOW_PERIOD_IN_SEC = int(
            os.getenv('FOLLOW_PERIOD_LENGTH_IN_SEC', 25000))
        for i in range(0, num_instances):
            # generate
            num_seconds = random.randint(0, FOLLOW_PERIOD_IN_SEC)
            seconds_place = int(num_seconds % 60)
            minutes_place = int((num_seconds / 60) % 60)
            hours_place = int(((num_seconds / 60) / 60) % 60)

            # add new time places to start time base
            hours_place = hours_base + hours_place
            if (hours_place < 10):
                hours_place = "0" + str(hours_place)

            minutes_place = minute_base + minutes_place
            if (minutes_place < 10):
                minutes_place = "0" + str(minutes_place)

            seconds_place = seconds_base + seconds_place
            if (seconds_place < 10):
                seconds_place = "0" + str(seconds_place)

            current_instance = str(hours_place) + ":" + str(
                minutes_place) + ":" + str(seconds_place)
            instances.append(current_instance)

        return instances

    def start_content_posting(self):
        num_posts = self.decide_num_posts()

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

        photo_id = ""
        photo_url = ""

        if (post_content == None):
            print("Couldn't find URLs")
        else:
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

        photo_id = photo_info[0]
        photo_address = "./PostStaging/DailyContent/" + photo_id + ".jpg"

        caption_file_address = "./PostStaging/DailyContent/" + photo_id + ".txt"
        caption_file = open(caption_file_address, 'r')
        caption = caption_file.read()

        # instabot does its thing here
        some_id = bot.upload_photo(photo_address, caption)

        instagram_id = "instagram_id (temp)"

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