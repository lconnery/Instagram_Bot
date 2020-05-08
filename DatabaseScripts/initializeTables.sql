create table photos
(
    photo_id uuid default uuid_generate_v4() PRIMARY KEY,
    photo_url varchar(500) not null,
    source_username varchar(100) not null,
    is_posted boolean DEFAULT FALSE
);

create table captions
(
    caption_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    caption VARCHAR(500) not null
);

create table contentSources
(
    content_sources uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    content_source_username VARCHAR(100) not null
);

