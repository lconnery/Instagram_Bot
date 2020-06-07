import os
from multiprocessing import Process
from dotenv import load_dotenv
import sys
import schedule
import time
from datetime import datetime, timedelta
from src.Database.Database import Database

# email services
from emailServices.notify_email import notify_email

# load environment variables
load_dotenv()

# import files from different directory
from src.InstaBot.InstagramBot import InstagramBot

sys.path.append('./src/InstaLoader')
from src.InstaLoader.content_retrieval import content_retrieval
from src.InstaLoader.followee_retrieval import followee_retrieval

FOLLOWEE_RETRIEVAL_TIME = "01:00"
CONTENT_RETRIEVAL_TIME = "04:00"
INSTA_BOT_SCHEDULE_TIME = "09:00"
EMAIL_DAILY_SUPPLY_EMAIL = "08:00"


def notify_daily_metrics():
    try:
        database = Database()
    except Exception as exception:
        print(exception)
        return

    # get current photo supply
    photo_supply = database.getPhotoSupply()

    # get current caption supply
    caption_supply = database.getCaptionSupply()

    # get follower supply
    follower_supply = database.getFollowerSupply()

    # get prev day follow successes
    num_days_ago = 1
    target_date = datetime.today() - timedelta(days=int(num_days_ago))
    target_year = target_date.year
    target_month = target_date.month
    target_day = target_date.day

    prev_day_follow_success = database.getPreviousDayFollowers(
        target_day, target_month, target_year)

    message = "Current Photo Supply:     " + str(photo_supply) + "</p>"
    message = message + "<p>Caption Supply:     " + str(
        caption_supply) + "</p>"
    message = message + "<p>Follower Supply:     " + str(
        follower_supply) + "</p>"
    message = message + "<p>Number of New Followers:     " + str(
        prev_day_follow_success) + "</p>"

    notify_email(message)


if __name__ == "__main__":

    # Set up bot schedule
    instagramBot = InstagramBot()

    schedule.every().day.at(INSTA_BOT_SCHEDULE_TIME).do(
        instagramBot.setup_schedule)

    schedule content retrieval
    schedule.every().day.at(FOLLOWEE_RETRIEVAL_TIME).do(followee_retrieval)
    schedule.every().day.at(CONTENT_RETRIEVAL_TIME).do(content_retrieval)
    schedule.every().day.at(EMAIL_DAILY_SUPPLY_EMAIL).do(notify_daily_metrics)

    success_setup_message = "Silvia Brown is successfully online. The scheduled time for followee retrieval, content retrieval, and posting actions are " + FOLLOWEE_RETRIEVAL_TIME + ", " + CONTENT_RETRIEVAL_TIME + ", and " + INSTA_BOT_SCHEDULE_TIME + " respectively."

    notify_email(success_setup_message)

    while 1:
        schedule.run_pending()
        time.sleep(1)