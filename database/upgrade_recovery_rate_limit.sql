-- Run once against an existing MySQL database before deploying this backend.
-- New Docker volumes already get this table from install.sql.
CREATE TABLE IF NOT EXISTS `recovery_rate_limit` (
  `bucket_key` char(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `window_start` bigint NOT NULL,
  `hits` int NOT NULL,
  PRIMARY KEY (`bucket_key`),
  KEY `recovery_rate_limit_window_idx` (`window_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
