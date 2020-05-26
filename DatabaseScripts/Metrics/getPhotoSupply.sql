select COUNT(photo_id) as photo_count
from photos
where is_posted=FALSE;