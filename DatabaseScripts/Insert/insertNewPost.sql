INSERT INTO posts
    (system_post_id, instagram_id, time_stamp, photo_id, content_source_id, caption_id)
VALUES(DEFAULT, %s, DEFAULT, %s, %s, %s)
RETURNING system_post_id;