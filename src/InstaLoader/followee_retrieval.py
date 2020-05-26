import instaloader
import pandas as pd
from time import sleep
from src.Database.Database import Database


def followee_retrieval():

    L = instaloader.Instaloader()

    # establish database connection
    database = None

    try:
        database = Database()
    except Exception as exception:
        print(
            "followee_retrieval: Error establishing a connection to the database..."
        )
        return

    # convert text file of content soures to list of usernames
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
        'username', 'user id', 'followers count', 'following count'
        'is private'
    ]
    new_followees = pd.DataFrame(columns=list(data_columns))

    total_new_followees = 100

    i = 0

    profile = instaloader.Profile.from_username(L.context,
                                                content_source_username)
    posts = profile.get_posts()

    for post in posts:
        likers = (post.get_likes())

        for liker in likers:
            username = liker.username
            user_id = liker.userid
            followers_count = liker.followers
            following_count = liker.followees
            is_private = liker.is_private

            if (followers_count < following_count) and is_private == 0:
                followee_data = [{
                    'username': username,
                    'user id': user_id,
                    'followers count': followers_count,
                    'following count': following_count,
                    'is private': is_private
                }]

                new_followees = new_followees.append(followee_data,
                                                     ignore_index=True)
                i += 1

            if i >= total_new_followees:
                break

    usernames = []
    instagram_uuid = []
    follower_count = []
    following_count = []
    is_private = []

    for username in new_followees["username"].values:
        usernames.append(username)

    for uuid in new_followees["user id"]:
        instagram_uuid.append(uuid)

    for count in new_followees['followers count'].values:
        follower_count.append(int(count))

    for count in new_followees['following count'].values:
        following_count.append(int(count))

    for state in new_followees['is private'].values:
        is_private.append(bool(state))

    for username, uuid, following, followers, state in zip(
            usernames, instagram_uuid, follower_count, following_count,
            is_private):
        database.insert_new_follower(uuid, username, following, followers,
                                     state)
