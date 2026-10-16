-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: badminton1
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actions` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `place` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `time_range` varchar(100) DEFAULT NULL,
  `date` varchar(100) DEFAULT NULL,
  `max_num` int DEFAULT NULL,
  `state` int DEFAULT NULL,
  `open_time` datetime DEFAULT NULL,
  `close_time` datetime DEFAULT NULL,
  `staff_user_id` int DEFAULT NULL,
  `wechat_url` varchar(1000) DEFAULT NULL,
  `borrow_num` int DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `activity_FK` (`staff_user_id`),
  CONSTRAINT `activity_FK` FOREIGN KEY (`staff_user_id`) REFERENCES `users` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `equip_id` varchar(100) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `equipment_FK` (`user_id`),
  CONSTRAINT `equipment_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `record_view`
--

/*!50001 DROP VIEW IF EXISTS `record_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `record_view` AS SELECT
 1 AS `account_name`,
 1 AS `account_id`,
 1 AS `account_student_id`,
 1 AS `action_title`,
 1 AS `action_place`,
 1 AS `action_date`,
 1 AS `action_time_range`,
 1 AS `action_state`,
 1 AS `borrow`,
 1 AS `id`,
 1 AS `sign_code`,
 1 AS `state`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `records`
--

DROP TABLE IF EXISTS `records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `records` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action_id` int DEFAULT NULL,
  `sign_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `state` int DEFAULT NULL,
  `borrow` tinyint(1) DEFAULT NULL,
  `sign_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `records_FK` (`action_id`),
  KEY `records_FK_1` (`user_id`),
  CONSTRAINT `records_FK` FOREIGN KEY (`action_id`) REFERENCES `actions` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `records_FK_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `staff_action_view`
--

/*!50001 DROP VIEW IF EXISTS `staff_action_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `staff_action_view` AS SELECT 
 1 AS `id`,
 1 AS `action_title`,
 1 AS `action_date`,
 1 AS `action_time_range`,
 1 AS `action_place`,
 1 AS `action_state`,
 1 AS `borrow_num`,
 1 AS `staff_id`,
 1 AS `staff_name`,
 1 AS `staff_username`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `staff_member_view`
--

/*!50001 DROP VIEW IF EXISTS `staff_member_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `staff_member_view` AS SELECT 
 1 AS `action_id`,
 1 AS `name`,
 1 AS `student_id`,
 1 AS `phone`,
 1 AS `wechat_id`,
 1 AS `borrow`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `tokens`
--

DROP TABLE IF EXISTS `tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tokens` (
  `user_id` int NOT NULL,
  `token` varchar(100) DEFAULT NULL,
  `out_time` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `tokens_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transfer`
--

DROP TABLE IF EXISTS `transfer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transfer` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `send_user_id` int DEFAULT NULL,
  `receive_user_id` int DEFAULT NULL,
  `record_id` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `transfer_FK` (`send_user_id`),
  KEY `transfer_FK_1` (`receive_user_id`),
  KEY `transfer_FK_2` (`record_id`),
  CONSTRAINT `transfer_FK` FOREIGN KEY (`send_user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transfer_FK_1` FOREIGN KEY (`receive_user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transfer_FK_2` FOREIGN KEY (`record_id`) REFERENCES `records` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `transfer_view`
--

/*!50001 DROP VIEW IF EXISTS `transfer_view`*/;
/*!50001 DROP VIEW IF EXISTS `transfer_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `transfer_view` AS SELECT 
 1 AS `ID`,
 1 AS `action_title`,
 1 AS `send_user`,
 1 AS `send_user_id`,
 1 AS `receive_user`,
 1 AS `receive_user_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `user_view`
--

/*!50001 DROP VIEW IF EXISTS `user_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `user_view` AS SELECT 
 1 AS `ID`,
 1 AS `username`,
 1 AS `name`,
 1 AS `phone`,
 1 AS `state`,
 1 AS `wechat_id`,
 1 AS `email`,
 1 AS `student_id`,
 1 AS `card_id`,
 1 AS `unsigned_num`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `card_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `phone` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `state` int DEFAULT NULL,
  `wechat_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `student_id` varchar(100) DEFAULT NULL,
  `unsigned_num` int DEFAULT '0',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `user_un` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `verifycode`
--

DROP TABLE IF EXISTS `verifycode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `verifycode` (
  `user_id` int NOT NULL,
  `code` varchar(100) DEFAULT NULL,
  `out_time` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `verifyCode_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Shared account-recovery request counters (also used by existing Docker installs).
DROP TABLE IF EXISTS `recovery_rate_limit`;
CREATE TABLE `recovery_rate_limit` (
  `bucket_key` char(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `window_start` bigint NOT NULL,
  `hits` int NOT NULL,
  PRIMARY KEY (`bucket_key`),
  KEY `recovery_rate_limit_window_idx` (`window_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `waiting`
--

DROP TABLE IF EXISTS `waiting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waiting` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action_id` int DEFAULT NULL,
  `rank` int DEFAULT NULL,
  `borrow` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `waiting_FK` (`user_id`),
  KEY `waiting_FK_1` (`action_id`),
  CONSTRAINT `waiting_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `waiting_FK_1` FOREIGN KEY (`action_id`) REFERENCES `actions` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `waiting_view`
--

/*!50001 DROP VIEW IF EXISTS `waiting_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `waiting_view` AS SELECT 
 1 AS `ID`,
 1 AS `action_title`,
 1 AS `action_user`,
 1 AS `wait_rank`,
 1 AS `user_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'badminton'
--

--
-- Dumping routines for database 'badminton'
--

--
-- Final view structure for view `record_view`
--

/*!50001 DROP VIEW IF EXISTS `record_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `record_view` AS select `users`.`name` AS `account_name`,`records`.`user_id` AS `account_id`,`users`.`student_id` AS `account_student_id`,`actions`.`title` AS `action_title`,`actions`.`place` AS `action_place`,`actions`.`date` AS `action_date`,`actions`.`time_range` AS `action_time_range`,`actions`.`state` AS `action_state`,`records`.`borrow` AS `borrow`,`records`.`ID` AS `id`,`records`.`sign_code` AS `sign_code`,`records`.`state` AS `state` from ((`users` join `actions`) join `records`) where ((`users`.`ID` = `records`.`user_id`) and (`actions`.`ID` = `records`.`action_id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `staff_action_view`
--

/*!50001 DROP VIEW IF EXISTS `staff_action_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `staff_action_view` AS select `actions`.`ID` AS `id`,`actions`.`title` AS `action_title`,`actions`.`date` AS `action_date`,`actions`.`time_range` AS `action_time_range`,`actions`.`place` AS `action_place`,`actions`.`state` AS `action_state`,`actions`.`borrow_num` AS `borrow_num`,`actions`.`staff_user_id` AS `staff_id`,`users`.`name` AS `staff_name`,`users`.`username` AS `staff_username` from (`actions` join `users`) where (`actions`.`staff_user_id` = `users`.`ID`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `staff_member_view`
--

/*!50001 DROP VIEW IF EXISTS `staff_member_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `staff_member_view` AS select `action`.`ID` AS `action_id`,`user`.`name` AS `name`,`user`.`student_id` AS `student_id`,`user`.`phone` AS `phone`,`user`.`wechat_id` AS `wechat_id`,`record`.`borrow` AS `borrow` from ((`actions` `action` join `records` `record`) join `users` `user`) where ((`action`.`ID` = `record`.`action_id`) and (`record`.`user_id` = `user`.`ID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `transfer_view`
--

/*!50001 DROP VIEW IF EXISTS `transfer_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `transfer_view` AS select `transfor`.`ID` AS `ID`,`actions`.`title` AS `action_title`,`user_send`.`name` AS `send_user`,`user_send`.`ID` AS `send_user_id`,`user_acpt`.`name` AS `receive_user`,`user_acpt`.`ID` AS `receive_user_id` from ((((`actions` join `transfer` `transfor`) join `users` `user_send`) join `users` `user_acpt`) join `records`) where ((`transfor`.`record_id` = `records`.`ID`) and (`records`.`action_id` = `actions`.`ID`) and (`transfor`.`send_user_id` = `user_send`.`ID`) and (`transfor`.`receive_user_id` = `user_acpt`.`ID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `user_view`
--

/*!50001 DROP VIEW IF EXISTS `user_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `user_view` AS select `users`.`ID` AS `ID`,`users`.`username` AS `username`,`users`.`name` AS `name`,`users`.`phone` AS `phone`,`users`.`state` AS `state`,`users`.`wechat_id` AS `wechat_id`,`users`.`email` AS `email`,`users`.`student_id` AS `student_id`,`users`.`card_id` AS `card_id`,`users`.`unsigned_num` AS `unsigned_num` from `users` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `waiting_view`
--

/*!50001 DROP VIEW IF EXISTS `waiting_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `waiting_view` AS select `waiting`.`ID` AS `ID`,`actions`.`title` AS `action_title`,`users`.`name` AS `action_user`,`waiting`.`rank` AS `wait_rank`,`waiting`.`user_id` AS `user_id` from ((`waiting` join `actions`) join `users`) where ((`users`.`ID` = `waiting`.`user_id`) and (`actions`.`ID` = `waiting`.`action_id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-20  0:20:18
