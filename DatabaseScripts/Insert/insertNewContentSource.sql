INSERT INTO contentSources
    (content_source_id, content_source_username)
VALUES(DEFAULT, %s)
RETURNING content_source_id;