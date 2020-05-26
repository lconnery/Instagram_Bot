SELECT COUNT(follower_id)
FROM follower_success
WHERE EXTRACT(year from time_stamp) =%s AND EXTRACT(month from time_stamp) =%s AND EXTRACT(day from time_stamp) =%s;
