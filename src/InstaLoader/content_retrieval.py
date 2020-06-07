import instaloader
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import pandas as pd
import numpy as np
from time import sleep
from src.Database.Database import Database
from emailServices.notify_email import notify_email


# email to notify content retrieval is finished
def notifyJobFinish():

    message = "Content Retrieval finished without errors at " + str(
        datetime.now())

    notify_email(message)


# function to keep track of and slow down the rate of requests made
# to instagram
def request_rate_control(request_count):

    request_count = request_count + 1

    # number of seconds to wait after last request
    wait_period = 0

    if (request_count % 10 == 0):
        wait_period = 400
    else:
        wait_period = 40

    print("After last request, the delay will be", wait_period)

    sleep(wait_period)

    print("request delay over, starting process again...")

    return request_count


def content_retrieval():

    L = instaloader.Instaloader()
    database = None

    request_count = 0

    try:
        database = Database()
    except Exception as exception:
        print("Error Establishing Connection to Database:\n\n", exception)

    # get source IDs and usernames from database
    # returns format [content_source_id, content_source_username]
    content_source_info = database.select_content_sources()

    print("Number of Content Sources: ", len(content_source_info))

    j = 0

    # get posts from two days ago to yesterday
    since = datetime.now() + timedelta(days=-2)
    until = datetime.now() + timedelta(days=-1)

    # to store post information
    data_columns = ['username', 'likes_per_follower', 'post_id', 'url']
    new_posts = pd.DataFrame(columns=list(data_columns))

    i = 0  # number of posts currently found
    k = 0  # number of sources covered so far

    username_to_id = {}

    for source in content_source_info:

        k = k + 1
        print("\n\nStarting Content Source #", k)

        content_source_id = source[0]
        content_username = source[1]

        username_to_id[content_username] = content_source_id

        print("Gathering Profile...")
        try:
            profile = instaloader.Profile.from_username(
                L.context, content_username)
        except Exception as exception:
            print("Problem finding", content_username, "...")
            print(exception)
            continue

        request_count = request_rate_control(request_count)

        follower_count = profile.followers
        print("Profile: ", content_username)
        print("Follower Count: ", follower_count)
        request_count = request_rate_control(request_count)

        # check user's posts, save pictures
        print("Gathering Posts from Profile...")
        posts = profile.get_posts()
        request_count = request_rate_control(request_count)

        for post in takewhile(lambda p: p.date > since,
                              dropwhile(lambda p: p.date > until, posts)):
            if post.typename == 'GraphImage':
                new_posts.loc[i] = [
                    post.owner_username, post.likes / follower_count,
                    post.mediaid, post.url
                ]
                i = i + 1
                print("Viable post found, count is now ", i)
                request_count = request_rate_control(request_count)

            # instagram gets cranky when tired
            j = j + 1
            print("J: ", j)
            request_count = request_rate_control(request_count)

    # find top n new posts
    n = 5  # number of posts to save

    if (i < n):
        n = i

    new_posts = new_posts.sort_values('likes_per_follower', ascending=False)
    new_posts = new_posts.iloc[0:n, :]

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