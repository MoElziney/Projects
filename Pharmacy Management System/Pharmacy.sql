CREATE DATABASE Pharmacy1

CREATE TABLE MEDICINE (
Medicine_SSN INT ,
Medicine_Name VARCHAR(50),
Medicine_Price INT ,
Medicine_Manufactor VARCHAR(30),
CONSTRAINT Medicine_PK PRIMARY KEY (Medicine_SSN),

);

CREATE TABLE Medicine_ExpiaryDate(
Medicine_SSN INT ,
Medicine_ID INT IDENTITY(1,1),
Expire_Date VARCHAR(10)

CONSTRAINT ExpiaryDate_PK PRIMARY KEY (Medicine_SSN,Medicine_ID),
CONSTRAINT ExpiaryDate_FK FOREIGN KEY (Medicine_SSN) REFERENCES MEDICINE(Medicine_SSN)
)
ALTER TABLE Medicine_ExpiaryDate
ADD  Expire_Statu VARCHAR(10)

UPDATE Medicine_ExpiaryDate SET Expire_Statu='EXP' WHERE Expire_Date<'2023-12-1' 
UPDATE Medicine_ExpiaryDate SET Expire_Statu='Warning' WHERE Expire_Date<'2024-1-1' AND Expire_Date>='2023-12-1'
UPDATE Medicine_ExpiaryDate SET Expire_Statu='Valid' WHERE Expire_Date>='2024-1-1' 

CREATE TABLE Medicine_EffectiveMaterial(
Medicine_SSN INT ,
Material Varchar(20),
Concentration int,
unit_concentration varchar(5)

CONSTRAINT EffectiveMaterial_PK PRIMARY KEY (Medicine_SSN,Material),
CONSTRAINT EffectiveMaterial_FK FOREIGN KEY (Medicine_SSN) REFERENCES MEDICINE(Medicine_SSN)
)

