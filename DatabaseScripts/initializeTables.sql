create extension
if not exists "uuid-ossp";

CREATE TABLE captions
(
    caption_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    caption VARCHAR(500) NOT NULL,
    is_posted bool DEFAULT FALSE
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

CREATE TABLE followers
(
    follower_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    follower_username VARCHAR(250) UNIQUE NOT NULL,
    num_followers INTEGER NOT NULL,
    num_following INTEGER NOT NULL,
    public_account boolean NOT NULL
);

CREATE TABLE follower_requests
(
    follower_id uuid PRIMARY KEY REFERENCES followers (follower_id),
    time_stamp TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE TABLE follower_success
(
    follower_id uuid PRIMARY KEY REFERENCES followers (follower_id),
    time_stamp TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE TABLE url_invalid
(
    photo_id uuid not null PRIMARY KEY REFERENCES photos (photo_id),
    time_stamp TIMESTAMP DEFAULT NOW() not null,
    issue_desc VARCHAR
    (500) NOT NULL
);

CREATE TABLE hashtag_log
(
    photo_id uuid NOT NULL REFERENCES photos (photo_id),
    hashtag_id uuid NOT NULL REFERENCES hashtags
    (hashtag_id)
);

CREATE TABLE posts
(
    system_post_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    instagram_id varchar(200) NOT NULL,
    time_stamp TIMESTAMP DEFAULT NOW() NOT NULL,
    photo_id uuid NOT NULL REFERENCES photos (photo_id),
    content_source_id uuid NOT NULL REFERENCES contentSources (content_source_id),
    caption_id uuid NOT NULL REFERENCES captions (caption_id)
);