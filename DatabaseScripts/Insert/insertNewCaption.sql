INSERT INTO captions
    (caption_id, caption)
VALUES(DEFAULT, %s)
RETURNING caption_id;