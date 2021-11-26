SELECT
   product_id, period,
   Count(star_rating) AS total_rating,
   Max(star_rating) AS best_rating,
   Min(star_rating) AS worst_rating 
FROM
   tbl_books 
WHERE
   verified_purchase = 'Y' 
   AND review_date BETWEEN '1995-07-22' AND '2015-08-31' 
   AND marketplace IN 
   (
      'DE','US','UK','FR','JP' 
   )
HAVING
    total_rating > 5
GROUP BY
   product_id, period
LIMIT 10