---INSERTS---
INSERT  MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(51561323,'Cefotax 1GM Vial',30,'EPICO')
---
INSERT  Medicine_EffectiveMaterial
VALUES(51561323,'Cefotaxime',1,'GM')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(51561323,'2023-12-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(51561323,'2024-3-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(51561323,'2024-5-1')
----------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(56511231,'Biovit B12 Depot AMP',19,'MUP')
---
INSERT  Medicine_EffectiveMaterial
VALUES(56511231,'Folic Acid',1,'mg')

INSERT  Medicine_EffectiveMaterial
VALUES(56511231,'Vitamin B6',1,'mg')

INSERT  Medicine_EffectiveMaterial
VALUES(56511231,'Vitamin B12',20,'mg')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(56511231,'2024-2-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(56511231,'2024-5-1')
--------------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(51328161,'Davalindi 5000 I.U 30 Tab',38,'MUP')
---

INSERT  Medicine_EffectiveMaterial
VALUES(51328161,'Vitamin D3',5000,' UNIT')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(51328161,'2024-1-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(51328161,'2024-3-1')
---------------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(35115151,'Panadol Advance 500mg 24 TAB',39,'Glaxo')
---
INSERT  Medicine_EffectiveMaterial
VALUES(35115151,'Paracetamol',500,'mg')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(35115151,'2024-3-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(35115151,'2024-4-1')
-----------------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(54622569,'Cetal 1000mg 15 TAB',24,'EPICO')
---
INSERT  Medicine_EffectiveMaterial
VALUES(54622569,'Paracetamol',1000,'mg')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(54622569,'2024-2-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(54622569,'2024-1-1')
------------------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(11262359,'Oplex-N Syrup 125ml',19,'Amyria')
---
INSERT  Medicine_EffectiveMaterial
VALUES(11262359,'Guaifenesin',12.5,' mg')

INSERT  Medicine_EffectiveMaterial
VALUES(11262359,'Oxomemazine',20 ,'mg')

INSERT  Medicine_EffectiveMaterial
VALUES(11262359,'Sodium Benzoat',32 ,'mg')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(11262359,'2024-3-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(11262359,'2024-2-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(11262359,'2024-1-1')
---------------------------------
INSERT MEDICINE(Medicine_SSN,Medicine_Name,Medicine_Price,Medicine_Manufactor)
VALUES(14236262,'Predsol Syrup 50ml',24,'Borg')
---
INSERT  Medicine_EffectiveMaterial
VALUES(14236262,'Prednisolon',5 ,'mg')
---
INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(14236262,'2024-2-1')

INSERT  Medicine_ExpiaryDate(Medicine_SSN,Expire_Date)
VALUES(14236262,'2024-1-1')

----------------------
SELECT Material ,MEDICINE.Medicine_SSN 
FROM Medicine_EffectiveMaterial , MEDICINE
WHERE  MEDICINE.Medicine_SSN = Medicine_EffectiveMaterial.Medicine_SSN

SELECT MEDICINE.Medicine_SSN ,MEDICINE.Medicine_Name,STRING_AGG(Medicine_ExpiaryDate.Expire_Date,' | ') AS Expiry_Information
FROM MEDICINE, Medicine_ExpiaryDate
WHERE MEDICINE.Medicine_SSN=Medicine_ExpiaryDate.Medicine_SSN 
GROUP BY MEDICINE.Medicine_SSN,MEDICINE.Medicine_Name,Medicine_ExpiaryDate.Expire_Statu


SELECT MEDICINE.Medicine_Name ,MEDICINE.Medicine_SSN,Medicine_EffectiveMaterial.Material,Medicine_EffectiveMaterial.Concentration,Medicine_EffectiveMaterial.unit_concentration
FROM MEDICINE INNER JOIN Medicine_EffectiveMaterial
ON MEDICINE.Medicine_SSN=Medicine_EffectiveMaterial.Medicine_SSN
ORDER BY Medicine_EffectiveMaterial.Material ASC


SELECT Medicine_Name ,Material,MAX(Concentration) AS MAX_VALUE
FROM MEDICINE ,Medicine_EffectiveMaterial
WHERE MEDICINE.Medicine_SSN IN
(SELECT Medicine_SSN FROM Medicine_EffectiveMaterial WHERE Material = 'Paracetamol' AND Concentration = 
(SELECT MAX(Concentration) FROM Medicine_EffectiveMaterial WHERE Material = 'Paracetamol'))
AND Material= 'Paracetamol'
GROUP BY Medicine_Name ,Material

----full join

----------------------
-----------------------------
---ORDER(Mariam)---------------------
-----------------------------
create table ordered(
  ORDER_ID          int  ,
  Medcine_order_ssn  int ,
  ORDER_Amount   int ,
  ORDER_Total  AS ORDER_Amount*ORDER_Price  ,
  ORDER_Price     int ,
  ORDERE_Date   varchar(20),
  constraint  ORDER11_PK  Primary key (ORDER_ID ),
  CONSTRAINT ORDER11_FK FOREIGN KEY (Medcine_order_ssn) REFERENCES MEDICINE(Medicine_SSN)
  );

 
  --------------------------------------------------
 
  insert into ordered( ORDER_ID , Medcine_order_ssn,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 230000,51561323, 60 , 39, '2023-4-5' )

  insert into ordered( ORDER_ID  ,Medcine_order_ssn,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 238888, 51561323,54, 19, '2023-6-5' )

  insert into ordered( ORDER_ID ,Medcine_order_ssn ,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 238844,35115151, 50 , 19, '2023-7-5' )

  insert into ordered ( ORDER_ID , Medcine_order_ssn,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 236117, 35115151,30  , 38, '2023-7-6' )

  insert into ordered ( ORDER_ID ,Medcine_order_ssn ,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 236240, 14236262,70, 39, '2023-6-6' )

  insert into ordered ( ORDER_ID ,Medcine_order_ssn , ORDER_Amount,ORDER_Price ,ORDERE_Date)
  values ( 236880, 1423626280, 66,24, '2023-8-6' )

  insert into ordered ( ORDER_ID ,Medcine_order_ssn ,ORDER_Amount ,ORDER_Price ,ORDERE_Date)
  values ( 280000, 51328161,65, 38, '2023-4-6' )

  insert into ordered ( ORDER_ID ,Medcine_order_ssn ,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 236277, 11262359,90, 39, '2023-10-6' )

  insert into ordered ( ORDER_ID ,Medcine_order_ssn ,ORDER_Amount, ORDER_Price ,ORDERE_Date)
  values ( 236237, 14236262,20, 24, '2023-10-6' )

  ----------------------------------------------------------

  
 
 ------------ first-----------------------------
SELECT  COUNT(ORDER_ID) AS num_orders, SUM(ORDER_Total) AS Total_order
FROM ordered
where ORDER_Price between 19 and 39 ;--

------- second ------------------------------------
SELECT ORDERE_Date, COUNT(ORDER_ID)AS num_orders ,SUM(ORDER_Total) AS total_order_amount
FROM ordered
GROUP BY ORDERE_Date
ORDER BY total_order_amount DESC;--
  ----------------------------------------------------------
SELECT ordered.* , MEDICINE.Medicine_Name,MEDICINE.Medicine_SSN,MEDICINE.Medicine_Price
FROM ordered JOIN MEDICINE
ON ordered.Medcine_order_ssn= MEDICINE.Medicine_SSN

------------------------------------------------------
SELECT ORDER_ID, ORDERED.Medcine_order_ssn,ORDERE_Date,Medicine_ExpiaryDate.Expire_Date,Medicine_ExpiaryDate.Expire_Statu
FROM Ordered LEFT JOIN Medicine_ExpiaryDate
ON Medcine_order_ssn=Medicine_ExpiaryDate.Medicine_SSN--
------------------------------------------------------
SELECT DISTINCT O.ORDER_ID, ORDER_Amount,(SELECT MAX(Receipt_value) FROM Receipt WHERE Receipt.ORDER_ID = O.ORDER_ID) AS MaxReceiptValue
FROM ordered O,Receipt R
------------------------------------------------------
SELECT ordered.ORDER_ID ,Receipt.*
FROM Receipt
FULL OUTER JOIN  ordered  ON ordered.ORDER_ID = Receipt.ORDER_ID
------------------------------------------------------



-----------------------------------------------
-----------------------------------
---------------------Hala----------
-----------------------------------
CREATE TABLE Expense  (
	Expense_ID INT NOT NULL,
	Paid_Loss INT,
	Loss_Type VARCHAR(20),
	Paid_salary INT,
	Total_paid_expense AS Paid_Loss+Paid_salary,
	
	CONSTRAINT expense_pk PRIMARY KEY (Expense_ID)
	);

	ALTER TABLE Expense
	ADD Expense_Month VARCHAR(30);

CREATE TABLE Receipt (
	Receipt_ID INT NOT NULL,
	Expense_ID INT ,
	Receipt_Date VARCHAR(10),
	Receipt_value INT,
	Receipt_Discount INT,
	Order_ID INT 

	CONSTRAINT receipt_pk PRIMARY KEY (Receipt_ID),

	CONSTRAINT receipt_fk FOREIGN KEY (Expense_ID) REFERENCES Expense (Expense_ID),
	CONSTRAINT receipt_fk2 FOREIGN KEY (Order_ID) REFERENCES Ordered(ORDER_ID)

	);
	ALTER TABLE Receipt
	ADD Cahsier_ID INT;


-----------Insert------------
INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (345678, 500 ,'Broken product','12/3/2023' );


INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (456789, 200 ,'Broken product','12/4/2023' );

INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (345344, 600 ,'expired product','12/4/2023' );

INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (345878, 500 ,'expired product','12/5/2023' );

INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (756394, 8000 ,'Broken product','12/5/2023' );

INSERT INTO Expense (Expense_ID, Paid_Loss,Loss_Type,Expense_Month)
VALUES (029374, 500 ,'Broken product','12/6/2023' );
------------------------------------------------------------------
INSERT INTO Receipt 
VALUES (165437, 345678, '12/3/2023', 2500, 15,230000, 235903);

	INSERT INTO Receipt VALUES (123456, 456789, '12/4/2023', 3200, 26,238888, 235907);

	INSERT INTO Receipt VALUES (543287, 345878, '12/5/2023', 4000, 20,238844, 235911);

	INSERT INTO Receipt VALUES (366678, 029374,'12/6/2023', 6800, 45,236117, 235915);

	INSERT INTO Receipt VALUES (176573, 345678,  '12/6/2023', 7000, null,236240, 235916);

	INSERT INTO Receipt VALUES (654321, 456789, '12/4/2023', 3200, 75,236880, 235917);

	INSERT INTO Receipt VALUES (123855, 456789, '12/4/2023', 3200, null,280000, 235918);

	INSERT INTO Receipt VALUES (479589, 456789,  '12/4/2023', 3200, 26,236277, 235919);
------------------------------------------------------------------

-- calculates the total expenses-- --hala--
SELECT SUM(Receipt_value + Paid_salary)
FROM Expense,Receipt
where Expense.Expense_ID=Receipt.Expense_ID
and Receipt_Date like'12/3/2023'
and Expense_Month like'12/3/2023'
and Receipt_Date=Expense_Month;

-- Calculates the total paid losses for the month oo april-- --hala--
SELECT SUM(Paid_Loss)
FROM Expense
where Expense_Month like '%/4/%'

--Gives the Receipt_ID if all the expired product related expenses-- --hala--


SELECT Receipt_ID
FROM Expense,Receipt
WHERE Expense.Expense_ID = Receipt.Expense_ID
AND Loss_Type = 'expired product';
--select the receipts that are related to paid loss that are worth more that 300 in paid loss-- --hala--
SELECT Receipt_ID
FROM Expense,Receipt
WHERE Expense.Expense_ID = Receipt.Expense_ID
AND Paid_Loss> 300;

--FIND THE phone numbers of each employee who made a receipt in the month of may-- --hala--
SELECT First_name+' '+Last_name as'employee name', Primary_Phone_number,Secondary_phone_number
FROM Staff,staff_phone_number 
where Staff_ID=S_ID
and Staff_ID in(
	SELECT Cashier.Cashier_ID
	FROM Cashier,Receipt
	where Receipt.Cahsier_ID=Cashier.Cashier_ID
	and Receipt_Date like '%/5/%'
);


--give me the name s of the cashiers who made the biggest receipt value greater than 4000 and their Cashier_Desk-- --hala--
SELECT First_name+' '+Last_name as'employee name',Cashier_Desk
FROM Cashier,Staff
WHERE Cashier.Cashier_ID=Staff_ID 
and Staff_ID in(
	SELECT Receipt.Cahsier_ID
	FROM Receipt
	GROUP BY Receipt.Cahsier_ID
	HAVING MAX(Receipt.Receipt_value)>4000
);

-give me the names of the cashiers who made ordrs in aprile--
	select First_name+' '+Last_name
	from Staff,Cashier
	where Cashier_ID=Staff_ID
	AND Cashier_ID IN(
	SELECT Receipt.Cahsier_ID
	FROM ordered,Receipt
	where Receipt.order_id=ordered.ORDER_ID
	and ordered.ORDERE_Date like'%/4/%'
	);

--selecet receipts related to the orders made-- --Mariam--
SELECT Receipt.Receipt_ID
FROM ordered,Receipt
WHERE ordered.ORDER_ID=Receipt.order_id;


-------------------------------
----------------Mohamed--------
-------------------------------
CREATE TABLE Insurance
(
Insurance_Provider VARCHAR(15) NOT NULL,
Insurance_Value INT NOT NULL,
Insurance_Start_Date INT NOT NULL,
Insurance_End_Date INT NOT NULL,
Insurance_Period AS (Insurance_End_Date-Insurance_Start_Date)+1,
Insurance_ID VARCHAR(7) NOT NULL,
CONSTRAINT Insurance_pk
PRIMARY KEY (Insurance_ID),
CONSTRAINT Insurance_fk
FOREIGN KEY (Insurance_ID) REFERENCES Staff (Staff_ID)

);
DELETE FROM Insurance
DROP TABLE Insurance
CREATE TABLE Staff
(
Salary INT NOT NULL,
Staff_ID VARCHAR(7) NOT NULL,
Check_In INT NOT NULL,
Check_Out INT NOT NULL,
Work_Hours AS (Check_Out-Check_In)+1,
CONSTRAINT Staff_pk
PRIMARY KEY (Staff_ID)
);

CREATE TABLE Cashier
(
Cashier_Desk INT NOT NULL,
Cashier_ID VARCHAR(7) NOT NULL,
CONSTRAINT Cashier_pk
PRIMARY KEY (Cashier_ID),
CONSTRAINT Cashier_fk
FOREIGN KEY (Cashier_ID) REFERENCES Staff (Staff_ID)
);

CREATE TABLE Pharmacist
(
Medical_Degree VARCHAR(10) NOT NULL,
Pharmacist_ID VARCHAR(7) NOT NULL,
CONSTRAINT Pharmacist_pk
PRIMARY KEY (Pharmacist_ID),
CONSTRAINT Pharmacist_fk
FOREIGN KEY (Pharmacist_ID) REFERENCES Staff (Staff_ID)
);

CREATE TABLE Name
(
ID VARCHAR(7) NOT NULL,
Frist_Name VARCHAR(15) NOT NULL,
Middle_Name VARCHAR(15) NOT NULL,
Last_Name VARCHAR(15) NOT NULL,
CONSTRAINT Name_pk
PRIMARY KEY (ID,Last_Name),
CONSTRAINT Name_fk
FOREIGN KEY (ID) REFERENCES Staff (Staff_ID)
);

CREATE TABLE Contant_Information
(
Employee_ID VARCHAR(7) NOT NULL,
Address VARCHAR(50),
Telephon VARCHAR(15),
CONSTRAINT Information_pk
PRIMARY KEY (Employee_ID,Telephon),
CONSTRAINT Information_fk
FOREIGN KEY (Employee_ID) REFERENCES Staff (Staff_ID)
);



---------- INSERT INTO Insurance --------------

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Allianz',235903,6000,1,6);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Arope',235904,4500,3,5);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('AXA',235905,8000,8,11);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Allianz',235906,4000,5,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Arope',235907,6000,3,6);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('AXA',235908,16000,1,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Allianz',235909,11000,1,11);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Arope',235910,1500,12,12);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('AXA',235911,4000,2,3);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Allianz',235912,4000,5,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Arope',235913,7500,4,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('AXA',235914,9000,1,6);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('GIG ',235915,1500,5,7);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Orient',235916,3000,3,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Royal ',235917,4000,11,12);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('AXA ',235918,4000,5,8);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Orient',235919,6000,1,6);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Royal',235920,1500,12,12);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Royal',235921,1500,12,12);

INSERT INTO Insurance(Insurance_Provider,Insurance_ID,Insurance_Value,Insurance_Start_Date,Insurance_End_Date)
VALUES('Allianz',235922,7500,4,8);

---------- INSERT INTO Staff --------------


INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235903,3000,1,6);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235904,6000,1,6);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235905,3000,1,6);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235906,4500,1,6);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235907,2500,7,12);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235908,5500,7,12);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235909,8000,7,12);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235910,4000,7,12);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235911,3500,13,18);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235912,5200,13,18);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235913,8500,13,18);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235914,4300,13,18);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235915,2500,1,6);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235916,2700,7,12);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235917,2700,12,17);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235918,2600,19,24);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235919,2200,19,24);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235920,4000,19,24);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235921,9000,19,24);

