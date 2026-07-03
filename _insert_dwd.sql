-- Insert DWD data from PostgreSQL staging into Iceberg
INSERT INTO iceberg.lake.user_behavior_dwd
SELECT
    CAST(user_id AS BIGINT) AS user_id,
    CAST(item_id AS BIGINT) AS item_id,
    CAST(category_id AS BIGINT) AS category_id,
    behavior_type,
    event_time,
    CAST(DATE_FORMAT(event_time, 'yyyy-MM-dd') AS VARCHAR) AS pt
FROM postgresql.public.staging_user_behavior
WHERE
    behavior_type IN ('pv', 'buy', 'cart', 'fav')
    AND CAST(user_id AS BIGINT) > 0
    AND CAST(item_id AS BIGINT) > 0
    AND CAST(category_id AS BIGINT) > 0
    AND CAST(ts AS BIGINT) > 0
    AND event_time IS NOT NULL;
