-- mysql.sql
GRANT ALL PRIVILEGES ON *.* TO 'test_user'@'%' WITH GRANT OPTION;
USE quik_db;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    PRIMARY KEY (id)
);

SET @max_id := IFNULL((SELECT MAX(id) FROM users), 0) ;
SET @target_rows = 100; -- Random number between 100 and 200

CREATE TEMPORARY TABLE temp_seq AS
WITH RECURSIVE seq AS (
    SELECT @max_id + 1 AS id
    UNION ALL
    SELECT id + 1 FROM seq WHERE id < @max_id + @target_rows
)
SELECT id
FROM seq;

-- Insert into users table using the temporary table
INSERT INTO users (id, name, dob)
SELECT id,
       CONCAT('User ', LPAD(id, 3, '0')),
       CURDATE() - INTERVAL FLOOR(RAND() * 20000) DAY
FROM temp_seq;

-- Drop the temporary table
DROP TEMPORARY TABLE temp_seq;
DELIMITER //
CREATE PROCEDURE GetUserName (IN user_id INT)
BEGIN
    SELECT name FROM test_data WHERE id = user_id;
END //
DELIMITER ;

CREATE TABLE IF NOT EXISTS test_data (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    dob VARCHAR(255),
    uuid CHAR(36)
);
-- command doesn't work without configuring the secure_file_priv variable.
-- LOAD DATA INFILE '/docker-entrypoint-initdb.d/test_data.csv'
-- INTO TABLE test_data
-- FIELDS TERMINATED BY ','
-- LINES TERMINATED BY '\n'
-- (id, name, dob, uuid);
INSERT INTO test_data (id, name, dob, uuid)
VALUES
    ("1","Emma Thompson","1985-07-23","8a6f1d9e-53a9-4f8c-bb07-1d18a3e4b9b9"),
    ("2","Liam Johnson","1992-11-15","c9e8a649-4ed0-4d2b-92ba-2e03b26b7b13"),
    ("3","Olivia Williams","1978-03-30","5f9f4a77-9248-456b-98f1-7b4bf31b9d67"),
    ("4","Noah Brown","1969-05-10","a4b9ec8c-3e2f-4c5a-b0b1-6a2e2a5e7c77"),
    ("5","Ava Jones","1990-09-08","7c6d9b5e-8d6f-4e3e-b9d8-1a8f3e4b7c9d"),
    ("6","William Garcia","1982-12-19","d4f7e8a6-5c2d-4f1b-a9b3-8c7d6e5f4a2b"),
    ("7","Sophia Miller","1975-01-14","e3b8c9d0-7a6b-4e5f-b8c7-d9e0f1a2b3c4"),
    ("8","James Davis","1995-04-27","f2a1b3c4-5d6e-7f8a-9b0c-1d2e3f4a5b6c"),
    ("9","Isabella Rodriguez","1988-08-02","0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d"),
    ("10","Benjamin Martinez","1970-10-25","b9c8d7e6-5f4a-3b2c-1d0e-9f8a7b6c5d4e"),
    ("11","Mia Hernandez","1983-02-18","c7d6e5f4-3a2b-1c0d-9e8f-7a6b5c4d3e2f"),
    ("12","Lucas Lopez","1991-06-05","8d7c6b5a-4e3f-2d1c-0b9a-8f7e6d5c4b3a"),
    ("13","Charlotte Gonzalez","1976-12-30","5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d"),
    ("14","Henry Wilson","1965-03-12","2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e"),
    ("15","Amelia Anderson","1993-09-17","a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d"),
    ("16","Alexander Thomas","1987-11-09","f4e3d2c1-b0a9-8f7e-6d5c-4b3a2f1e0d9c"),
    ("17","Harper Taylor","1979-07-06","1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"),
    ("18","Michael Moore","1996-02-23","6d5c4b3a-2f1e-0d9c-8b7a-6f5e4d3c2b1a"),
    ("19","Evelyn Jackson","1984-05-19","9e8f7a6b-5c4d-3e2f-1a0b-9c8d7e6f5a4b"),
    ("20","Daniel Martin","1972-08-11","0f1e2d3c-4b5a-6c7d-8e9f-0a1b2c3d4e5f"),
    ("21","Abigail Lee","1986-04-22","1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e"),
    ("22","Matthew Perez","1994-07-13","2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"),
    ("23","Emily White","1974-10-29","3d4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7f8a"),
    ("24","David Harris","1981-01-08","4e5f6a7b-8c9d-0e1f-2a3b-4c5d6e7f8a9b"),
    ("25","Ella Clark","1993-06-21","5f6a7b8c-9d0e-1f2a-3b4c-5d6e7f8a9b0c"),
    ("26","Joseph Lewis","1977-09-04","6a7b8c9d-0e1f-2a3b-4c5d-6e7f8a9b0c1d"),
    ("27","Grace Robinson","1990-12-16","7b8c9d0e-1f2a-3b4c-5d6e-7f8a9b0c1d2e"),
    ("28","Samuel Walker","1968-02-05","8c9d0e1f-2a3b-4c5d-6e7f-8a9b0c1d2e3f"),
    ("29","Chloe Young","1989-05-27","9d0e1f2a-3b4c-5d6e-7f8a-9b0c1d2e3f4a"),
    ("30","Andrew Allen","1971-08-19","0e1f2a3b-4c5d-6e7f-8a9b-0c1d2e3f4a5b"),
    ("31","Lily King","1995-03-11","1f2a3b4c-5d6e-7f8a-9b0c-1d2e3f4a5b6c"),
    ("32","Joshua Wright","1983-07-24","2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d"),
    ("33","Victoria Scott","1976-11-30","3b4c5d6e-7f8a-9d0e-1c2d-3f4a5b6c7d8e"),
    ("34","Ethan Green","1992-04-14","4c5d6e7f-8a9b-0c1d-2e3f-4a5b6c7d8e9f"),
    ("35","Sofia Adams","1980-09-07","5d6e7f8a-9b0c-1d2e-3f4a-5b6c7d8e9f0a"),
    ("36","Logan Nelson","1997-12-03","6e7f8a9b-0c1d-2e3f-4a5b-6c7d8e9f0a1b"),
    ("37","Aria Carter","1973-02-28","7f8a9b0c-1d2e-3f4a-5b6c-7d8e9f0a1b2c"),
    ("38","Jayden Mitchell","1991-05-19","8a9b0c1d-2e3f-4a5b-6c7d-8e9f0a1b2c3d"),
    ("39","Scarlett Perez","1985-08-08","9b0c1d2e-3f4a-5b6c-7d8e-9f0a1b2c3d4e"),
    ("40","Caleb Roberts","1979-10-22","0c1d2e3f-4a5b-6c7d-8e9f-0a1b2c3d4e5f"),
    ("41","Victoria Turner","1984-01-17","1d2e3f4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a"),
    ("42","Gabriel Phillips","1996-04-09","2e3f4a5b-6c7d-8e9f-0a1b-2c3d4e5f6a7b"),
    ("43","Amelia Campbell","1975-07-31","3f4a5b6c-7d8e-9f0a-1b2c-3d4e5f6a7b8c"),
    ("44","Jackson Parker","1994-10-15","4a5b6c7d-8e9f-0a1b-2c3d-4e5f6a7b8c9d"),
    ("45","Ella Evans","1987-03-05","5b6c7d8e-9f0a-1b2c-3d4e-5f6a7b8c9d0e"),
    ("46","Aiden Edwards","1993-06-20","6c7d8e9f-0a1b-2c3d-4f5a-6b7c8d9e0f1a"),
    ("47","Mila Collins","1972-09-12","7d8e9f0a-1b2c-3d4e-5f6a-7b8c9d0e1f2a"),
    ("48","Elijah Stewart","1981-12-25","8e9f0a1b-2c3d-4f5a-6a7b-8c9d0e1f2a3b"),
    ("49","Abigail Sanchez","1998-02-14","9f0a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c"),
    ("50","Matthew Morris","1974-05-06","0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d"),
    ("51","Ella Rogers","1999-08-18","1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e"),
    ("52","Sebastian Reed","1986-11-01","2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"),
    ("53","Avery Cook","1971-03-23","3d4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7f8a"),
    ("54","Carter Morgan","1990-07-07","4e5f6a7b-8c9d-0e1f-2a3b-4c5d6e7f8a9b"),
    ("55","Madison Bell","1989-10-30","5f6a7b8c-9d0e-1f2a-3b4c-5d6e7f8a9b0c"),
    ("56","Wyatt Murphy","1978-02-11","6a7b8c9d-0e1f-2a3b-4c5d-6e7f8a9b0c1d"),
    ("57","Luna Bailey","1997-05-25","7b8c9d0e-1f2a-3b4c-5d6e-7f8a9b0c1d2e"),
    ("58","Owen Rivera","1980-09-16","8c9d0e1f-2a3b-4c5d-6e7f-8a9b0c1d2e3f"),
    ("59","Harper Cooper","1992-12-04","9d0e1f2a-3b4c-5d6e-7f8a-9b0c1d2e3f4a"),
    ("60","Wyatt Richardson","1973-04-19","0d1f2a3b-4c5d-6e7f-8a9b-0c1d2e3f4a5b"),
    ("61","Aubrey Cox","1998-07-02","1e2a3b4c-5d6e-7f8a-9c0d-1d2e3f4a5b6c"),
    ("62","Logan Howard","1984-10-28","2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c"),
    ("63","Eleanor Ward","1976-01-09","3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d"),
    ("64","Lucas Torres","1991-04-12","4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e"),
    ("65","Scarlett Peterson","1987-07-21","5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f"),
    ("66","Jack Gray","1994-11-03","6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a"),
    ("67","Zoey Ramirez","1979-02-27","7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b"),
    ("68","Sebastian James","1993-06-14","8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c"),
    ("69","Mila Watson","1985-09-05","9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d"),
    ("70","Elijah Brooks","1972-12-18","0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e"),
    ("71","Aria Kelly","1996-03-30","1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f"),
    ("72","Gabriel Sanders","1988-07-09","2d3e4f5a-6b7c-8d9e-0f1a-2b3c4d5e6f7a"),
    ("73","Layla Price","1990-10-24","3e4f5a6b-7c8d-9e0f-1a2b-3c4d5e6f7a8b"),
    ("74","Jackson Bennett","1974-01-16","4f5a6b7c-8d9e-0f1a-2b3c-4d5e6f7a8b9c"),
    ("75","Avery Wood","1995-04-29","5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d"),
    ("76","Logan Barnes","1983-08-02","6b7c8d9e-0f1a-2b3c-4d5e-6f7a8b9c0d1e"),
    ("77","Chloe Ross","1997-11-13","7c8d9e0f-1a2b-3c4d-5e6f-7a8b9c0d1e2f"),
    ("78","Ethan Henderson","1975-02-19","8d9e0f1a-2b3c-4d5e-6f7a-8b9c0d1e2f3a"),
    ("79","Amelia Coleman","1992-05-07","9e0f1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b"),
    ("80","Matthew Jenkins","1980-09-25","0f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c"),
    ("81","Avery Perry","1994-12-11","1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"),
    ("82","Lucas Powell","1971-03-03","2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e"),
    ("83","Scarlett Long","1998-06-20","3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f"),
    ("84","Oliver Patterson","1982-10-16","4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"),
    ("85","Mia Hughes","1991-01-28","5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b"),
    ("86","Benjamin Flores","1976-04-04","6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c"),
    ("87","Abigail Washington","1993-07-19","7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d"),
    ("88","Samuel Butler","1985-11-30","8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e"),
    ("89","Evelyn Simmons","1973-02-08","9c0d1e2f-3a4b-5c6d-7e8f-9a0b1c2d3e4f"),
    ("90","Henry Foster","1990-05-22","0d1e2f3a-4b5c-6d7e-8f9a-0b1c2d3e4f5a"),
    ("91","Amelia Gonzales","1987-08-14","1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b"),
    ("92","Alexander Bryant","1995-12-07","2f3a4b5c-6d7e-8f9a-0b1c-2d3e4f5a6b7c"),
    ("93","Harper Russell","1974-03-26","3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d"),
    ("94","Jackson Griffin","1996-06-18","4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e"),
    ("95","Lily Diaz","1989-09-29","5c6d7e8f-9a0b-1c2d-3e4f-5a6b7c8d9e0f"),
    ("96","Sebastian Hayes","1970-12-21","6d7e8f9a-0b1c-2d3e-4f5a-6b7c8d9e0f1a"),
    ("97","Aria Myers","1992-02-02","7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b"),
    ("98","Gabriel Ford","1984-05-13","8f9a0b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c"),
    ("99","Layla Hamilton","1997-08-25","9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c4d"),
    ("100","Owen Graham","1975-11-09","0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e");