create table user_information(
	user_id INT UNSIGNED AUTO_INCREMENT ,-- 编号
	name VARCHAR(40) NOT NULL,-- 姓名
	gender VARCHAR(40) NOT NULL,-- 性别
	identity_number VARCHAR(40),-- 身份证号码
  	tel VARCHAR(40),-- 手机号
	email VARCHAR(40),-- 邮箱
	address VARCHAR(80),-- 住址
	PRIMARY KEY (user_id)
);

CREATE TABLE user_information_index (
`user_id` INT NOT NULL,
`ip` VARCHAR(20) NOT NULL,
`encrypted` char(1) NOT NULL,
PRIMARY KEY(`user_id`, `ip`,`encrypted`)
);

CREATE TABLE key_index (
`user_id` INT NOT NULL,
`ip` VARCHAR(20) NOT NULL,
PRIMARY KEY(`user_id`, `ip`)
);

CREATE TABLE key_storage (
`user_id` INT NOT NULL,
`key` VARCHAR(40) NOT NULL
);

INSERT INTO user_information (name,gender,identity_number, tel,email,address)
                       VALUES
                       ( "bob","m","42030319950122","13399992222","bob@hust.edu","hust" );

INSERT INTO user_information (name,gender,identity_number, tel,email,address)
                       VALUES
                       ( "alice","f","42030319920123","13299993333","alice@hust.edu","hust" );

INSERT INTO user_information (name,gender,identity_number, tel,email,address)
                       VALUES
                       ( "de158516507069fe1aad7e27ddd6e87b","de158516507069fe1aad7e27ddd6e87b","de158516507069fe1aad7e27ddd6e87b","de158516507069fe1aad7e27ddd6e87b","de158516507069fe1aad7e27ddd6e87b","de158516507069fe1aad7e27ddd6e87b" );

INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 1,"192.0.0.1","0" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 1,"192.0.0.2","0" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 1,"192.0.0.3","0" );

INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 2,"192.0.0.1","0" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 2,"192.0.0.2","0" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 2,"192.0.0.3","0" );

INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 3,"192.0.0.1","1" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 3,"192.0.0.2","1" );
INSERT INTO user_information_index (user_id,ip, encrypted)
                       VALUES
                       ( 3,"192.0.0.3","1" );


INSERT INTO key_index (user_id,ip)
                       VALUES
                       ( 3,"192.0.0.1" );
INSERT INTO key_index (user_id,ip)
                       VALUES
                       ( 3,"192.0.0.2" );
INSERT INTO key_index (user_id,ip)
                       VALUES
                       ( 3,"192.0.0.3" );

INSERT INTO key_storage (user_id,key)
                       VALUES
                       ( 3,"81f44672f7707f551ea23c36b66f7afe" );

INSERT INTO key_storage (user_id,key)
                       VALUES
                       ( 3,"f665550b58ad1dad577b70f26e9e28f2" );

INSERT INTO key_storage (user_id,key)
                       VALUES
                       ( 3,"347f1b22e78051043914229868c101d3" );

drop table user_information_index;
drop table key_index;
drop table user_information;
drop table key_storage;
