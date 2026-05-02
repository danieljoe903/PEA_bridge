-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 01, 2026 at 03:00 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pea_bridge`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(11) NOT NULL,
  `admin_date` date DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `admin_email` varchar(100) NOT NULL,
  `admin_password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`admin_id`, `admin_date`, `user_id`, `admin_email`, `admin_password`) VALUES
(4, NULL, NULL, 'manage@peabridge.com', 'scrypt:32768:8:1$jdObHxtVF5kvxu0O$6cf6bef09376d2f8577fe41f5159425e7df91ec38bac1e2368bcb58c73e325011c8538c8481738a6876e3b1ba8c77f46451d1e5eb390802d7717bbb8f079d812');

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('1c1b5e492dc7');

-- --------------------------------------------------------

--
-- Table structure for table `client_interest`
--

CREATE TABLE `client_interest` (
  `interest_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `client_user_id` int(11) NOT NULL,
  `interest_status` enum('requested','approved','declined') NOT NULL DEFAULT 'requested',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `client_interest`
--

INSERT INTO `client_interest` (`interest_id`, `property_id`, `client_user_id`, `interest_status`, `created_at`) VALUES
(1, 2, 7, 'approved', '2026-03-08 23:18:30'),
(2, 3, 6, 'requested', '2026-03-14 17:41:00'),
(4, 6, 7, 'declined', '2026-04-08 03:34:29'),
(5, 6, 7, 'declined', '2026-04-11 16:22:21');

-- --------------------------------------------------------

--
-- Table structure for table `identity_verification`
--

CREATE TABLE `identity_verification` (
  `verification_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `id_type` enum('nin','passport','drivers_license') NOT NULL,
  `id_number` varchar(100) NOT NULL,
  `verification_status` enum('pending','approved','rejected') NOT NULL,
  `verified_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `properties`
--

CREATE TABLE `properties` (
  `property_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `property_title` varchar(300) DEFAULT NULL,
  `property_type` enum('land','house','apartment','commercial') DEFAULT NULL,
  `adress` text NOT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `property_status` enum('available','under_verification','sold','rented','rejected','archived','expired') NOT NULL DEFAULT 'under_verification',
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `property_listing` enum('SALE') NOT NULL,
  `agent_id` int(11) DEFAULT NULL,
  `state_id` int(11) DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `properties`
--

INSERT INTO `properties` (`property_id`, `owner_id`, `property_title`, `property_type`, `adress`, `price`, `property_status`, `created_at`, `property_listing`, `agent_id`, `state_id`, `expires_at`) VALUES
(2, 6, 'occean vila', 'house', 'victoria island', 900000000.00, 'sold', '2026-03-07 16:27:44', 'SALE', 1, 2, NULL),
(3, 7, 'fct vila', 'land', 'ph', 700000000.00, 'archived', '2026-03-08 23:39:29', 'SALE', 2, NULL, NULL),
(6, 6, 'luxury vila', 'house', 'banana island', 2000000000.00, 'available', '2026-03-14 21:54:14', 'SALE', 1, 1, NULL),
(12, 6, 'luxuzry vila', 'house', 'ikeja mainland', 1000000000.00, 'archived', '2026-03-18 23:14:13', 'SALE', 1, 1, NULL),
(13, 6, 'ikeja vila', 'house', 'ikeja ', 6000000.00, 'archived', '2026-03-20 14:22:19', 'SALE', 1, 1, NULL),
(14, 7, 'Modern nigerian duplex ', 'house', 'lekki phase 1', 799999999.00, 'archived', '2026-04-15 14:58:17', 'SALE', 2, 1, '2026-04-29 14:58:17'),
(15, 7, 'Modern duplex', 'house', 'lekki phase 1', 800000000.00, 'available', '2026-04-15 14:59:54', 'SALE', 2, 1, '2026-05-14 23:27:15'),
(16, 7, 'luxury villa', 'house', 'kekki phase2', 500000000.00, 'available', '2026-04-15 15:01:11', 'SALE', 2, 1, '2026-05-14 23:27:17'),
(17, 7, 'modern duplex', 'house', 'Victoria Island', 2000000000.00, 'available', '2026-04-15 15:02:49', 'SALE', 2, 1, '2026-05-14 23:27:13'),
(18, 7, 'Luxury Villa', 'house', 'Airport road', 650000000.00, 'archived', '2026-04-15 15:05:25', 'SALE', 2, 2, '2026-04-29 15:05:25'),
(19, 7, 'Luxury Villa', 'house', 'Airport road', 950000000.00, 'available', '2026-04-15 15:06:44', 'SALE', 2, 2, '2026-05-14 23:27:11'),
(20, 7, 'Modern luxury villa', 'house', 'Victoria Island', 900000000.00, 'available', '2026-04-15 15:10:03', 'SALE', 2, 1, '2026-05-14 23:27:08'),
(21, 6, 'Luxury Duplex', 'house', 'Lekki Phase 3', 1000000000.00, 'available', '2026-04-15 15:12:23', 'SALE', 1, 1, '2026-05-14 23:28:02'),
(22, 6, 'Modern luxury palace', 'house', 'Lekki Phase 2', 850000000.00, 'available', '2026-04-15 15:14:14', 'SALE', 1, 1, '2026-05-14 23:27:59');

-- --------------------------------------------------------

--
-- Table structure for table `property_agents`
--

CREATE TABLE `property_agents` (
  `agent_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `license_number` varchar(100) NOT NULL,
  `agency_name` varchar(150) DEFAULT NULL,
  `agency_status` enum('active','suspended','pending') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `property_agents`
--

INSERT INTO `property_agents` (`agent_id`, `user_id`, `license_number`, `agency_name`, `agency_status`) VALUES
(1, 6, '123245678', 'bokula', 'active'),
(2, 7, '123456789', 'emma daniel', 'active'),
(3, 8, '8900000222', 'ikechukwu', 'suspended');

-- --------------------------------------------------------

--
-- Table structure for table `property_documents`
--

CREATE TABLE `property_documents` (
  `document_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `document_type` enum('c_of_o','deed','survey_plan') DEFAULT NULL,
  `document_reference` varchar(200) DEFAULT NULL,
  `verified_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `property_image`
--

CREATE TABLE `property_image` (
  `image_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `image_url` varchar(100) DEFAULT NULL,
  `uploaded_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `property_image`
--

INSERT INTO `property_image` (`image_id`, `property_id`, `image_url`, `uploaded_at`) VALUES
(4, 2, 'property_images/022fa434b0514a6bb0d58ee653904046.jpg', '2026-03-07 16:27:44'),
(5, 2, 'property_images/57c249c08a88431c962fc8b1ba87f058.jpg', '2026-03-07 16:27:44'),
(6, 2, 'property_images/3117da4702584431831d74299607d323.jpg', '2026-03-07 16:27:44'),
(7, 3, 'property_images/64ecd50e467d418faacbc32906de029a.png', '2026-03-08 23:39:29'),
(11, 6, 'property_images/83ecf3ff14d2486ab96e88b2ffaf9742.jpg', '2026-03-14 21:54:14'),
(12, 6, 'property_images/3b792b9754634c5e88f5a4e17419a521.webp', '2026-03-14 21:54:14'),
(13, 6, 'property_images/122267ef64d949a99ee601bb6e657ffc.webp', '2026-03-14 21:54:14'),
(14, 12, 'property_images/17ac6f86b50c4f66b62482950c5b9860.jpg', '2026-03-18 23:14:13'),
(15, 13, 'property_images/f789cc4bced44c3d865c99209afc2329.jpg', '2026-03-20 14:22:19'),
(16, 14, 'property_images/a2b2b632d5884ef2bf312664f90fdd33.jpg', '2026-04-15 14:58:17'),
(17, 15, 'property_images/d16e7bb7231e4c158e701bfbc48c23a7.jpg', '2026-04-15 14:59:54'),
(18, 16, 'property_images/c9be3b798951446d8b79211d1e8479f6.jpg', '2026-04-15 15:01:11'),
(19, 17, 'property_images/6e6c8bd19b1d4cd6925db8b272d753a3.jpg', '2026-04-15 15:02:49'),
(20, 18, 'property_images/ff67c34caf7642e3ad597342603fabc9.jpg', '2026-04-15 15:05:25'),
(21, 19, 'property_images/8ccf93837ea743d98e593037232c692c.jpg', '2026-04-15 15:06:44'),
(22, 20, 'property_images/6652aa66d65443bcb8548cf617752a32.jpg', '2026-04-15 15:10:03'),
(23, 21, 'property_images/d108dd289a2248d5ab35b6c9cdee599b.jpg', '2026-04-15 15:12:23'),
(24, 22, 'property_images/8cf8bf932d454a28af582b13035dc69c.jpg', '2026-04-15 15:14:14');

-- --------------------------------------------------------

--
-- Table structure for table `state`
--

CREATE TABLE `state` (
  `state_id` int(11) NOT NULL,
  `state_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `state`
--

INSERT INTO `state` (`state_id`, `state_name`) VALUES
(1, 'lagos'),
(2, 'abuja');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `user_fname` varchar(200) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `is_verified` tinyint(1) DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `image_url` varchar(200) DEFAULT NULL,
  `user_password` varchar(255) NOT NULL,
  `users_lname` varchar(200) NOT NULL,
  `username` varchar(200) NOT NULL,
  `suspended` tinyint(1) NOT NULL DEFAULT 0,
  `reset_nonce` varchar(64) NOT NULL DEFAULT 'initial nonce'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `user_fname`, `email`, `phone`, `is_verified`, `created_at`, `image_url`, `user_password`, `users_lname`, `username`, `suspended`, `reset_nonce`) VALUES
(6, 'bukola', 'boku@gmail.com', '07056783421', 1, '2026-03-07 15:20:23', 'uploads/074f1459005d7eba0319.avif', 'scrypt:32768:8:1$YyNCusV95MM7buKZ$2e13096281e25eae47c6b375f7f2a9a582a526fd527b62c9c600f035746b9bb9171548ad00759c5399bb09231f4287f0e28efb624c82c470d773a86d33552ee6', 'odunipe', 'boku5555', 0, 'initial nonce'),
(7, 'emmanuel', 'chinoyere@gmail.com', '09067894567', 1, '2026-03-07 17:10:36', 'uploads/45f92ba1cd459a357f0f.jpg', 'scrypt:32768:8:1$CyWIxb4ZrWutKhH0$f09111dbb149f35343bcbfc063282752464df472bd0780c81ddda74500f17fb3366b87d9699204abe2502544cc8f0590f231e5e0295f1468dbbed360777f8342', 'daniel', 'emma777', 0, 'initial nonce'),
(8, 'chioma', 'ike@gmail.com', '09034562312', 1, '2026-03-07 17:19:55', 'uploads/40fdd523503d05aef59b.jpeg', 'scrypt:32768:8:1$06LdCIfQ5Up7Ut6F$3398e8744170a71f91d59c7431115ef4aa67edb464459c39d5a233598bde8bcf35056a0423107615dfcc0a33663a3a22119811b189af604694107c3e2957db32', 'ike', 'ike9999', 0, 'initial nonce'),
(12, 'tomasious', 'victorytryvic@gmail.com', '09056431449', 0, '2026-04-12 23:23:05', 'uploads/default.png', 'scrypt:32768:8:1$XzTuW5vzdn5Z86xW$a7fee08cff442243846ad8cac2c27bbc3aa01e0253515b6420f66f5ef5912d9e5fdc642a8b24829b8a742f4dd9f8b286f7b25c1903d3899b92ee6ec5c9318a3e', 'victory', 'tomag333', 0, 'b2d539223d355929e399b063251afc9e');

-- --------------------------------------------------------

--
-- Table structure for table `user_type`
--

CREATE TABLE `user_type` (
  `user_typeid` int(11) NOT NULL,
  `user_type` enum('buyer','seller','agent') DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `admin_email` (`admin_email`),
  ADD KEY `fk_admin` (`user_id`),
  ADD KEY `ix_admin_user_id` (`user_id`);

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `client_interest`
--
ALTER TABLE `client_interest`
  ADD PRIMARY KEY (`interest_id`),
  ADD KEY `fk_client_user` (`client_user_id`),
  ADD KEY `ix_client_interest_client_user_id` (`client_user_id`),
  ADD KEY `property_id` (`property_id`),
  ADD KEY `ix_client_interest_property_id` (`property_id`);

--
-- Indexes for table `identity_verification`
--
ALTER TABLE `identity_verification`
  ADD PRIMARY KEY (`verification_id`),
  ADD KEY `fk_verification_user` (`user_id`),
  ADD KEY `ix_identity_verification_user_id` (`user_id`);

--
-- Indexes for table `properties`
--
ALTER TABLE `properties`
  ADD PRIMARY KEY (`property_id`),
  ADD KEY `fk_owner_id` (`owner_id`),
  ADD KEY `fk_agent` (`agent_id`),
  ADD KEY `ix_properties_agent_id` (`agent_id`),
  ADD KEY `ix_properties_owner_id` (`owner_id`),
  ADD KEY `state_id` (`state_id`);

--
-- Indexes for table `property_agents`
--
ALTER TABLE `property_agents`
  ADD PRIMARY KEY (`agent_id`),
  ADD KEY `fk_agent_user` (`user_id`),
  ADD KEY `ix_property_agents_user_id` (`user_id`);

--
-- Indexes for table `property_documents`
--
ALTER TABLE `property_documents`
  ADD PRIMARY KEY (`document_id`),
  ADD KEY `FK_document` (`property_id`),
  ADD KEY `ix_property_documents_property_id` (`property_id`);

--
-- Indexes for table `property_image`
--
ALTER TABLE `property_image`
  ADD PRIMARY KEY (`image_id`),
  ADD KEY `fk_property_id` (`property_id`),
  ADD KEY `ix_property_image_property_id` (`property_id`);

--
-- Indexes for table `state`
--
ALTER TABLE `state`
  ADD PRIMARY KEY (`state_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `ix_users_email` (`email`),
  ADD KEY `ix_users_username` (`username`);

--
-- Indexes for table `user_type`
--
ALTER TABLE `user_type`
  ADD PRIMARY KEY (`user_typeid`),
  ADD KEY `fk_typeid` (`user_id`),
  ADD KEY `ix_user_type_user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `client_interest`
--
ALTER TABLE `client_interest`
  MODIFY `interest_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `identity_verification`
--
ALTER TABLE `identity_verification`
  MODIFY `verification_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `properties`
--
ALTER TABLE `properties`
  MODIFY `property_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `property_agents`
--
ALTER TABLE `property_agents`
  MODIFY `agent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `property_documents`
--
ALTER TABLE `property_documents`
  MODIFY `document_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `property_image`
--
ALTER TABLE `property_image`
  MODIFY `image_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `state`
--
ALTER TABLE `state`
  MODIFY `state_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user_type`
--
ALTER TABLE `user_type`
  MODIFY `user_typeid` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `fk_admin` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `client_interest`
--
ALTER TABLE `client_interest`
  ADD CONSTRAINT `client_interest_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`property_id`),
  ADD CONSTRAINT `fk_client_user` FOREIGN KEY (`client_user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `identity_verification`
--
ALTER TABLE `identity_verification`
  ADD CONSTRAINT `fk_verification_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `properties`
--
ALTER TABLE `properties`
  ADD CONSTRAINT `fk_agent` FOREIGN KEY (`agent_id`) REFERENCES `property_agents` (`agent_id`),
  ADD CONSTRAINT `fk_owner_id` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `properties_ibfk_1` FOREIGN KEY (`state_id`) REFERENCES `state` (`state_id`);

--
-- Constraints for table `property_agents`
--
ALTER TABLE `property_agents`
  ADD CONSTRAINT `fk_agent_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `property_documents`
--
ALTER TABLE `property_documents`
  ADD CONSTRAINT `FK_document` FOREIGN KEY (`property_id`) REFERENCES `properties` (`property_id`);

--
-- Constraints for table `property_image`
--
ALTER TABLE `property_image`
  ADD CONSTRAINT `fk_property_id` FOREIGN KEY (`property_id`) REFERENCES `properties` (`property_id`);

--
-- Constraints for table `user_type`
--
ALTER TABLE `user_type`
  ADD CONSTRAINT `fk_typeid` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
