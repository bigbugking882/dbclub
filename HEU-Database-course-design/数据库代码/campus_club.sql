-- 创建数据库（若不存在）
DROP DATABASE campus_club;
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
  `audit_status` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '审核状态：0-待审核，1-已通过，2-已拒绝',
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
  `status` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '活动状态：0-未开始，1-进行中，2-已结束，3-待审核，4-未通过',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '活动创建时间',
  `creator_id` INT(11) NOT NULL COMMENT '创建者ID（关联user.id）',
  FOREIGN KEY (`club_id`) REFERENCES `club`(`club_id`) ON DELETE CASCADE,
  FOREIGN KEY (`creator_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
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

-- =============================================
-- 初始化测试数据
-- =============================================

-- 1. 用户数据
INSERT INTO `user` (`username`, `password`, `telephone`, `role`) VALUES
('admin', 'admin123', '13800138000', 2),
('testuser', 'user123', '13800138001', 0),
('张三', 'zhangsan123', '13800138002', 0),
('李四', 'lisi123', '13800138003', 0),
('王五', 'wangwu123', '13800138004', 0),
('赵六', 'zhaoliu123', '13800138005', 0),
('钱七', 'qianqi123', '13800138006', 0),
('孙八', 'sunba123', '13800138007', 0),
('周九', 'zhoujiu123', '13800138008', 0),
('吴十', 'wushi123', '13800138009', 0)
ON DUPLICATE KEY UPDATE 
  `username` = VALUES(`username`), 
  `password` = VALUES(`password`), 
  `role` = VALUES(`role`);

-- 2. 社团数据（包含审核状态）
INSERT INTO `club` (`club_name`, `description`, `founder_id`, `create_time`, `status`, `category`, `audit_status`) VALUES
('计算机协会', '计算机技术交流与学习，编程技术分享', 1, '2024-01-15', 1, '学术科技', 1),
('篮球社', '篮球运动爱好者聚集地，定期组织比赛', 2, '2024-02-20', 1, '文化体育', 1),
('志愿者协会', '组织各类志愿服务活动，服务社会', 1, '2024-03-10', 1, '志愿公益', 1),
('英语角', '英语学习交流平台，提高口语能力', 3, '2024-01-25', 1, '学术科技', 1),
('舞蹈社', '舞蹈爱好者社团，学习各种舞蹈风格', 4, '2024-02-15', 1, '文化体育', 1),
('摄影协会', '摄影技术交流，组织外拍活动', 5, '2024-03-05', 1, '文化体育', 1)
ON DUPLICATE KEY UPDATE 
  `description` = VALUES(`description`), 
  `status` = VALUES(`status`),
  `audit_status` = VALUES(`audit_status`);

-- 3. 社团成员数据
INSERT INTO `club_member` (`user_id`, `club_id`, `role`, `join_time`, `audit_status`) VALUES
-- 计算机协会成员
(1, 1, 1, '2024-01-15', 1), -- 社长
(2, 1, 0, '2024-01-20', 1),
(3, 1, 0, '2024-01-22', 1),
(4, 1, 0, '2024-01-25', 1),

-- 篮球社成员
(2, 2, 1, '2024-02-20', 1), -- 社长
(1, 2, 0, '2024-02-25', 1),
(5, 2, 0, '2024-02-28', 1),
(6, 2, 0, '2024-03-01', 1),

-- 志愿者协会成员
(1, 3, 1, '2024-03-10', 1), -- 社长
(3, 3, 0, '2024-03-12', 1),
(7, 3, 0, '2024-03-15', 1),
(8, 3, 0, '2024-03-18', 1),

-- 英语角成员
(3, 4, 1, '2024-01-25', 1), -- 社长
(4, 4, 0, '2024-01-28', 1),
(9, 4, 0, '2024-02-01', 1),

-- 舞蹈社成员
(4, 5, 1, '2024-02-15', 1), -- 社长
(6, 5, 0, '2024-02-20', 1),
(10, 5, 0, '2024-02-25', 1),

-- 摄影协会成员
(5, 6, 1, '2024-03-05', 1), -- 社长
(7, 6, 0, '2024-03-08', 1),
(8, 6, 0, '2024-03-10', 1),

-- 待审核的申请
(9, 1, 0, '2024-11-20', 0), -- 申请加入计算机协会，待审核
(10, 2, 0, '2024-11-21', 0) -- 申请加入篮球社，待审核
ON DUPLICATE KEY UPDATE 
  `role` = VALUES(`role`), 
  `audit_status` = VALUES(`audit_status`);

-- 4. 活动数据（包含创建者ID）
INSERT INTO `activity` (`club_id`, `title`, `content`, `start_time`, `end_time`, `location`, `status`, `creator_id`) VALUES
-- 计算机协会活动（admin创建）
(1, 'Python入门讲座', 'Python基础语法与环境搭建，适合零基础学员', '2024-12-01 14:00:00', '2024-12-01 16:00:00', '教学楼201教室', 0, 1),
(1, 'Web开发实战', 'HTML、CSS、JavaScript前端开发实战', '2024-12-08 15:00:00', '2024-12-08 17:00:00', '计算机实验室', 0, 1),
(1, '算法竞赛培训', 'ACM竞赛算法讲解与实战训练', '2024-11-25 19:00:00', '2024-11-25 21:00:00', '教学楼305教室', 1, 1),

-- 篮球社活动（testuser创建）
(2, '校园篮球联赛', '各学院篮球代表队参赛，精彩对决', '2024-12-05 16:00:00', '2024-12-05 18:00:00', '体育馆篮球场', 0, 2),
(2, '篮球基础训练', '篮球基本功教学，适合初学者', '2024-11-28 17:00:00', '2024-11-28 19:00:00', '室外篮球场', 4, 2),

-- 志愿者协会活动（admin创建）
(3, '社区环保活动', '清理社区垃圾，宣传环保知识', '2024-12-02 09:00:00', '2024-12-02 12:00:00', '学校周边社区', 0, 1),
(3, '敬老院慰问', '看望敬老院老人，表演文艺节目', '2024-11-30 14:00:00', '2024-11-30 17:00:00', '阳光敬老院', 4, 1),

-- 英语角活动（张三创建）
(4, '英语口语角', '自由英语对话，提高口语表达能力', '2024-12-03 19:00:00', '2024-12-03 21:00:00', '外语学院活动室', 0, 3),
(4, '英文电影欣赏', '观看英文电影，学习地道表达', '2024-11-29 18:30:00', '2024-11-29 21:00:00', '多媒体教室', 1, 3),

-- 舞蹈社活动（李四创建）
(5, '街舞基础教学', '学习街舞基本动作和节奏感', '2024-12-04 19:00:00', '2024-12-04 21:00:00', '舞蹈排练厅', 4, 4),
(5, '民族舞表演', '民族舞蹈排练和表演技巧', '2024-11-27 20:00:00', '2024-11-27 22:00:00', '艺术中心', 2, 4),

-- 摄影协会活动（王五创建）
(6, '校园秋色外拍', '捕捉校园秋季美景，摄影技巧交流', '2024-12-06 15:00:00', '2024-12-06 17:00:00', '校园内', 0, 5),
(6, '人像摄影讲座', '人像摄影构图与灯光技巧', '2024-11-26 19:00:00', '2024-11-26 21:00:00', '摄影工作室', 2, 5)
ON DUPLICATE KEY UPDATE 
  `content` = VALUES(`content`), 
  `status` = VALUES(`status`),
  `creator_id` = VALUES(`creator_id`);

-- 5. 活动报名数据
INSERT INTO `activity_signup` (`activity_id`, `user_id`, `signup_time`, `is_attend`) VALUES
-- Python入门讲座报名
(1, 2, '2024-11-20 10:00:00', 0),
(1, 3, '2024-11-20 11:00:00', 0),
(1, 4, '2024-11-21 09:00:00', 0),

-- Web开发实战报名
(2, 2, '2024-11-21 14:00:00', 0),
(2, 5, '2024-11-22 10:00:00', 0),

-- 算法竞赛培训报名（已开始活动）
(3, 2, '2024-11-20 15:00:00', 0),
(3, 3, '2024-11-21 16:00:00', 0),
(3, 4, '2024-11-22 11:00:00', 0),

-- 校园篮球联赛报名
(4, 1, '2024-11-21 09:00:00', 0),
(4, 5, '2024-11-21 10:00:00', 0),
(4, 6, '2024-11-22 14:00:00', 0),

-- 社区环保活动报名
(6, 3, '2024-11-20 16:00:00', 0),
(6, 7, '2024-11-21 11:00:00', 0),
(6, 8, '2024-11-22 15:00:00', 0),

-- 英语口语角报名
(8, 4, '2024-11-21 17:00:00', 0),
(8, 9, '2024-11-22 12:00:00', 0)
ON DUPLICATE KEY UPDATE 
  `is_attend` = VALUES(`is_attend`);