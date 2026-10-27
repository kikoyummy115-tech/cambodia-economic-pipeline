SELECT indicator_name, year, value, unit
FROM economic_observations AS e
WHERE year = (
    SELECT MAX(e2.year)
    FROM economic_observations AS e2
    WHERE e2.indicator_code = e.indicator_code
)
ORDER BY indicator_code;
