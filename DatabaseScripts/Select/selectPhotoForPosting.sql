SELECT p.photo_id, p.photo_url, c.content_source_id, c.content_source_username
FROM contentsources AS c, (SELECT *
    FROM photos
    WHERE is_posted=FALSE
    ORDER BY random()) AS p
WHERE p.content_source_id=c.content_source_id
LIMIT 1;