import instaloader
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import pandas as pd
import numpy as np
from time import sleep
from src.Database.Database import Database


def content_retrieval():

    L = instaloader.Instaloader()
    database = None

    try:
        database = Database()
    except Exception as exception:
        print("Error Establishing Connection to Database:\n\n", exception)

    # get source IDs and usernames from database
    # returns format [content_source_id, content_source_username]
    content_source_info = database.select_content_sources()

    username_to_id = {}
    for source in content_source_info:
        content_source_id = source[0]
        content_username = source[1]

        username_to_id[content_username] = content_source_id

        # # get posts from two days ago to yesterday
        since = datetime.now() + timedelta(days=-2)
        until = datetime.now() + timedelta(days=-1)

        # to store post information
        data_columns = ['username', 'likes_per_follower', 'post_id', 'url']
        new_posts = pd.DataFrame(columns=list(data_columns))

        # check each user
        i = 0
        for source in content_source_info:

            source_id = source[0]
            username = source[1]

        profile = instaloader.Profile.from_username(L.context, username)
        follower_count = profile.followers

        # check user's posts, save pictures
        posts = profile.get_posts()
        for post in takewhile(lambda p: p.date > since,
                              dropwhile(lambda p: p.date > until, posts)):
            if post.typename == 'GraphImage':
                new_posts.loc[i] = [
                    post.owner_username, post.likes / follower_count,
                    post.mediaid, post.url
                ]
                i = i + 1
        # instagram gets cranky when tired
        sleep(1)

    # find top three new posts
    new_posts = new_posts.sort_values('likes_per_follower', ascending=False)
    new_posts = new_posts.iloc[0:3, :]

    usernames = []
    photo_urls = []

    for username in new_posts["username"].values:
        usernames.append(username)

    for url in new_posts["url"].values:
        photo_urls.append(url)

    # get content_source_id and insert url, ID to database
    for username, url in zip(usernames, photo_urls):
        source_id = username_to_id[username]
        database.insert_new_photo(url, source_id)