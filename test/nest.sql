-- SELECT
--    product_id, T.a AS u
--    Count(star_rating) AS total_rating
-- FROM
--    tbl_books INNER JOIN (SELECT * FROM Q WHERE Q.c < 100) AS T ON tbl_books.d = T.d
-- WHERE
--    verified_purchase = 'Y' 
--    AND marketplace IN 
--    (
--       select A.a, B.b
-- 			from A, B
-- 			where A.c < B.c
--    )
-- HAVING
--     total_rating > 5
-- GROUP BY
--    product_id

SELECT a.c1, b.c1
FROM (
   SELECT c1, c3
   FROM c
) AS a
INNER JOIN 
(
   SELECT c2, c3
   FROM d
) AS b
ON a.c3 = b.c3