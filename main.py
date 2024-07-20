import tkinter as tk
from tkinter import messagebox
import psycopg2

def connect_db():
    return psycopg2.connect(
        host="localhost",           #Change the detail of database, host, user, password according to your system
        database="ProjectGrp9", 
        user="postgres",
        password="Ngochung@2004"
    )

root = tk.Tk()
root.title("Hospital Management System")

def add_user():
    def submit():
        user_id = entry_user_id.get()
        password = entry_password.get()
        name = entry_name.get()
        dob = entry_dob.get()
        sex = entry_sex.get()
        phone = entry_phone.get()
        address = entry_address.get()
        role = entry_role.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO "user" (user_id, password, name, dob, sex, phone, address, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (user_id, password, name, dob, sex, phone, address, role)
            )
            conn.commit()
            messagebox.showinfo("Success", "User added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()
    
    window = tk.Toplevel(root)
    window.title("Add User")

    tk.Label(window, text="User ID").grid(row=0)
    tk.Label(window, text="Password").grid(row=1)
    tk.Label(window, text="Name").grid(row=2)
    tk.Label(window, text="DOB").grid(row=3)
    tk.Label(window, text="Sex").grid(row=4)
    tk.Label(window, text="Phone").grid(row=5)
    tk.Label(window, text="Address").grid(row=6)
    tk.Label(window, text="Role").grid(row=7)

    entry_user_id = tk.Entry(window)
    entry_password = tk.Entry(window)
    entry_name = tk.Entry(window)
    entry_dob = tk.Entry(window)
    entry_sex = tk.Entry(window)
    entry_phone = tk.Entry(window)
    entry_address = tk.Entry(window)
    entry_role = tk.Entry(window)

    entry_user_id.grid(row=0, column=1)
    entry_password.grid(row=1, column=1)
    entry_name.grid(row=2, column=1)
    entry_dob.grid(row=3, column=1)
    entry_sex.grid(row=4, column=1)
    entry_phone.grid(row=5, column=1)
    entry_address.grid(row=6, column=1)
    entry_role.grid(row=7, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=8, column=1)

# Hàm tìm kiếm thông tin bệnh nhân
def search_patient():
    def search():
        user_id = entry_user_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT u.user_id, u.name, u.dob, u.sex, u.phone, u.address, p.blood_type
                FROM "user" u
                JOIN patient p ON u.user_id = p.user_id
                WHERE u.user_id = %s AND u.role = 1;
                """,
                (user_id,)
            )
            patient = cur.fetchone()
            if patient:
                result.set(f"User ID: {patient[0]}\nName: {patient[1]}\nDOB: {patient[2]}\nSex: {patient[3]}\nPhone: {patient[4]}\nAddress: {patient[5]}\nBlood Type: {patient[6]}")
            else:
                result.set(f"Không tồn tại bệnh nhân có user_id {user_id}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Search Patient")

    tk.Label(window, text="User ID").grid(row=0)
    entry_user_id = tk.Entry(window)
    entry_user_id.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)

def search_doctor():
    def search():
        user_id = entry_user_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT u.user_id, u.name, u.dob, u.sex, u.phone, u.address, d.department_id, d.salary
                FROM "user" u
                JOIN doctor d ON u.user_id = d.user_id
                WHERE u.user_id = %s AND u.role = 2;
                """,
                (user_id,)
            )
            doctor = cur.fetchone()
            if doctor:
                result.set(f"User ID: {doctor[0]}\nName: {doctor[1]}\nDOB: {doctor[2]}\nSex: {doctor[3]}\nPhone: {doctor[4]}\nAddress: {doctor[5]}\nDepartment ID: {doctor[6]}\nSalary: {doctor[7]}")
            else:
                result.set(f"Không tồn tại bác sĩ có user_id {user_id}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Search Doctor")

    tk.Label(window, text="User ID").grid(row=0)
    entry_user_id = tk.Entry(window)
    entry_user_id.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)

