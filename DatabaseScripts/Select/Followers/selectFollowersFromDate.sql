select x.follower_id, x.instagram_uuid
from followers as x, follower_requests as y
where x.follower_id=y.follower_id AND EXTRACT(year from y.time_stamp)=%s AND EXTRACT(month from y.time_stamp)=%s AND EXTRACT(day from y.time_stamp)=%s;