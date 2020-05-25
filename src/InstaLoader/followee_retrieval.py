import instaloader
import pandas as pd
from time import sleep

L = instaloader.Instaloader()
# convert text file of content soures to list of usernames
source_users = [line.rstrip('\n') for line in open('src/InstaLoader/ig_users.txt')]
username = source_users[1]

# to store post information
data_columns = ['username', 'user id', 'followers count', 'following count' 'is private']
new_followees = pd.DataFrame(columns=list(data_columns))

total_new_followees = 100

i = 0

print(username)
profile = instaloader.Profile.from_username(L.context, username)
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
            followee_data = [{'username': username, 'user id': user_id, 'followers count': followers_count,
                              'following count': following_count, 'is private': is_private}]

            new_followees = new_followees.append(followee_data, ignore_index=True)
            print(followee_data)
            i += 1

    if i >= total_new_followees:
        print(new_followees)
        new_followees.to_csv('new-followees')
        break
print('done')