INSERT INTO Staff(Staff_ID, Salary,Check_In,Check_Out)
VALUES (235922,4850,19,24);


---------- INSERT INTO Name --------------


INSERT INTO Contant_Information
VALUES (235903,'Maddi,1 district, 22 streat, 50 building','01185768312');

INSERT INTO Contant_Information
VALUES (235903,'','01585438312');

INSERT INTO Contant_Information
VALUES (235904,'Maddi,5 district, 40 streat, 22 building','01087321456');

INSERT INTO Contant_Information
VALUES (235905,'Maddi,3 district, 28 streat, 33 building','01576541236');

INSERT INTO Contant_Information
VALUES (235906,'Maddi,2 district, 25 streat, 25 building','01576574636');

INSERT INTO Contant_Information
VALUES (235907,'Maddi,7 district, 5 streat, 10 building','01176564326');

INSERT INTO Contant_Information
VALUES (235907,'','01176534561');

INSERT INTO Contant_Information
VALUES (235908,'Nasr City,3 district, 20 streat, 80 building','01276598346');

INSERT INTO Contant_Information
VALUES (235908,'','01047659274');

INSERT INTO Contant_Information
VALUES (235909,'Nasr City,2 district, 12 streat, 30 building','01000417786');

INSERT INTO Contant_Information
VALUES (235910,'Nasr City,5 district, 43 streat, 110 building','01000534467');

