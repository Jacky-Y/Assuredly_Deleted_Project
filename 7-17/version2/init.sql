use deletion_db;
CREATE TABLE personal_information_table (
  ID INT PRIMARY KEY AUTO_INCREMENT,
  infoID VARCHAR(36),
  deleteDupInfoID VARCHAR(36),
  infoType INT,
  person_name VARCHAR(50),
  gender INT,
  identity_number VARCHAR(18),
  phone_number VARCHAR(11),
  email VARCHAR(100),
  address VARCHAR(100),
  infoOwner VARCHAR(50),
  infoCreator VARCHAR(50),
  infoCreateTime DATETIME,
  infoCreateLoc VARCHAR(100)
);

INSERT INTO personal_information_table (infoID, deleteDupInfoID, infoType, person_name, gender, identity_number, phone_number, email, address, infoOwner, infoCreator, infoCreateTime, infoCreateLoc)
VALUES ('BA4A7F24-ACA7-4844-98A5-464786DF5C09', 'sever1-48942ECA-7CDA-4B02', 1, 'Li Yang', 1, '320201199820129991', '13917271131', '10291023801@163.com', 'Wuhan', '李XX', '李XX', '2022-12-10 10:14:34', '北京市海淀区100085');

INSERT INTO personal_information_table (infoID, deleteDupInfoID, infoType, person_name, gender, identity_number, phone_number, email, address, infoOwner, infoCreator, infoCreateTime, infoCreateLoc)
VALUES ('E0F1C355-32B6-4B8D-BF77-549EFB579845', 'sever2-539C3DA2-A52D-4F34', 1, 'Zhang San', 1, '510201199810012345', '13888888888', 'zhangsan@gmail.com', 'Shanghai', '张XX', '张XX', '2022-11-15 15:25:00', '上海市浦东新区200120');

INSERT INTO personal_information_table (infoID, deleteDupInfoID, infoType, person_name, gender, identity_number, phone_number, email, address, infoOwner, infoCreator, infoCreateTime, infoCreateLoc)
VALUES ('87F94C31-1847-4B69-AFF3-52E3F02B1ED6', 'sever3-67BD0AAB-3D12-4A8E', 2, 'Wang Wu', 2, '610201198910112233', '13777777777', 'wangwu@hotmail.com', 'Beijing', '王XX', '王XX', '2023-01-05 09:40:21', '北京市朝阳区100025');


CREATE TABLE personal_information_duplication_index (
  infoID CHAR(36) NOT NULL,
  ip VARCHAR(20) NOT NULL,
  deleteDupInfoID VARCHAR(30) NOT NULL,
  PRIMARY KEY (infoID, ip, deleteDupInfoID)
);
INSERT INTO personal_information_duplication_index (infoID, ip, deleteDupInfoID)
VALUES ('BA4A7F24-ACA7-4844-98A5-464786DF5C09', '127.0.0.1', 'sever1-48942ECA-7CDA-4B02');
INSERT INTO personal_information_duplication_index (infoID, ip, deleteDupInfoID)
VALUES ('BA4A7F24-ACA7-4844-98A5-464786DF5C09', '127.0.0.2', 'sever2-48942ECA-7CDA-DHJS');
INSERT INTO personal_information_duplication_index (infoID, ip, deleteDupInfoID)
VALUES ('BA4A7F24-ACA7-4844-98A5-464786DF5C09', '127.0.0.3', 'sever3-48942ECA-7CDA-COS0');