def check_doctor_schedule():
    def search():
        user_id = entry_user_id.get()
        date = entry_date.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT ex.examination_id, ex.time_arranged
                FROM examination ex
                WHERE ex.doctor_id = %s AND ex."date" = %s;
                """,
                (user_id, date)
            )
            schedule = cur.fetchall()
            if schedule:
                result.set("\n".join([f"Examination ID: {s[0]}, Time: {s[1]}" for s in schedule]))
            else:
                result.set(f"Không có lịch khám bệnh của bác sĩ có ID {user_id} trong ngày {date}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Doctor Schedule")

    tk.Label(window, text="Doctor ID").grid(row=0)
    entry_user_id = tk.Entry(window)
    entry_user_id.grid(row=0, column=1)
    tk.Label(window, text="Date (YYYY-MM-DD)").grid(row=1)
    entry_date = tk.Entry(window)
    entry_date.grid(row=1, column=1)

    tk.Button(window, text="Check Schedule", command=search).grid(row=2, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=3, columnspan=2)

def insert_examination():
    def submit():
        examination_id = entry_examination_id.get()
        user_id = entry_user_id.get()
        examination_date = entry_date.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO examination (examination_id, user_id, date)
                VALUES (%s, %s, %s);
                """,
                (examination_id, user_id, examination_date)
            )
            conn.commit()
            messagebox.showinfo("Success", "Examination added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Add Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    tk.Label(window, text="User ID").grid(row=1)
    tk.Label(window, text="Date (YYYY-MM-DD)").grid(row=2)

    entry_examination_id = tk.Entry(window)
    entry_user_id = tk.Entry(window)
    entry_date = tk.Entry(window)

    entry_examination_id.grid(row=0, column=1)
    entry_user_id.grid(row=1, column=1)
    entry_date.grid(row=2, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=3, column=1)

def update_examination():
    def submit():
        examination_id = entry_examination_id.get()
        doctor_id = entry_doctor_id.get()
        height = entry_height.get()
        weight = entry_weight.get()
        blood_pressure_s = entry_bp_s.get()
        blood_pressure_d = entry_bp_d.get()
        heart_rate = entry_heart_rate.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE examination
                SET doctor_id = %s,
                    height = %s,
                    weight = %s,
                    "blood_pressure_S" = %s,
                    "blood_pressure_D" = %s,
                    heart_rate = %s
                WHERE examination_id = %s;
                """,
                (doctor_id, height, weight, blood_pressure_s, blood_pressure_d, heart_rate, examination_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "Examination updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Update Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    tk.Label(window, text="Doctor ID").grid(row=1)
    tk.Label(window, text="Height").grid(row=2)
    tk.Label(window, text="Weight").grid(row=3)
    tk.Label(window, text="Blood Pressure S").grid(row=4)
    tk.Label(window, text="Blood Pressure D").grid(row=5)
    tk.Label(window, text="Heart Rate").grid(row=6)

    entry_examination_id = tk.Entry(window)
    entry_doctor_id = tk.Entry(window)
    entry_height = tk.Entry(window)
    entry_weight = tk.Entry(window)
    entry_bp_s = tk.Entry(window)
    entry_bp_d = tk.Entry(window)
    entry_heart_rate = tk.Entry(window)

    entry_examination_id.grid(row=0, column=1)
    entry_doctor_id.grid(row=1, column=1)
    entry_height.grid(row=2, column=1)
    entry_weight.grid(row=3, column=1)
    entry_bp_s.grid(row=4, column=1)
    entry_bp_d.grid(row=5, column=1)
    entry_heart_rate.grid(row=6, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=7, column=1)

def search_examination_history():
    def search():
        user_id = entry_user_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT e.user_id, e.examination_id, u.name, e.date, e.doctor_id, e.height, e.weight, e."blood_pressure_S", e."blood_pressure_D", e.heart_rate, e.fee, e.conclusion, e.time_arranged,e.age
                FROM "user" u
                JOIN examination e ON u.user_id = e.user_id
                WHERE u.user_id = %s
                ORDER BY e.date DESC;
                """,
                (user_id,)
            )
            history = cur.fetchall()
            if history:
                result.set("\n".join([f"User ID: {h[0]}, Examination ID: {h[1]}, Name: {h[2]}, Date: {h[3]}, Doctor ID: {h[4]}, Height: {h[5]}, Weight: {h[6]}, Blood Pressure S: {h[7]}, Blood Pressure D: {h[8]}, Heart Rate: {h[9]}, Fee: {h[10]}, Conclusion: {h[11]}, Time Arranged: {h[12]}, Age: {h[13]}" for h in history]))
            else:
                result.set(f"Không có lịch sử khám bệnh cho user_id {user_id}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Examination History")

    tk.Label(window, text="User ID").grid(row=0)
    entry_user_id = tk.Entry(window)
    entry_user_id.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)