INSERT INTO Contant_Information
VALUES (235910,'','01101230681');

INSERT INTO Contant_Information
VALUES (235911,'Nasr City,6 district, 50 streat, 140 building','01101231365');

INSERT INTO Contant_Information
VALUES (235912,'Nacr City,3 district, 22 streat,30 building','01503999875');

INSERT INTO Contant_Information
VALUES (235913,'Zamalek,2 district, 15 streat,25 building','01503911187');

INSERT INTO Contant_Information
VALUES (235914,'Zamalek,4 district, 33 streat,88 building','01503911187');

INSERT INTO Contant_Information
VALUES (235915,'Zamalek,1 district, 5 streat,12 building','01503965187');

INSERT INTO Contant_Information
VALUES (235916,'Zamalek,7 district, 60 streat,150 building','01101231712');

INSERT INTO Contant_Information
VALUES (235917,'Zamalek,3 district, 29 streat,37 building','011765345543');

INSERT INTO Contant_Information
VALUES (235918,'Shrouk,1 district, 9 streat,12 building','01011822444');

INSERT INTO Contant_Information
VALUES (235919,'Shrouk,2 district, 17 streat,22 building','01101231437');

INSERT INTO Contant_Information
VALUES (235920,'Shrouk,3 district, 25 streat,34 building','01507778265');

