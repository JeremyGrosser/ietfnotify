-- MySQL dump 10.9
--
-- Host: 10.1.1.201    Database: ietfnotify
-- ------------------------------------------------------
-- Server version	4.1.20-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `eventTypes`
--

DROP TABLE IF EXISTS `eventTypes`;
CREATE TABLE `eventTypes` (
  `id` int(10) NOT NULL auto_increment,
  `field` text NOT NULL,
  `type` text NOT NULL,
  `admin` tinyint(1) NOT NULL default '0',
  `defaultIgnore` tinyint(1) default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `eventTypes`
--


/*!40000 ALTER TABLE `eventTypes` DISABLE KEYS */;
LOCK TABLES `eventTypes` WRITE;
INSERT INTO `eventTypes` VALUES (1,'atom','event',1,0),(2,'html_email','event',0,0),(3,'plain_email','event',0,0),(4,'jabber','event',0,0);
UNLOCK TABLES;
/*!40000 ALTER TABLE `eventTypes` ENABLE KEYS */;

--
-- Table structure for table `filters`
--

DROP TABLE IF EXISTS `filters`;
CREATE TABLE `filters` (
  `id` int(10) NOT NULL auto_increment,
  `pattern` text,
  `field` text,
  `parent_id` int(10) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `filters`
--


/*!40000 ALTER TABLE `filters` DISABLE KEYS */;
LOCK TABLES `filters` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `filters` ENABLE KEYS */;

--
-- Table structure for table `subscriptions`
--

DROP TABLE IF EXISTS `subscriptions`;
CREATE TABLE `subscriptions` (
  `id` int(10) NOT NULL auto_increment,
  `username` text,
  `type` text,
  `target` text,
  `is_admin` int(11) default '0',
  `enabled` tinyint(1) default '1',
  `name` text,
  `ignorebit` text,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `subscriptions`
--


/*!40000 ALTER TABLE `subscriptions` DISABLE KEYS */;
LOCK TABLES `subscriptions` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `subscriptions` ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

