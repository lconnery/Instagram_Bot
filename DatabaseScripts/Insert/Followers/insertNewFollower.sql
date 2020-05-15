INSERT INTO followers
    (follower_id, follower_username, num_followers, num_following, public_account)
VALUES(DEFAULT, %s, %s, %s, %s)
RETURNING follower_id;