INSERT INTO Contant_Information
VALUES (235921,'Shrouk,4 district, 36 streat,46 building','01096688544');

INSERT INTO Contant_Information
VALUES (235922,'Shrouk,5 district, 44 streat,58 building','01507778241');

---------- INSERT INTO Pharmacist --------------

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235904,'doctor');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235905,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235906,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235908,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235909,'doctor');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235910,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235912,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235913,'doctor');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235914,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235920,'assistant');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235921,'doctor');

INSERT INTO Pharmacist (Pharmacist_ID,Medical_Degree)
VALUES (235922,'assistant');

---------- INSERT INTO Name --------------

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235903,'Mohamed', 'Ali', 'Ahmed');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235904,'Mahmoud', 'Zeyad', 'Ahmed');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235905,'Asmaa', 'Khaled', 'Ali');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235906,'Marwa', 'moaz', 'Khaled');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235907,'Ali', 'Mohamed', 'Zien');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235908,'Zien', 'Marwan', 'Foad');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235909,'Nagy', 'Ali', 'Saed');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235910,'nour', 'Khaled', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235911,'hitham', 'Mohamed', 'Samy');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235912,'Farida', 'Khaled', 'Osman');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235913,'Ahmed', 'Yousef', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235914,'Mohamed', 'Nagy', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235915,'Mohamed', 'Ali', 'Nagy');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235916,'hossam', 'belal', 'Ahmed');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235917,'Mohamed', 'Hossam', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235918,'Marwa', 'Hossam', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235919,'Hana', 'Mohamed', 'Ali');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235920,'Marwa', 'Hossam', 'Naser');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235921,'Ayman', 'Ahmed', 'Mahmoud');

