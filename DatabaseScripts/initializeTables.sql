create table captions
(
    caption_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    caption VARCHAR(500) not null
);

create table contentSources
(
    content_source_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    content_source_username VARCHAR(100) UNIQUE not null
);

create table photos
(
    photo_id uuid default uuid_generate_v4() PRIMARY KEY,
    photo_url varchar(500) UNIQUE not null,
    content_source_id uuid not null REFERENCES contentSources (content_source_id),
    is_posted boolean DEFAULT FALSE
);
