SELECT
   product_id, T.a AS u
   Count(star_rating) AS total_rating
FROM
   tbl_books INNER JOIN (SELECT * FROM Q WHERE Q.c < 100) AS T ON tbl_books.d = T.d
WHERE
   verified_purchase = 'Y' 
   AND review_date BETWEEN '1995-07-22' AND '2015-08-31' 
   AND marketplace IN 
   (
      select A.a, B.b
			from A, B
			where A.c < B.c
   )
HAVING
    total_rating > 5
GROUP BY
   product_id, period