INSERT INTO Name (ID,Frist_Name,Middle_Name,Last_Name)
VALUES (235922,'Nagy', 'Hossam', 'Naser');

---------- INSERT INTO Cashier --------------


INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235903,1100);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235907,800);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235911,2000);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235915,2200);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235916,3000);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235917,3200);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235918,2500);

INSERT INTO Cashier (Cashier_ID, Cashier_Desk)
VALUES (235919,1500);


SELECT Pharmacist_ID,Address FROM Pharmacist
JOIN Contant_Information
ON Pharmacist_ID = Employee_ID 
WHERE Address LIKE 'Maddi%' AND Medical_Degree = 'assistant';--

SELECT DISTINCT Last_Name FROM Name
JOIN Cashier ON ID = ANY(SELECT Cashier_ID FROM Cashier
JOIN Insurance
ON Cashier_ID = Insurance_ID
WHERE Insurance_Provider = 'AXA')--

SELECT DISTINCT Employee_ID,Telephon FROM Contant_Information
JOIN Pharmacist ON
Employee_ID = (SELECT Pharmacist_ID FROM Pharmacist
JOIN Insurance ON Pharmacist_ID = Insurance_ID
WHERE  Medical_Degree = 'doctor' AND Insurance_Provider = 'Royal' AND Address LIKE 'Shrouk%')--

SELECT COUNT(Employee_ID) AS 'Numbers of Cashier' FROM Contant_Information
JOIN Cashier ON Employee_ID = Cashier_ID
WHERE Address LIKE 'Zamalek%'

SELECT DISTINCT Last_Name, ID FROM Name
 JOIN Receipt ON ID =(SELECT Receipt.Cahsier_ID FROM Receipt
 JOIN ordered on Receipt.Order_ID = ordered.ORDER_ID
 WHERE Receipt_value =2500 )



-------------------------------
------------------Nour---------
-------------------------------
CREATE TABLE STOCK (
  M_Ssn INT NOT NULL,
  Stock_quantity INT,
  Safety_stock INT,
  Stock_state VARCHAR(50) NOT NULL,

  CONSTRAINT Stock_PK PRIMARY KEY (M_Ssn),
  CONSTRAINT Stock_FK FOREIGN KEY (M_Ssn) REFERENCES Medicine (Medicine_SSN)
);


