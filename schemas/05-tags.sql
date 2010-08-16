--
-- Table structure for table `tags`
--
DROP TABLE IF EXISTS `tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tags` (
  `user_id` int(64) NOT NULL,
  `youtube_id` varchar(16) NOT NULL,
  `tag_name` varchar(64) NOT NULL,
  PRIMARY KEY (`user_id`, `youtube_id`, `tag_name`),
  INDEX us (user_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
