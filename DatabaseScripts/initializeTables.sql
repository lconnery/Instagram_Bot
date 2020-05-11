create extension
if not exists "uuid-ossp";

CREATE TABLE captions
(
    caption_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    caption VARCHAR(500) NOT NULL
);

CREATE TABLE contentSources
(
    content_source_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    content_source_username VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE hashtags
(
    hashtag_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    hashtag VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE photos
(
    photo_id uuid default uuid_generate_v4() PRIMARY KEY,
    photo_url varchar(500) UNIQUE NOT NULL,
    content_source_id uuid NOT NULL REFERENCES contentSources (content_source_id),
    is_posted boolean DEFAULT FALSE
);
