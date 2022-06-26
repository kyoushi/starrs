SET GLOBAL local_infile=1;
USE starss2;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/department.csv' 
INTO TABLE department 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/courses.csv' 
INTO TABLE course 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
SET FOREIGN_KEY_CHECKS=0;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/department_course.csv' 
INTO TABLE department_has_course 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/section.csv' 
INTO TABLE section 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/gradeConversion.csv' 
INTO TABLE gradeConversion 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;
-- INSERT INTO 
-- 	department_has_course(Course_courseNumber, Department_idDepartment)
-- VALUES
-- ('MSE_600','MSE'),
-- ('MSE_601','MSE'),
-- ('MSE_602','MSE'),
-- ('MSE_603','MSE'),
-- ('MSE_604','MSE'),
-- ('MSE_605','MSE'),
-- ('MSE_606','MSE'),
-- ('MSE_607','MSE'),
-- ('MSE_608','MSE'),
-- ('MSE_609','MSE'),
-- ('MSE_610','MSE'),
-- ('MSE_611','MSE'),
-- ('MSE_612','MSE'),
-- ('MSE_613','MSE'),
-- ('MSE_614','MSE'),
-- ('MSE_615','MSE'),
-- ('MSE_616','MSE'),
-- ('MS_500','MS'),
-- ('MS_501','MS'),
-- ('MS_502','MS'),
-- ('MS_503','MS'),
-- ('MS_504','MS'),
-- ('MS_505','MS'),
-- ('MS_506','MS'),
-- ('MS_507','MS'),
-- ('MS_508','MS'),
-- ('MS_509','MS'),
-- ('MS_510','MS'),
-- ('MS_511','MS'),
-- ('MS_512','MS'),
-- ('MS_513','MS'),
-- ('MS_514','MS'),
-- ('MS_515','MS'),
-- ('MS_516','MS');