def examination_count_by_month():
    def search():
        year = entry_year.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT 
                    CAST(EXTRACT(MONTH FROM ex.date) AS INT) AS check_month, 
                    COUNT(ex.examination_id) AS total_examination
                FROM 
                    examination ex
                WHERE 
                    EXTRACT(YEAR FROM ex.date) = %s
                GROUP BY 
                    check_month
                ORDER BY 
                    check_month;
                """,
                (year,)
            )
            stats = cur.fetchall()
            if stats:
                result.set("\n".join([f"Month: {s[0]}, Total Examinations: {s[1]}" for s in stats]))
            else:
                result.set(f"Không có dữ liệu cho năm {year}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Examination Count by Month")

    tk.Label(window, text="Year").grid(row=0)
    entry_year = tk.Entry(window)
    entry_year.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)

def add_symptom_to_examination():
    def submit():
        examination_id = entry_examination_id.get()
        symptom_id = entry_symptom_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT add_symptom_to_examination(%s, %s);
                """,
                (examination_id, symptom_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "Symptom added to examination successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Add Symptom to Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    tk.Label(window, text="Symptom ID").grid(row=1)

    entry_examination_id = tk.Entry(window)
    entry_symptom_id = tk.Entry(window)

    entry_examination_id.grid(row=0, column=1)
    entry_symptom_id.grid(row=1, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=2, column=1)

def add_new_symptom():
    def submit():
        symptom_id = entry_symptom_id.get()
        symptom_name = entry_symptom_name.get()
        department_id = entry_department_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT add_new_symptom(%s, %s, %s);
                """,
                (symptom_id, symptom_name, department_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "New symptom added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Add New Symptom")

    tk.Label(window, text="Symptom ID").grid(row=0)
    tk.Label(window, text="Symptom Name").grid(row=1)
    tk.Label(window, text="Department ID").grid(row=2)

    entry_symptom_id = tk.Entry(window)
    entry_symptom_name = tk.Entry(window)
    entry_department_id = tk.Entry(window)

    entry_symptom_id.grid(row=0, column=1)
    entry_symptom_name.grid(row=1, column=1)
    entry_department_id.grid(row=2, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=3, column=1)

def get_symptoms_of_examination():
    def search():
        examination_id = entry_examination_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT s.symptom_name
                FROM symptom_join sj
                JOIN symptom s ON sj.symptom_id = s.symptom_id
                WHERE sj.examination_id = %s;
                """,
                (examination_id,)
            )
            symptoms = cur.fetchall()
            if symptoms:
                result.set("\n".join([s[0] for s in symptoms]))
            else:
                result.set(f"Không có triệu chứng nào cho examination_id {examination_id}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Get Symptoms of Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    entry_examination_id = tk.Entry(window)
    entry_examination_id.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)