--------------------------------------Insert1----------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(51561323,20,10,'AVAILABLE');
---------------------------------------Insert2---------------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(56511231,40,2,'AVAILABLE');
--------------------------------------Insert3----------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(51328161,0,0,'UNAVAILABLE');
--------------------------------------4----------------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(35115151,0,0,'NEED');
--------------------------------------Insert5----------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)	
VALUES(11262359,5,4,'NEED');
-------------------------------------6-----------------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(54622569,100,60,'AVAILABLE');
--------------------------------------Insert--7--------------------------------------------------
INSERT INTO STOCK (M_Ssn,Stock_quantity,Safety_stock,Stock_state)
VALUES(14236262,0,0,'UNAVAILABLE AND NEED');
---------------------------------------TABLE STOCK DRAWER------------------------------------------------------------
create table STOCK_DRAWER(
MED_Ssn INT NOT NULL,
Medicine_ID INT NOT NULL,
Drawer_Number INT NOT NULL,
CONSTRAINT DRAWER_PK PRIMARY KEY(MED_Ssn, Medicine_ID),
CONSTRAINT DRAWER_FK FOREIGN KEY(MED_Ssn) REFERENCES STOCK(M_ssn),
CONSTRAINT DRAWER_MSSN_FK FOREIGN KEY(MED_Ssn,Medicine_ID) REFERENCES Medicine_ExpiaryDate(Medicine_SSN,Medicine_ID)
);

INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(51328161,6,1);
---------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(51561323,3,2);
----------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(11262359,14,4);
----------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(35115151,8,7);
-----------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(51561323,2,3);
-----------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(54622569,10,4);
-----------------------------------------------------------------------------------------------------
INSERT INTO STOCK_DRAWER (MED_Ssn,Medicine_ID,Drawer_Number)
VALUES(56511231,4,9);
-----------------------------------TABLE REFUND------------------------------------------------------------
CREATE TABLE REFUND (
  Refund_id INT NOT NULL,
  Refund_value INT NOT NULL,
  Refund_quantity INT NOT NULL,
  Refund_start_date DATE NOT NULL,
  Refund_end_date DATE NOT NULL,
  Refund_reason VARCHAR(50) NOT NULL,
  medicine_ssn INT NOT NULL,
  Medicine_ID INT NOT NULL,
  Pharmacist_ID VARCHAR(7) NOT NULL,
  CONSTRAINT Refund_PK PRIMARY KEY (Refund_id),
  CONSTRAINT Refund_FK FOREIGN KEY (medicine_ssn) REFERENCES STOCK(M_Ssn),
  CONSTRAINT Refund_Pharmacist_FK FOREIGN KEY (Pharmacist_ID) REFERENCES Pharmacist(Pharmacist_ID),
  CONSTRAINT Refund_Medicine_FK FOREIGN KEY (medicine_ssn,Medicine_ID) REFERENCES STOCK_DRAWER(MED_Ssn, Medicine_ID)
);

--------------------------------------Insert1----------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1299,500,5,'2023-12-22','2023-12-30','Broken',56511231,4,'235913');
---------------------------------------2---------------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1251,200,5,'2023-10-22','2023-10-30','ERROR IN PACKAGING',54622569,10,'235904');
--------------------------------------Insert3----------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1249,12000,900,'2023-9-2','2023-9-17','MISSING CAPSULES',11262359,14,'235909');
--------------------------------------4----------------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1253,1000,20,'2023-12-22','2023-1-12','Broken',35115151,8,'235913')
--------------------------------------Insert5----------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1291,1250,100,'2023-2-4','2023-2-8','Broken',51328161,6,'235921');
-------------------------------------6-----------------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1258,500,40,'2023-12-22','2023-12-30','APPROACH EXPIRY DATE',54622569,10,'235921');
--------------------------------------------7----------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1201,200,20,'2023-12-22','2023-12-30','APPROACH EXPIRY DATE',11262359,14,'235905');
--------------------------------------Insert---8-------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1701,5000,10000,'2023-12-22','2023-12-30','Broken',51561323,2,'235908');
-----------------------------------------------9-------------------------------------------------
INSERT INTO REFUND (Refund_id,Refund_value,Refund_quantity,Refund_start_date,Refund_end_date, Refund_reason,medicine_ssn,Medicine_ID,Pharmacist_ID)
VALUES(1459,100,5,'2023-12-23','2023-12-30','Broken',51561323,3,'235905');

