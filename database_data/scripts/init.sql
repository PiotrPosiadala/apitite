CREATE DATABASE IF NOT EXISTS db;
-- Change username and password for custom deployment
CREATE USER 'databaseuser' IDENTIFIED BY 'databasepassword';
ALTER USER 'databaseuser' IDENTIFIED WITH mysql_native_password BY 'databasepassword';
GRANT ALL PRIVILEGES ON *.* TO 'databaseuser'@'%';

CREATE TABLE db.apitite (ID int NOT NULL AUTO_INCREMENT, label varchar(50), tastyCount int, PRIMARY KEY (ID));
ALTER TABLE db.apitite ADD CONSTRAINT unique_id UNIQUE(label);