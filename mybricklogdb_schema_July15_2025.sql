-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Jul 15, 2025 at 01:57 PM
-- Server version: 8.0.42
-- PHP Version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mybricklogdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `collection`
--

CREATE TABLE `collection` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `set_num` varchar(255) NOT NULL,
  `collection_set_quantity` int NOT NULL DEFAULT '1',
  `complete` int NOT NULL DEFAULT '0',
  `sealed` int NOT NULL DEFAULT '0'
) ;

-- --------------------------------------------------------

--
-- Table structure for table `collection_minifigs`
--

CREATE TABLE `collection_minifigs` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `set_num` varchar(255) NOT NULL,
  `fig_num` varchar(20) NOT NULL,
  `quantity_owned` int NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventories`
--

CREATE TABLE `inventories` (
  `id` int NOT NULL,
  `version` int DEFAULT NULL,
  `set_num` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory_minifigs`
--

CREATE TABLE `inventory_minifigs` (
  `inventory_id` int NOT NULL,
  `fig_num` varchar(20) NOT NULL,
  `quantity` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory_sets`
--

CREATE TABLE `inventory_sets` (
  `inventory_id` int NOT NULL,
  `set_num` varchar(20) NOT NULL,
  `quantity` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `log_id` int NOT NULL,
  `log_user` int DEFAULT NULL,
  `log_action` varchar(256) NOT NULL,
  `log_useragent` varchar(45) NOT NULL,
  `log_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `minifigs`
--

CREATE TABLE `minifigs` (
  `fig_num` varchar(20) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `num_parts` int DEFAULT NULL,
  `img_url` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `popular_themes`
--

CREATE TABLE `popular_themes` (
  `id` int NOT NULL,
  `theme_id` int NOT NULL,
  `collection_count` int NOT NULL,
  `snapshot_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `recent_set_additions`
--

CREATE TABLE `recent_set_additions` (
  `id` int NOT NULL,
  `set_num` varchar(20) DEFAULT NULL,
  `theme_id` int DEFAULT NULL,
  `added_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sets`
--

CREATE TABLE `sets` (
  `set_num` varchar(20) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `theme_id` int DEFAULT NULL,
  `num_parts` int DEFAULT NULL,
  `img_url` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `set_prices`
--

CREATE TABLE `set_prices` (
  `id` int NOT NULL,
  `set_num` varchar(20) NOT NULL,
  `retail_price` decimal(10,2) DEFAULT NULL,
  `market_price` decimal(10,2) DEFAULT NULL,
  `market_price_difference` decimal(5,2) DEFAULT NULL,
  `sealed_value` decimal(10,2) DEFAULT NULL,
  `used_value` decimal(10,2) DEFAULT NULL,
  `used_value_range_low` decimal(10,2) DEFAULT NULL,
  `used_value_range_high` decimal(10,2) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) DEFAULT 'success',
  `status_message` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `themes`
--

CREATE TABLE `themes` (
  `id` int NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `parent_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `verified` tinyint(1) DEFAULT '0',
  `verification_token` varchar(255) DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `show_email` tinyint(1) DEFAULT '0',
  `display_name` varchar(100) DEFAULT NULL,
  `bio` text,
  `location` varchar(100) DEFAULT NULL,
  `favorite_theme` int DEFAULT NULL,
  `join_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `twitter_handle` varchar(50) DEFAULT NULL,
  `youtube_channel` varchar(100) DEFAULT NULL,
  `bricklink_store` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `set_num` varchar(255) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `collection`
--
ALTER TABLE `collection`
  ADD PRIMARY KEY (`id`),
  ADD KEY `set_num` (`set_num`(250)),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `collection_minifigs`
--
ALTER TABLE `collection_minifigs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_collection_minifig` (`user_id`,`set_num`,`fig_num`),
  ADD KEY `idx_user_set` (`user_id`,`set_num`),
  ADD KEY `idx_fig_num` (`fig_num`),
  ADD KEY `set_num` (`set_num`),
  ADD KEY `idx_collection_minifigs_user_set_fig` (`user_id`,`set_num`,`fig_num`);

--
-- Indexes for table `inventories`
--
ALTER TABLE `inventories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `set_num` (`set_num`);

--
-- Indexes for table `inventory_minifigs`
--
ALTER TABLE `inventory_minifigs`
  ADD PRIMARY KEY (`inventory_id`,`fig_num`),
  ADD KEY `fig_num` (`fig_num`);

--
-- Indexes for table `inventory_sets`
--
ALTER TABLE `inventory_sets`
  ADD PRIMARY KEY (`inventory_id`,`set_num`),
  ADD KEY `set_num` (`set_num`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `minifigs`
--
ALTER TABLE `minifigs`
  ADD PRIMARY KEY (`fig_num`);

--
-- Indexes for table `popular_themes`
--
ALTER TABLE `popular_themes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `theme_id` (`theme_id`),
  ADD KEY `snapshot_date` (`snapshot_date`);

--
-- Indexes for table `recent_set_additions`
--
ALTER TABLE `recent_set_additions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `set_num` (`set_num`),
  ADD KEY `theme_id` (`theme_id`);

--
-- Indexes for table `sets`
--
ALTER TABLE `sets`
  ADD PRIMARY KEY (`set_num`),
  ADD KEY `theme_id` (`theme_id`);

--
-- Indexes for table `set_prices`
--
ALTER TABLE `set_prices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_set_num` (`set_num`),
  ADD KEY `idx_set_num` (`set_num`),
  ADD KEY `idx_last_updated` (`last_updated`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `themes`
--
ALTER TABLE `themes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_users_username` (`username`),
  ADD KEY `idx_users_email` (`email`),
  ADD KEY `idx_users_last_login` (`last_login`),
  ADD KEY `fk_users_favorite_theme` (`favorite_theme`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`id`),
  ADD KEY `set_num` (`set_num`(250)),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `collection`
--
ALTER TABLE `collection`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `collection_minifigs`
--
ALTER TABLE `collection_minifigs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `log_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `popular_themes`
--
ALTER TABLE `popular_themes`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recent_set_additions`
--
ALTER TABLE `recent_set_additions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `set_prices`
--
ALTER TABLE `set_prices`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `collection_minifigs`
--
ALTER TABLE `collection_minifigs`
  ADD CONSTRAINT `collection_minifigs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collection_minifigs_ibfk_2` FOREIGN KEY (`set_num`) REFERENCES `sets` (`set_num`) ON DELETE CASCADE,
  ADD CONSTRAINT `collection_minifigs_ibfk_3` FOREIGN KEY (`fig_num`) REFERENCES `minifigs` (`fig_num`) ON DELETE CASCADE;

--
-- Constraints for table `inventory_minifigs`
--
ALTER TABLE `inventory_minifigs`
  ADD CONSTRAINT `inventory_minifigs_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`),
  ADD CONSTRAINT `inventory_minifigs_ibfk_2` FOREIGN KEY (`fig_num`) REFERENCES `minifigs` (`fig_num`);

--
-- Constraints for table `inventory_sets`
--
ALTER TABLE `inventory_sets`
  ADD CONSTRAINT `inventory_sets_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`),
  ADD CONSTRAINT `inventory_sets_ibfk_2` FOREIGN KEY (`set_num`) REFERENCES `inventories` (`set_num`);

--
-- Constraints for table `popular_themes`
--
ALTER TABLE `popular_themes`
  ADD CONSTRAINT `popular_themes_ibfk_1` FOREIGN KEY (`theme_id`) REFERENCES `themes` (`id`);

--
-- Constraints for table `recent_set_additions`
--
ALTER TABLE `recent_set_additions`
  ADD CONSTRAINT `recent_set_additions_ibfk_1` FOREIGN KEY (`set_num`) REFERENCES `sets` (`set_num`),
  ADD CONSTRAINT `recent_set_additions_ibfk_2` FOREIGN KEY (`theme_id`) REFERENCES `themes` (`id`);

--
-- Constraints for table `sets`
--
ALTER TABLE `sets`
  ADD CONSTRAINT `sets_ibfk_1` FOREIGN KEY (`theme_id`) REFERENCES `themes` (`id`);

--
-- Constraints for table `set_prices`
--
ALTER TABLE `set_prices`
  ADD CONSTRAINT `fk_set_prices_sets` FOREIGN KEY (`set_num`) REFERENCES `sets` (`set_num`),
  ADD CONSTRAINT `set_prices_ibfk_1` FOREIGN KEY (`set_num`) REFERENCES `sets` (`set_num`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_users_favorite_theme` FOREIGN KEY (`favorite_theme`) REFERENCES `themes` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
