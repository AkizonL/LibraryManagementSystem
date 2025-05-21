/*
 Navicat Premium Data Transfer

 Source Server         : Graduation project
 Source Server Type    : MySQL
 Source Server Version : 80041
 Source Host           : localhost:3306
 Source Schema         : librarydatabase

 Target Server Type    : MySQL
 Target Server Version : 80041
 File Encoding         : 65001

 Date: 04/05/2025 08:22:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admins
-- ----------------------------
DROP TABLE IF EXISTS `admins`;
CREATE TABLE `admins`  (
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`username`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of admins
-- ----------------------------
INSERT INTO `admins` VALUES ('admin', '123456');

-- ----------------------------
-- Table structure for books
-- ----------------------------
DROP TABLE IF EXISTS `books`;
CREATE TABLE `books`  (
  `isbn` varchar(17) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '分类，可为空',
  `stock` int NOT NULL COMMENT '剩余数量',
  `shelves` tinyint(1) NOT NULL COMMENT '上架状态',
  PRIMARY KEY (`isbn`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of books
-- ----------------------------
INSERT INTO `books` VALUES ('978-1-4391-3126-7', '原则', '商业、自我提升', 5, 0);
INSERT INTO `books` VALUES ('978-7-02-011805-3', '百年孤独', '文学', 0, 1);
INSERT INTO `books` VALUES ('978-7-02-015220-0', '活着', '文学', 9, 1);
INSERT INTO `books` VALUES ('978-7-101-14272-5', '明朝那些事儿（壹）', '历史', 17, 1);
INSERT INTO `books` VALUES ('978-7-115-49925-9', '算法图解', '计算机', 8, 1);
INSERT INTO `books` VALUES ('978-7-121-35632-6', 'Python编程：从入门到实践', '计算机', 14, 1);
INSERT INTO `books` VALUES ('978-7-208-16840-7', '人类简史', '历史', 7, 1);
INSERT INTO `books` VALUES ('978-7-302-53035-4', '深入理解计算机系统', '计算机', 5, 1);
INSERT INTO `books` VALUES ('978-7-5399-8589-2', '三体：地球往事', '科幻', 10, 0);
INSERT INTO `books` VALUES ('978-7-5399-8590-8', '三体Ⅱ：黑暗森林', '科幻', 9, 0);

-- ----------------------------
-- Table structure for borrow_records
-- ----------------------------
DROP TABLE IF EXISTS `borrow_records`;
CREATE TABLE `borrow_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `isbn` varchar(17) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `borrow_date` datetime NOT NULL,
  `due_date` datetime NOT NULL,
  `returned_date` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `isbn`(`isbn` ASC) USING BTREE,
  CONSTRAINT `borrow_records_ibfk_1` FOREIGN KEY (`isbn`) REFERENCES `books` (`isbn`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 57 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of borrow_records
-- ----------------------------
INSERT INTO `borrow_records` VALUES (1, 2023001, '978-7-121-35632-6', '2025-03-12 17:01:26', '2025-04-11 17:01:26', '2025-03-13 11:32:17');
INSERT INTO `borrow_records` VALUES (2, 2023001, '978-7-121-35632-6', '2025-03-12 17:01:40', '2025-04-11 17:01:40', '2025-03-12 17:01:40');
INSERT INTO `borrow_records` VALUES (3, 2023001, '978-7-121-35632-6', '2025-03-12 17:02:30', '2025-04-11 17:02:30', '2025-03-12 17:02:30');
INSERT INTO `borrow_records` VALUES (4, 2023001, '978-7-121-35632-6', '2025-03-12 17:03:36', '2025-04-11 17:03:36', '2025-03-12 17:03:36');
INSERT INTO `borrow_records` VALUES (5, 2023001, '978-7-121-35632-6', '2025-03-12 17:11:58', '2025-04-11 17:11:58', '2025-03-12 17:11:58');
INSERT INTO `borrow_records` VALUES (6, 2023001, '978-7-121-35632-6', '2025-03-12 17:30:23', '2025-04-11 17:30:23', '2025-03-12 17:30:23');
INSERT INTO `borrow_records` VALUES (7, 2023001, '978-7-121-35632-6', '2025-03-12 17:35:54', '2025-04-11 17:35:54', '2025-03-12 17:35:54');
INSERT INTO `borrow_records` VALUES (8, 2023001, '978-7-121-35632-6', '2025-03-12 17:36:44', '2025-04-11 17:36:44', '2025-03-12 17:36:44');
INSERT INTO `borrow_records` VALUES (9, 2023001, '978-7-121-35632-6', '2025-03-12 20:42:18', '2025-04-11 20:42:18', '2025-03-12 20:42:18');
INSERT INTO `borrow_records` VALUES (10, 2023001, '978-7-121-35632-6', '2025-03-12 21:05:30', '2025-04-11 21:05:30', '2025-03-12 21:05:30');
INSERT INTO `borrow_records` VALUES (11, 2023001, '978-7-121-35632-6', '2025-03-12 21:07:23', '2025-04-11 21:07:23', '2025-03-12 21:07:23');
INSERT INTO `borrow_records` VALUES (12, 2023001, '978-7-121-35632-6', '2025-03-12 21:46:16', '2025-04-11 21:46:16', '2025-03-12 21:46:16');
INSERT INTO `borrow_records` VALUES (13, 123456, '978-7-101-14272-5', '2025-03-13 12:52:52', '2025-04-12 12:52:52', '2025-03-13 12:53:14');
INSERT INTO `borrow_records` VALUES (14, 114514, '978-7-208-16840-7', '2025-03-13 12:57:14', '2025-04-12 12:57:14', '2025-03-13 12:57:41');
INSERT INTO `borrow_records` VALUES (15, 1, '978-7-101-14272-5', '2025-03-14 12:49:30', '2025-04-13 12:49:30', '2025-03-14 12:59:51');
INSERT INTO `borrow_records` VALUES (16, 4, '978-7-02-015220-0', '2025-03-14 12:51:15', '2025-04-13 12:51:15', '2025-03-14 12:54:09');
INSERT INTO `borrow_records` VALUES (17, 44, '978-7-5399-8589-2', '2025-03-14 12:51:40', '2025-04-13 12:51:40', '2025-03-14 13:00:49');
INSERT INTO `borrow_records` VALUES (18, 1111111111, '978-7-101-14272-5', '2025-03-14 13:01:37', '2025-04-13 13:01:37', '2025-03-14 13:02:07');
INSERT INTO `borrow_records` VALUES (19, 22222, '978-7-121-35632-6', '2025-03-14 13:01:56', '2025-04-13 13:01:56', '2025-03-14 13:02:44');
INSERT INTO `borrow_records` VALUES (20, 1, '978-7-101-14272-5', '2025-03-14 13:03:53', '2025-04-13 13:03:53', '2025-03-14 13:03:58');
INSERT INTO `borrow_records` VALUES (21, 1, '978-7-101-14272-5', '2025-03-14 13:04:34', '2025-04-13 13:04:34', '2025-03-14 13:04:36');
INSERT INTO `borrow_records` VALUES (22, 1, '978-7-101-14272-5', '2025-03-14 13:13:09', '2025-04-13 13:13:09', '2025-03-18 13:33:34');
INSERT INTO `borrow_records` VALUES (23, 114555, '978-7-101-14272-5', '2025-03-17 00:00:00', '2025-04-16 00:00:00', '2025-03-18 13:33:27');
INSERT INTO `borrow_records` VALUES (24, 151515, '978-7-115-49925-9', '2025-03-17 00:00:00', '2025-04-01 00:00:00', '2025-03-18 13:33:32');
INSERT INTO `borrow_records` VALUES (25, 999999, '978-7-101-14272-5', '2025-03-17 00:00:00', '2025-04-01 00:00:00', '2025-03-18 13:33:06');
INSERT INTO `borrow_records` VALUES (26, 777777, '978-7-101-14272-5', '2025-03-17 00:00:00', '2025-04-16 00:00:00', '2025-03-18 13:30:55');
INSERT INTO `borrow_records` VALUES (27, 444444, '978-7-101-14272-5', '2025-03-17 00:00:00', '2025-04-16 00:00:00', '2025-03-18 13:30:46');
INSERT INTO `borrow_records` VALUES (28, 111111, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-01 00:00:00', '2025-03-18 12:24:29');
INSERT INTO `borrow_records` VALUES (29, 11111, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:30:17');
INSERT INTO `borrow_records` VALUES (30, 15, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 12:24:32');
INSERT INTO `borrow_records` VALUES (31, 1555, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 12:24:34');
INSERT INTO `borrow_records` VALUES (32, 11111, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:30:19');
INSERT INTO `borrow_records` VALUES (33, 11551, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 12:24:36');
INSERT INTO `borrow_records` VALUES (34, 11, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:30:34');
INSERT INTO `borrow_records` VALUES (35, 11, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 12:24:38');
INSERT INTO `borrow_records` VALUES (36, 151515, '978-7-02-015220-0', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:30:43');
INSERT INTO `borrow_records` VALUES (37, 123, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:34:25');
INSERT INTO `borrow_records` VALUES (38, 123, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:34:27');
INSERT INTO `borrow_records` VALUES (39, 123, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:34:29');
INSERT INTO `borrow_records` VALUES (40, 111, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:35:04');
INSERT INTO `borrow_records` VALUES (41, 222, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:35:11');
INSERT INTO `borrow_records` VALUES (42, 333, '978-7-02-011805-3', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:35:15');
INSERT INTO `borrow_records` VALUES (43, 111, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:45:17');
INSERT INTO `borrow_records` VALUES (44, 222, '978-7-121-35632-6', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:50:13');
INSERT INTO `borrow_records` VALUES (45, 333, '978-7-02-011805-3', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:50:06');
INSERT INTO `borrow_records` VALUES (46, 444, '978-7-5399-8589-2', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:50:11');
INSERT INTO `borrow_records` VALUES (47, 555, '978-7-5399-8590-8', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 13:50:09');
INSERT INTO `borrow_records` VALUES (48, 114514, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-03 00:00:00', '2025-03-18 19:14:52');
INSERT INTO `borrow_records` VALUES (49, 123123, '978-7-101-14272-5', '2025-03-18 00:00:00', '2025-04-01 00:00:00', '2025-03-18 19:27:54');
INSERT INTO `borrow_records` VALUES (50, 222222, '978-7-02-015220-0', '2025-03-18 00:00:00', '2025-04-17 00:00:00', '2025-03-18 19:21:45');
INSERT INTO `borrow_records` VALUES (51, 333333, '978-7-208-16840-7', '2025-03-18 00:00:00', '2025-04-02 00:00:00', '2025-03-18 19:28:34');
INSERT INTO `borrow_records` VALUES (52, 123123, '978-7-101-14272-5', '2025-03-19 00:00:00', '2025-04-04 00:00:00', NULL);
INSERT INTO `borrow_records` VALUES (53, 222222, '978-7-121-35632-6', '2025-03-19 00:00:00', '2025-03-23 00:00:00', NULL);
INSERT INTO `borrow_records` VALUES (54, 333333, '978-7-02-015220-0', '2025-03-05 00:00:00', '2025-03-16 00:00:00', '2025-03-23 15:36:20');
INSERT INTO `borrow_records` VALUES (55, 444444, '978-7-02-015220-0', '2025-03-06 00:00:00', '2025-04-11 00:00:00', NULL);
INSERT INTO `borrow_records` VALUES (56, 1111111, '978-1-4391-3126-7', '2025-03-23 00:00:00', '2025-04-22 00:00:00', '2025-03-23 14:03:35');

SET FOREIGN_KEY_CHECKS = 1;