---------------------------Quaries1-------------------------------------------------------------------
SELECT MONTH(Refund_start_date) AS 'Refund Month', AVG(Refund_quantity) AS 'Average Refunded Quantity'
FROM REFUND
GROUP BY MONTH(Refund_start_date);
---------------------------Quaries2-------------------------------------------------------------------
SELECT Medicine_Name AS 'Medicine Name', Stock_quantity
FROM STOCK, MEDICINE M LEFT OUTER JOIN Medicine_ExpiaryDate E
ON M.Medicine_SSN = E.Medicine_SSN 
WHERE E.Medicine_SSN IN (Select M_Ssn)
GROUP BY Stock_quantity, Medicine_Name;
																												
-------------------------------Quaries3-----------------------------------------------------------------------
SELECT Medicine_Name,Refund_start_date AS 'Refund Date', Refund_reason AS 'Refund Reason'
FROM REFUND R JOIN MEDICINE M
ON R.medicine_ssn = M.Medicine_SSN;

--------------------------Quaries4---------------------------------------------------------------------
UPDATE REFUND
SET Refund_end_date ='2023-12-25'
WHERE Refund_id =1253;
--------------------------Quaries5---------------------------------------------------------------------
SELECT E.Medicine_ID AS 'MEDICINE ID',Refund_id  AS 'Refund ID',Refund_start_date AS 'Refund start day',Refund_end_date AS 'Refund END day',DATEDIFF(DAY, Refund_start_date, Refund_end_date) AS Duration
FROM Medicine_ExpiaryDate E,REFUND R, STOCK S
WHERE R.medicine_ssn = S.M_Ssn; 

--------------------------Quary6-------------------------------------------------------------------------
SELECT M.Medicine_ID AS 'MEDICINE ID',M.Medicine_SSN AS 'Medicine SSN' , Stock_quantity AS 'STOCK  QAUNTITY',Safety_stock AS 'Safety stock'
FROM STOCK S,Medicine_ExpiaryDate M;

---------------------------Quary7//--------------------------------------------------------------------------------
SELECT AVG(Refund_value) AS Avg_refund_value,Refund_start_date AS 'Refund start day',Refund_end_date AS 'Refund END day'
FROM REFUND 
RIGHT JOIN STOCK 
ON medicine_ssn = M_Ssn
GROUP BY Refund_id,Refund_start_date,Refund_end_date
ORDER BY Avg_refund_value DESC;
--------------------------Quary8------------------------------------------------------------------------
SELECT *
FROM Medicine_ExpiaryDate  FULL JOIN STOCK
ON M_Ssn = Medicine_SSN;
---------------------------Quary9------------------------------------------------------------------------
SELECT  DISTINCT Drawer_NUmber AS 'Drawer Number' ,MED_Ssn AS 'Medicine Serial number',Stock_quantity AS 'Stock quantity'
FROM STOCK_DRAWER join STOCK
ON  MED_Ssn=M_Ssn;
---------------------------------------------------------------------------------------------------------
SELECT Refund_reason AS 'Refund Reason', COUNT(*) AS 'Number of Refunds' ,SUM(Refund_value)AS'Total Refund'
FROM REFUND
GROUP BY Refund_reason;
----------------------------------------------------------------------------------------------------------
SELECT DISTINCT P.Pharmacist_ID AS 'Pharmacist ID',Refund_id AS 'Refund ID',medicine_ssn AS 'Medicine Serial Number'
FROM Pharmacist P,REFUND R
WHERE P.Pharmacist_ID=R.Pharmacist_ID AND R.medicine_ssn IN (select M_Ssn
															 FROM STOCK
													       	 WHERE Safety_stock <= 100);
---------------------------------------------------------------------------------------------------------
UPDATE STOCK
SET Stock_quantity = Stock_quantity+1000
WHERE M_Ssn =14236262;
---------------------------------------------------------------------------------------------------------
UPDATE REFUND
SET Refund_quantity = Refund_quantity+50
WHERE Refund_id =1299;
---------------------------------------------------------------------------------------------------------
UPDATE STOCK
SET Safety_stock = NULL,Stock_quantity = NULL
WHERE M_Ssn IN (51328161, 35115151, 14236262);
