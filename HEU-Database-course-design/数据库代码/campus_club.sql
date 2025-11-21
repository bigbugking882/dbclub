-- 创建数据库（若不存在）
CREATE DATABASE IF NOT EXISTS campus_club 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE campus_club;

-- 1. 用户表（存储用户账号信息）
CREATE TABLE `user` (
  `id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '用户唯一ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(100) NOT NULL COMMENT '密码（明文存储，测试用）',
  `telephone` VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号（登录账号）',
  `role` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '角色：0-普通用户，1-社团管理员，2-系统管理员',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 社团表（存储社团基本信息）
CREATE TABLE `club` (
  `club_id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '社团唯一ID',
  `club_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '社团名称（不可重复）',
  `description` TEXT COMMENT '社团简介',
  `founder_id` INT(11) NOT NULL COMMENT '创始人ID（关联user.id）',
  `create_time` DATE NOT NULL COMMENT '社团创建日期',
  `status` TINYINT(4) NOT NULL DEFAULT 1 COMMENT '状态：0-注销，1-正常运行',
  `category` VARCHAR(50) NOT NULL COMMENT '社团类别（学术科技/文化体育/志愿公益）',
  FOREIGN KEY (`founder_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='社团表';

-- 3. 社团成员表（记录用户与社团的关联关系）
CREATE TABLE `club_member` (
  `member_id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '成员记录ID',
  `user_id` INT(11) NOT NULL COMMENT '用户ID（关联user.id）',
  `club_id` INT(11) NOT NULL COMMENT '社团ID（关联club.club_id）',
  `role` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '成员角色：0-普通社员，1-社长，2-管理员',
  `join_time` DATE NOT NULL COMMENT '加入社团的日期',
  `audit_status` TINYINT(4) NOT NULL DEFAULT 1 COMMENT '审核状态：0-待审核，1-已通过，2-已拒绝',
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`club_id`) REFERENCES `club`(`club_id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_user_club` (`user_id`, `club_id`) COMMENT '同一用户不能重复加入同一社团'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='社团成员表';

-- 4. 活动表（存储社团活动信息）
CREATE TABLE `activity` (
  `activity_id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '活动唯一ID',
  `club_id` INT(11) NOT NULL COMMENT '所属社团ID（关联club.club_id）',
  `title` VARCHAR(200) NOT NULL COMMENT '活动名称（对应前端activity_name参数）',
  `content` TEXT COMMENT '活动描述（对应前端description参数）',
  `start_time` DATETIME NOT NULL COMMENT '活动开始时间',
  `end_time` DATETIME NOT NULL COMMENT '活动结束时间',
  `location` VARCHAR(200) NOT NULL COMMENT '活动地点',
  `status` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '活动状态：0-未开始，1-进行中，2-已结束',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '活动创建时间',
  FOREIGN KEY (`club_id`) REFERENCES `club`(`club_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动表';

-- 5. 活动报名表（记录用户报名活动的信息）
CREATE TABLE `activity_signup` (
  `signup_id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '报名记录ID',
  `activity_id` INT(11) NOT NULL COMMENT '活动ID（关联activity.activity_id）',
  `user_id` INT(11) NOT NULL COMMENT '用户ID（关联user.id）',
  `signup_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  `is_attend` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '是否出席：0-未出席，1-已出席',
  FOREIGN KEY (`activity_id`) REFERENCES `activity`(`activity_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_user_activity` (`user_id`, `activity_id`) COMMENT '同一用户不能重复报名同一活动'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动报名表';

-- 6. 验证码临时存储表（模拟Redis，测试用）
CREATE TABLE `vercode_temp` (
  `id` INT(11) PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
  `telephone` VARCHAR(20) NOT NULL COMMENT '手机号',
  `vercode` VARCHAR(6) NOT NULL COMMENT '6位验证码',
  `expire_time` DATETIME NOT NULL COMMENT '过期时间（5分钟）',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  UNIQUE KEY `uk_telephone` (`telephone`) COMMENT '同一手机号同一时间只能有一个有效验证码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='验证码临时存储表';

-- 初始化数据
-- 1. 系统管理员账号（手机号：13800138000，密码：admin123，角色：2-系统管理员）
INSERT INTO `user` (`username`, `password`, `telephone`, `role`)
VALUES ('admin', 'admin123', '13800138000', 2)
ON DUPLICATE KEY UPDATE `username`='admin', `password`='admin123', `role`=2;

-- 2. 测试普通用户（手机号：13800138001，密码：user123，角色：0-普通用户）
INSERT INTO `user` (`username`, `password`, `telephone`, `role`)
VALUES ('testuser', 'user123', '13800138001', 0)
ON DUPLICATE KEY UPDATE `username`='testuser', `password`='user123', `role`=0;

-- 3. 测试社团（创始人：系统管理员，ID=1）
INSERT INTO `club` (`club_name`, `description`, `founder_id`, `create_time`, `status`, `category`)
VALUES (
  '计算机协会', 
  '计算机技术交流与学习',
  1, 
  CURDATE(), 
  1, 
  '学术科技'
)
ON DUPLICATE KEY UPDATE `description`='计算机技术交流与学习', `status`=1;

-- 4. 创始人自动加入社团（角色：1-社长）
INSERT INTO `club_member` (`user_id`, `club_id`, `role`, `join_time`, `audit_status`)
VALUES (1, 1, 1, CURDATE(), 1)
ON DUPLICATE KEY UPDATE `role`=1, `audit_status`=1;

-- 5. 测试活动（所属社团：计算机协会，ID=1）
INSERT INTO activity (club_id, title, content, start_time, end_time, location, status) 
VALUES (1, 'Python入门讲座', 'Python基础语法与环境搭建', '2025-11-24 14:00:00', '2025-11-24 16:00:00', '201教室', 0)
ON DUPLICATE KEY UPDATE content='Python基础语法与环境搭建', status=0;