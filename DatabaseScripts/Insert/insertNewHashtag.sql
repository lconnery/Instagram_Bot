INSERT INTO hashtags
    (hashtag_id, hashtag)
VALUES(DEFAULT, %s)
RETURNING hashtag_id;