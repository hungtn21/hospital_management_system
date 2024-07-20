
CREATE TABLE "user"(
    "user_id" INTEGER PRIMARY KEY,
    "password" VARCHAR(255) NULL,
    "name" VARCHAR(255) NULL,
    "dob" DATE NULL,
    "sex" VARCHAR(255) NULL,
    "phone" VARCHAR(255) NULL,
    "address" VARCHAR(255) NULL,
    "role" INTEGER NULL
);
CREATE TABLE "patient"(
    "user_id" INTEGER PRIMARY KEY REFERENCES "user"("user_id"),
    "blood_type" VARCHAR(255) NULL
);
CREATE TABLE "department"(
    "department_id" INTEGER PRIMARY KEY,
    "department_name" VARCHAR(255) NOT NULL
);
CREATE TABLE "doctor"(
    "user_id" INTEGER PRIMARY KEY REFERENCES "user"("user_id"),
    "department_id" INTEGER NULL REFERENCES "department"("department_id"),
    "salary" DOUBLE PRECISION NULL
);
CREATE TABLE "symptom"(
    "symptom_id" INTEGER PRIMARY KEY,
    "symptom_name" VARCHAR(255) NULL,
    "department_id" INTEGER NULL REFERENCES "department"("department_id")
);
CREATE TABLE "test"(
    "test_id" INTEGER PRIMARY KEY,
    "test_name" VARCHAR(255) NULL,
    "fee" DOUBLE PRECISION NULL
);
CREATE TABLE "examination"(
    "examination_id" INTEGER PRIMARY KEY,
    "user_id" INTEGER NULL REFERENCES "patient"("user_id"),
    "date" DATE,
    "doctor_id" INTEGER NULL REFERENCES "doctor"("user_id"),
	"age" INTEGER NULL,
    "height" DOUBLE PRECISION NULL,
    "weight" DOUBLE PRECISION NULL,
    "blood_pressure_S" INTEGER NULL,
    "blood_pressure_D" INTEGER NULL,
    "heart_rate" INTEGER NULL,
    "fee" DOUBLE PRECISION NULL,
    "conclusion" VARCHAR(255) NULL,
    "time_arranged" TIME NULL
);
CREATE TABLE "medicine"(
    "medicine_id" INTEGER PRIMARY KEY,
    "medicine_name" VARCHAR(255) NULL,
    "number_left" INTEGER NULL,
    "cost_per" DOUBLE PRECISION NULL
);
CREATE TABLE "test_join"(
    "examination_id" INTEGER NOT NULL REFERENCES "examination"("examination_id"),
    "test_id" INTEGER NOT NULL REFERENCES "test"("test_id"),
    "result" VARCHAR(255) NULL
);
CREATE TABLE "symptom_join"(
    "examination_id" INTEGER NOT NULL REFERENCES "examination"("examination_id"),
    "symptom_id" INTEGER NOT NULL REFERENCES "symptom"("symptom_id")
);

CREATE TABLE "medicine_prescription"(
    "examination_id" INTEGER NOT NULL REFERENCES "examination"("examination_id"),
    "medicine_id" INTEGER NOT NULL REFERENCES "medicine"("medicine_id"),
    "number" INTEGER NULL,
    "cost" DOUBLE PRECISION NULL
);

-- Tạo constraints cho bảng medicine
ALTER TABLE medicine
ADD CONSTRAINT check_number_left CHECK(number_left >= 0);

ALTER TABLE medicine
ADD CONSTRAINT check_cost_per CHECK(cost_per >= 0);
--Tạo constraints cho bảng medicine_prescription

ALTER TABLE medicine_prescription
ADD CONSTRAINT check_numer CHECK(number >= 0);

ALTER TABLE medicine_prescription
ADD CONSTRAINT check_cost CHECK(cost >= 0);

-- Tạo constraints cho bảng examination
ALTER TABLE examination
ADD CONSTRAINT check_height CHECK(height > 0);

ALTER TABLE examination
ADD CONSTRAINT check_weight CHECK(weight > 0);

ALTER TABLE examination
ADD CONSTRAINT check_blood_pressure_S CHECK("blood_pressure_S" > 0);

ALTER TABLE examination
ADD CONSTRAINT check_blood_pressure_D CHECK("blood_pressure_D" > 0);

ALTER TABLE examination
ADD CONSTRAINT check_heart_rate CHECK(heart_rate > 0);

-- Tạo constraints cho bảng patient
ALTER TABLE patient
ADD CONSTRAINT check_blood_type CHECK(blood_type in ('A','B','AB','O'));

-- Tạo constraints cho bảng user
ALTER TABLE "user"
ADD CONSTRAINT check_sex CHECK(sex in ('Male', 'Female'));

