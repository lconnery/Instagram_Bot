SELECT x.follower_id, x.follower_username
FROM followers AS x LEFT OUTER JOIN follower_requests AS y ON x.follower_id=y.follower_id
WHERE y.follower_id IS NULL
LIMIT %s;