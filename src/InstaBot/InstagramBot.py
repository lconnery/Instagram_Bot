import glob
import os
import sys
import time
from io import open

from instabot import Bot
from src.Database.Database import Database


class InstagramBot(object):

    database = None

    def __init__(self):
        try:
            self.database = Database()
        except Exception as exception:
            print("Issue initializing database: ", exception)

        hashtag_id = self.database.insert_new_hashtag('#interiorDesign')
        print("hash_id: ", hashtag_id)

    def setup_schedule():
        
    
    def decide_on_posts():