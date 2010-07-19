DROP TABLE IF EXISTS `youtube_videos`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `youtube_videos` (
  `youtube_id` varchar(16) default NULL,
  `title` varchar(60) default NULL,
  `artist` varchar(60) default NULL,
  `description` varchar(255) default NULL,
  `view_count` int(10) unsigned default NULL,
  `duration` int(8) unsigned default NULL,
  `saved_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `thumbnail_1` varchar(255) default NULL,
  `thumbnail_2` varchar(255) default NULL,
  `thumbnail_3` varchar(255) default NULL,
  `flash_url` varchar(255) default NULL,
  PRIMARY KEY  (`youtube_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `playlist_youtube_map`
--
DROP TABLE IF EXISTS `playlist_youtube_map`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `playlist_youtube_map` (
  `id` int(64) unsigned NOT NULL auto_increment,
  `playlist_id` int(64) NOT NULL,
  `youtube_id` varchar(16) NOT NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `next_id` int(64) unsigned default NULL,
  PRIMARY KEY (`id`),
  INDEX pl (playlist_id),
  INDEX yt (youtube_id),
  UNIQUE KEY pl_yt (playlist_id, youtube_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `playlists`
--
DROP TABLE IF EXISTS `playlists`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `playlists` (
  `id` int(64) unsigned NOT NULL auto_increment,
  `user_id` int(64) NOT NULL,
  `title` varchar(100) NOT NULL,
  `subdomain` varchar(100) DEFAULT NULL,
  `deleted_at` timestamp DEFAULT 0,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX us (user_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
