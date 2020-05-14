SELECT x.hashtag_id, x.hashtag
FROM (SELECT hashtag_id, hashtag
    FROM hashtags
    ORDER BY random()
) AS x
LIMIT 30;