def add_test_to_examination():
    def submit():
        examination_id = entry_examination_id.get()
        test_id = entry_test_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO test_join (examination_id, test_id)
                VALUES (%s, %s);
                """,
                (examination_id, test_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "Test added to examination successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Add Test to Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    tk.Label(window, text="Test ID").grid(row=1)

    entry_examination_id = tk.Entry(window)
    entry_test_id = tk.Entry(window)

    entry_examination_id.grid(row=0, column=1)
    entry_test_id.grid(row=1, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=2, column=1)

def add_medicine_to_examination():
    def submit():
        examination_id = entry_examination_id.get()
        medicine_id = entry_medicine_id.get()
        number = entry_number.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO medicine_prescription (examination_id, medicine_id, "number")
                VALUES (%s, %s, %s);
                """,
                (examination_id, medicine_id, number)
            )
            conn.commit()
            messagebox.showinfo("Success", "Medicine added to examination successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Add Medicine to Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    tk.Label(window, text="Medicine ID").grid(row=1)
    tk.Label(window, text="Number").grid(row=2)

    entry_examination_id = tk.Entry(window)
    entry_medicine_id = tk.Entry(window)
    entry_number = tk.Entry(window)

    entry_examination_id.grid(row=0, column=1)
    entry_medicine_id.grid(row=1, column=1)
    entry_number.grid(row=2, column=1)

    tk.Button(window, text="Submit", command=submit).grid(row=3, column=1)

def get_medicines_of_examination():
    def search():
        examination_id = entry_examination_id.get()
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT
                    m.medicine_name,
                    mp.number
                FROM
                    medicine_prescription mp
                JOIN
                    medicine m ON mp.medicine_id = m.medicine_id
                WHERE
                    mp.examination_id = %s;
                """,
                (examination_id,)
            )
            medicines = cur.fetchall()
            if medicines:
                result.set("\n".join([f"Medicine: {m[0]}, Number: {m[1]}" for m in medicines]))
            else:
                result.set(f"Không có thuốc nào cho examination_id {examination_id}")
        except Exception as e:
            result.set(str(e))
        finally:
            cur.close()
            conn.close()

    window = tk.Toplevel(root)
    window.title("Get Medicines of Examination")

    tk.Label(window, text="Examination ID").grid(row=0)
    entry_examination_id = tk.Entry(window)
    entry_examination_id.grid(row=0, column=1)

    tk.Button(window, text="Search", command=search).grid(row=1, column=1)
    result = tk.StringVar()
    tk.Label(window, textvariable=result).grid(row=2, columnspan=2)


# Create the menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)


# User Menu
user_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="User", menu=user_menu)
user_menu.add_command(label="Add User", command=add_user)

# Patient Menu
patient_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Patient", menu=patient_menu)
patient_menu.add_command(label="Search Patient", command=search_patient)

# Doctor Menu
doctor_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Doctor", menu=doctor_menu)
doctor_menu.add_command(label="Search Doctor", command=search_doctor)
doctor_menu.add_command(label="Check Doctor Schedule", command=check_doctor_schedule)

# Examination Menu
examination_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Examination", menu=examination_menu)
examination_menu.add_command(label="Insert Examination", command=insert_examination)
examination_menu.add_command(label="Update Examination", command=update_examination)
examination_menu.add_command(label="Search Examination History", command=search_examination_history)
examination_menu.add_command(label="Examination Count by Month", command=examination_count_by_month)

# Symptom Menu
symptom_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Symptom", menu=symptom_menu)
symptom_menu.add_command(label="Add Symptom to Examination", command=add_symptom_to_examination)
symptom_menu.add_command(label="Add New Symptom", command=add_new_symptom)
symptom_menu.add_command(label="Get Symptoms of Examination", command=get_symptoms_of_examination)

# Test Menu
test_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Test", menu=test_menu)
test_menu.add_command(label="Add Test to Examination", command=add_test_to_examination)

# Medicine Menu
medicine_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Medicine", menu=medicine_menu)
medicine_menu.add_command(label="Add Medicine to Examination", command=add_medicine_to_examination)
medicine_menu.add_command(label="Get Medicines of Examination", command=get_medicines_of_examination)

# Start the main loop
root.mainloop()