SELECT x.caption_id, x.caption
FROM (SELECT caption_id, caption
    FROM captions
    WHERE is_posted=FALSE
    ORDER BY random()
) AS x
LIMIT 1;