ALTER TABLE "user"
ADD CONSTRAINT "check_user_role"
CHECK ("role" IN (1, 2));

-- Tạo constraint doctor
ALTER TABLE doctor
ADD CONSTRAINT check_salary CHECK(salary > 0);

-- Tạo constraint test
ALTER TABLE test
ADD CONSTRAINT check_fee CHECK(fee >= 0);


CREATE OR REPLACE FUNCTION update_age()
RETURNS TRIGGER AS $$
BEGIN
    NEW.age := DATE_PART('year', NEW.date) - DATE_PART('year', (SELECT dob FROM "user" WHERE "user_id" = NEW.user_id));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_age_trigger
BEFORE INSERT ON "examination"
FOR EACH ROW
EXECUTE FUNCTION update_age();

CREATE OR REPLACE FUNCTION update_examination_fee_from_medicine()
RETURNS TRIGGER AS $$
DECLARE
    total_medicine_fee NUMERIC;
BEGIN
    -- Tính tổng phí thuốc cho examination_id tương ứng
    SELECT
        SUM(mp.cost) AS total_medicine_fee 
    INTO total_medicine_fee
    FROM medicine_prescription mp
    WHERE mp.examination_id = COALESCE(NEW.examination_id, OLD.examination_id);

    -- Cập nhật phí của bảng examination
    UPDATE examination e
    SET fee = total_medicine_fee + COALESCE((SELECT SUM(t.fee) FROM test_join tj JOIN test t ON tj.test_id = t.test_id WHERE tj.examination_id = COALESCE(NEW.examination_id, OLD.examination_id)), 0)
    WHERE e.examination_id = COALESCE(NEW.examination_id, OLD.examination_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_examination_fee_from_test()
RETURNS TRIGGER AS $$
BEGIN
    -- Đảm bảo fee không phải là NULL
    IF TG_OP = 'INSERT' THEN
        -- Add the fee of the new test to the existing fee
        UPDATE examination
        SET fee = COALESCE(fee, 0) + (SELECT fee FROM test WHERE test_id = NEW.test_id)
        WHERE examination_id = NEW.examination_id;

    ELSIF TG_OP = 'DELETE' THEN
        -- Subtract the fee of the deleted test from the existing fee
        UPDATE examination
        SET fee = COALESCE(fee, 0) - (SELECT fee FROM test WHERE test_id = OLD.test_id)
        WHERE examination_id = OLD.examination_id;

    ELSIF TG_OP = 'UPDATE' THEN
        -- Adjust the fee by removing the old test fee and adding the new test fee
        UPDATE examination
        SET fee = COALESCE(fee, 0) - (SELECT fee FROM test WHERE test_id = OLD.test_id) 
                   + (SELECT fee FROM test WHERE test_id = NEW.test_id)
        WHERE examination_id = NEW.examination_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger cho bảng medicine_prescription
CREATE TRIGGER update_examination_fee_on_medicine_prescription
AFTER INSERT OR UPDATE OR DELETE ON medicine_prescription
FOR EACH ROW
EXECUTE FUNCTION update_examination_fee_from_medicine();

-- Trigger cho bảng test_join
CREATE TRIGGER test_join_after_change
AFTER INSERT OR UPDATE OR DELETE ON test_join
FOR EACH ROW
EXECUTE FUNCTION update_examination_fee_from_test();

CREATE OR REPLACE FUNCTION update_medicine_stock_and_cost()
RETURNS TRIGGER AS $$
DECLARE
    current_stock INT;
    change_in_stock INT;
BEGIN
    -- Tính toán sự thay đổi trong số lượng thuốc
    change_in_stock := COALESCE(NEW.number, 0) - COALESCE(OLD.number, 0);
    
    -- Lấy số lượng thuốc hiện tại từ bảng medicine
    SELECT COALESCE(number_left, 0) INTO current_stock
    FROM medicine
    WHERE medicine_id = NEW.medicine_id;

    -- Kiểm tra nếu số lượng thuốc trong kho đủ
    IF current_stock < change_in_stock THEN
        RAISE EXCEPTION 'Insufficient stock for medicine_id %', NEW.medicine_id;
    END IF;

    -- Cập nhật số lượng thuốc còn lại trong bảng medicine
    UPDATE medicine
    SET number_left = current_stock - change_in_stock
    WHERE medicine_id = NEW.medicine_id;

    -- Cập nhật cột cost trong bảng medicine_prescription
    NEW.cost := COALESCE(NEW.number, 0) * (SELECT COALESCE(cost_per, 0) FROM medicine WHERE medicine_id = NEW.medicine_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_medicine_stock_and_cost_trigger
BEFORE INSERT OR UPDATE ON medicine_prescription
FOR EACH ROW
EXECUTE FUNCTION update_medicine_stock_and_cost();

CREATE OR REPLACE FUNCTION insert_role_based_data() 
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.role = 1 THEN
        -- Thêm thông tin vào bảng patient nếu role là 1
        INSERT INTO patient (user_id) VALUES (NEW.user_id);
    ELSIF NEW.role = 2 THEN
        -- Thêm thông tin vào bảng personnel nếu role là 2
        INSERT INTO doctor (user_id) VALUES (NEW.user_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tạo trigger gọi hàm trên sau khi chèn dữ liệu vào bảng user
CREATE TRIGGER after_user_insert
AFTER INSERT ON "user"
FOR EACH ROW
EXECUTE FUNCTION insert_role_based_data();

CREATE OR REPLACE FUNCTION add_diagnose_test()
RETURNS TRIGGER AS $$
DECLARE
    diagnose_test_id INT;
BEGIN
    -- Lấy test_id của 'Diagnose'
    SELECT test_id INTO diagnose_test_id
    FROM test
    WHERE test_name = 'Diagnostic';

    -- Chèn một bản ghi mới vào test_join với test_id của 'Diagnose'
    INSERT INTO test_join (examination_id, test_id)
    VALUES (NEW.examination_id, diagnose_test_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_examination_insert
AFTER INSERT ON examination
FOR EACH ROW
EXECUTE FUNCTION add_diagnose_test();

CREATE OR REPLACE FUNCTION insert_user(user_id INT, password VARCHAR(255), name VARCHAR(255), dob DATE, sex VARCHAR(255), phone VARCHAR(255), address VARCHAR(255), role INT)
RETURNS VOID AS
$$
BEGIN
    INSERT INTO "user" ("user_id", "password", "name", "dob", "sex", "phone", "address", "role")
    VALUES (user_id, password, name, dob, sex, phone, address, role);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_new_symptom(new_symptom_id INTEGER, new_symptom_name VARCHAR(255), new_department_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Check if symptom with the same symptom_id already exists
    IF EXISTS (
        SELECT 1
        FROM symptom
        WHERE symptom_id = new_symptom_id
    ) THEN
        RAISE EXCEPTION 'Symptom with id % already exists', new_symptom_id;
    END IF;

    -- Check if symptom with the same symptom_name already exists
    IF EXISTS (
        SELECT 1
        FROM symptom
        WHERE symptom_name = new_symptom_name
    ) THEN
        RAISE EXCEPTION 'Symptom with name % already exists', new_symptom_name;
    END IF;

    -- If symptom does not exist, insert the new symptom
    INSERT INTO symptom (symptom_id, symptom_name, department_id)
    VALUES (new_symptom_id, new_symptom_name, new_department_id);
END;
$$ LANGUAGE plpgsql; 

CREATE OR REPLACE FUNCTION add_symptom_to_examination(
    add_examination_id INTEGER,
    add_symptom_id INTEGER
) RETURNS void AS $$
BEGIN
    -- Check if the symptom already exists for the given examination_id
    IF EXISTS (
        SELECT 1
        FROM symptom_join sj
        WHERE sj.examination_id = add_examination_id
          AND sj.symptom_id = add_symptom_id
    ) THEN
        RAISE EXCEPTION 'Symptom with id % already exists for examination id %', add_symptom_id, add_examination_id;
    ELSE
        -- Insert the symptom into the symptom_join table
        INSERT INTO symptom_join (examination_id, symptom_id)
        VALUES (add_examination_id, add_symptom_id);
    END IF;
END;
$$ LANGUAGE plpgsql; 

-- Tạo index trên cột user_id của bảng examination
CREATE INDEX idx_examination_user_id
ON examination (user_id);
-- Tạo index trên cột date của bảng examination
CREATE INDEX idx_examination_date
ON examination (date);
-- Tạo index trên cột age trên examination
CREATE INDEX idx_examination_age
ON examination (age);
-- Tạo chỉ mục trên cột examination_id của bảng symptom_join
CREATE INDEX idx_symptom_join_examination_id ON symptom_join(examination_id);
-- Tạo chỉ mục trên cột medicine_id của bảng medicine_prescription
CREATE INDEX idx_medicine_prescription_medicine_id
ON medicine_prescription (medicine_id);
-- Tạo chỉ mục trên cột examination_id của bảng medicine_prescription
CREATE INDEX idx_medicine_prescription_examination_id
ON medicine_prescription (examination_id);
-- Tạo chỉ mục trên cột examination_id của bảng test_join
CREATE INDEX idx_test_join_examination_id
ON test_join (examination_id);
