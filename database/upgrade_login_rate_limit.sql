-- Apply to existing MySQL databases before deploying login throttling.
-- Safe to re-run; unlike install.sql this does not touch existing records.
CREATE TABLE IF NOT EXISTS `login_rate_limit` (
  `bucket_key` char(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `window_start` bigint NOT NULL,
  `hits` int NOT NULL,
  PRIMARY KEY (`bucket_key`),
  KEY `login_rate_limit_window_idx` (`window_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
