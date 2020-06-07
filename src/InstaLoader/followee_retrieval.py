import instaloader
import pandas as pd
from time import sleep
from src.Database.Database import Database
from datetime import datetime
from emailServices.notify_email import notify_email


def notifyJobFinish():

    message = "Followee Retrieval finished without errors at " + str(
        datetime.now())

    notify_email(message)


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


def followee_retrieval():

    L = instaloader.Instaloader()
    request_count = 0

    # establish database connection
    database = None

    try:
        database = Database()
    except Exception as exception:
        print(
            "followee_retrieval: Error establishing a connection to the database..."
        )
        return

    print("Established Database...")

    # gets content sources from the database
    NUM_CONTENT_SOURCES = 1
    content_source_info = database.select_limit_content_source_rand(
        NUM_CONTENT_SOURCES)
    content_source_username = ""
    if (content_source_info):
        content_source_username = content_source_info[1]
    else:
        return

    # to store post information
    data_columns = [
        'username', 'user id', 'followers count', 'following count',
        'is private'
    ]
    new_followees = pd.DataFrame(columns=list(data_columns))

    total_new_followees = 100

    i = 0

    print("Getting profile information...")

    try:
        profile = instaloader.Profile.from_username(L.context,
                                                    content_source_username)
    except Exception as exception:
        print(exception)
        return

    request_count = request_rate_control(request_count)

    print("Getting Posts...")
    posts = profile.get_posts()
    request_count = request_rate_control(request_count)

    print("Posts received")

    #print("Number of Posts:", len(list(posts)))

    for post in posts:
        likers = (post.get_likes())
        request_count = request_rate_control(request_count)

        #print("Number of Likers: ", len(list(likers)))

        for liker in likers:
            request_count = request_rate_control(request_count)
            print(datetime.now(), "Username")
            username = liker.username
            print(datetime.now(), " User ID")
            user_id = liker.userid
            print(datetime.now(), "User Followers")
            followers_count = liker.followers
            print(datetime.now(), "User Followees")
            following_count = liker.followees
            print(datetime.now(), "User State")
            is_private = liker.is_private

            print(datetime.now(), "all liker information finished...")

            print("Inserting New Follower to Database...")
            database.insert_new_follower(user_id, username, followers_count,
                                         following_count, is_private)
            i += 1
            print("i:", i)

            if i >= total_new_followees:

                # Final Wait Period before the retrieval of content begins
                final_wait_period = 400

                print("Followee Retrieval Finished, waiting ",
                      final_wait_period, "seconds...")
                sleep(final_wait_period)
                return
