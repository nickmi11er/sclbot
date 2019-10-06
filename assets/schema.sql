BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `work_type` (
	`group_id`	INTEGER,
	`subj_ids`	VARCHAR,
	`w_type`	INTEGER,
	FOREIGN KEY(`group_id`) REFERENCES `groups`(`group_id`)
);
CREATE TABLE IF NOT EXISTS `users` (
	`user_id`	INTEGER NOT NULL UNIQUE,
	`username`	VARCHAR,
	`tg_user_id`	VARCHAR UNIQUE,
	`role`	INTEGER DEFAULT (2),
	`group_id`	INTEGER,
	`description`	VARCHAR,
	`show_lecturer`	BOOLEAN NOT NULL DEFAULT false,
	FOREIGN KEY(`role`) REFERENCES `roles`(`role_id`),
	FOREIGN KEY(`group_id`) REFERENCES `groups`(`group_id`),
	PRIMARY KEY(`user_id`)
);
ALTER TABLE users ADD show_lecturer BOOLEAN NOT NULL DEFAULT false;

CREATE TABLE IF NOT EXISTS `subscribers` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`chat_id`	INTEGER NOT NULL UNIQUE,
	`tg_user_id`	VARCHAR
);
CREATE TABLE IF NOT EXISTS `subjects` (
	`subject_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`subj_name`	VARCHAR,
	`exam`	BOOLEAN DEFAULT false,
	`lecture`	INTEGER,
	`term`	VARCHAR,
	FOREIGN KEY(`lecture`) REFERENCES `lecturer`(`lecturer_id`)
);
CREATE TABLE IF NOT EXISTS `roles` (
	`role_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`role_name`	VARCHAR
);
CREATE TABLE IF NOT EXISTS `meta` (
	`meta_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`group_name`	VARCHAR,
	`start_date`	DATE,
	`session_date`	DATE
);
CREATE TABLE IF NOT EXISTS `lecturer` (
	`lecturer_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`lecturer_name`	VARCHAR,
	`respect`	DECIMAL ( 0 , 1 ) DEFAULT (0),
	`subject`	INTEGER,
	FOREIGN KEY(`subject`) REFERENCES `subjects`(`subject_id`)
);
CREATE TABLE IF NOT EXISTS `groups` (
	`group_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`group_name`	char ( 128 ) NOT NULL
);
COMMIT;
