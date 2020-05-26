SELECT content_source_id, content_source_username
FROM contentsources
ORDER BY random()
LIMIT %s;