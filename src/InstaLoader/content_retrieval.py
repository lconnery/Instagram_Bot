import instaloader
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
import pandas as pd
from time import sleep

L = instaloader.Instaloader()

# convert text file of content soures to list of usernames
source_users = [line.rstrip('\n') for line in open('src/InstaLoader/ig_users.txt')]

# get posts from two days ago to yesterday
since = datetime.now()+timedelta(days=-2)
until = datetime.now()+timedelta(days=-1)

# to store post information
data_columns = ['username', 'likes_per_follower', 'post_id', 'url']
new_posts = pd.DataFrame(columns=list(data_columns))

# check each user
i = 0
for username in source_users:
    print(username)
    profile = instaloader.Profile.from_username(L.context, username)
    follower_count = profile.followers

    # check user's posts, save pictures
    posts = profile.get_posts()
    for post in takewhile(lambda p: p.date > since, dropwhile(lambda p: p.date > until, posts)):
        if post.typename == 'GraphImage':
            new_posts.loc[i] = [post.owner_username, post.likes /
                                follower_count, post.mediaid, post.url]
            i = i+1
    # instagram gets cranky when tired
    sleep(1)

# find top three new posts
new_posts = new_posts.sort_values('likes_per_follower', ascending=False)
new_posts = new_posts.iloc[0:3, :]
return new_posts
