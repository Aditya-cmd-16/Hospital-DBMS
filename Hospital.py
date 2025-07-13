import mysql.connector
from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime

# -----------------------------------------------------
# Database Connection
# -----------------------------------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Init@2503",  # Change if needed
        database="hospital1"
    )

# -----------------------------------------------------
# Doctor Class
# -----------------------------------------------------
class Doctor:
    def __init__(self):
        self.con = get_connection()
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Doctor(
            DoctorId INT PRIMARY KEY,
            DoctorName VARCHAR(50),
            DoctorAge SMALLINT,
            Department VARCHAR(50),
            UserName VARCHAR(50),
            Password VARCHAR(50)
        )
        """)
        self.con.commit()

    def signup(self, did, name, age, dept, uname, pwd):
        self.cur.execute("INSERT INTO Doctor VALUES (%s,%s,%s,%s,%s,%s)",
                         (did, name, age, dept, uname, pwd))
        self.con.commit()

    def login(self, uname, pwd):
        self.cur.execute("SELECT * FROM Doctor WHERE UserName=%s AND Password=%s", (uname, pwd))
        return self.cur.fetchone()

    def add_speciality(self, did, sp):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Speciality(
            DoctorId INT PRIMARY KEY,
            Speciality VARCHAR(50),
            FOREIGN KEY (DoctorId) REFERENCES Doctor(DoctorId)
        )
        """)
        self.cur.execute("INSERT INTO Speciality VALUES (%s,%s)", (did, sp))
        self.con.commit()

    def confirm_appointment(self, aid, status):
        self.cur.execute("UPDATE Appointments SET status=%s WHERE id=%s", (status, aid))
        self.con.commit()

    def add_prescription(self, aid, text):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Prescriptions(
            prescription_id INT AUTO_INCREMENT PRIMARY KEY,
            appointment_id INT,
            prescription_text VARCHAR(500),
            FOREIGN KEY (appointment_id) REFERENCES Appointments(id)
        )
        """)
        self.cur.execute("INSERT INTO Prescriptions(appointment_id, prescription_text) VALUES (%s,%s)", (aid, text))
        self.con.commit()

    def add_medical_record(self, pid, desc, rec_date):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS MedicalRecords(
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            description VARCHAR(500),
            record_date DATE,
            FOREIGN KEY (patient_id) REFERENCES Patient(PatientId)
        )
        """)
        self.cur.execute("INSERT INTO MedicalRecords(patient_id, description, record_date) VALUES (%s,%s,%s)", (pid, desc, rec_date))
        self.con.commit()

    def generate_bill(self, aid, amt):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Bills(
            Appointment_ID INT PRIMARY KEY,
            Amount INT,
            status ENUM('Unpaid','Paid') DEFAULT 'Unpaid'
        )
        """)
        self.cur.execute("INSERT INTO Bills(Appointment_ID, Amount) VALUES (%s,%s)", (aid, amt))
        self.con.commit()

    def mark_bill_paid(self, aid):
        self.cur.execute("UPDATE Bills SET status='Paid' WHERE Appointment_ID=%s", (aid,))
        self.con.commit()

    def view_unpaid_bills(self):
        self.cur.execute("SELECT * FROM Bills WHERE status='Unpaid'")
        return self.cur.fetchall()

    def update_patient_details(self, pid, field, value):
        self.cur.execute(f"UPDATE Patient SET {field}=%s WHERE PatientId=%s", (value, pid))
        self.con.commit()

    def get_all_appointments(self):
        self.cur.execute("SELECT * FROM Appointments")
        return self.cur.fetchall()

# -----------------------------------------------------
# Patient Class
# -----------------------------------------------------
class Patient:
    def __init__(self):
        self.con = get_connection()
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Patient(
            PatientId INT PRIMARY KEY,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            Age INT,
            UserName VARCHAR(50),
            Password VARCHAR(50),
            Registration_Date DATE
        )
        """)
        self.con.commit()

    def signup(self, pid, fname, lname, age, uname, pwd, reg_date):
        self.cur.execute("INSERT INTO Patient VALUES (%s,%s,%s,%s,%s,%s,%s)",
                         (pid, fname, lname, age, uname, pwd, reg_date))
        self.con.commit()

    def login(self, uname, pwd):
        self.cur.execute("SELECT * FROM Patient WHERE UserName=%s AND Password=%s", (uname, pwd))
        return self.cur.fetchone()

    def schedule_appointment(self, pid, adate):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Appointments(
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            appointment_date DATE,
            status ENUM('Pending','Confirmed','Completed','Cancelled') DEFAULT 'Pending',
            FOREIGN KEY (patient_id) REFERENCES Patient(PatientId)
        )
        """)
        self.cur.execute("INSERT INTO Appointments(patient_id, appointment_date) VALUES (%s,%s)", (pid, adate))
        self.con.commit()
        return self.cur.lastrowid

    def view_appointments(self, pid):
        self.cur.execute("SELECT * FROM Appointments WHERE patient_id=%s", (pid,))
        return self.cur.fetchall()

    def view_prescriptions(self, pid):
        self.cur.execute("""
            SELECT p.prescription_id, a.id, p.prescription_text
            FROM Prescriptions p
            JOIN Appointments a ON p.appointment_id = a.id
            WHERE a.patient_id=%s
        """, (pid,))
        return self.cur.fetchall()

    def view_medical_records(self, pid):
        self.cur.execute("SELECT * FROM MedicalRecords WHERE patient_id=%s", (pid,))
        return self.cur.fetchall()

    def search_doctors_by_speciality(self, sp):
        self.cur.execute("""
            SELECT d.DoctorId, d.DoctorName, d.Department
            FROM Doctor d
            JOIN Speciality s ON d.DoctorId = s.DoctorId
            WHERE s.Speciality=%s
        """, (sp,))
        return self.cur.fetchall()

    def get_patient_details(self, pid):
        self.cur.execute("SELECT * FROM Patient WHERE PatientId=%s", (pid,))
        return self.cur.fetchone()

# -----------------------------------------------------
# GUI Application
# -----------------------------------------------------
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("800x600")
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        
        self.current_user = None
        self.user_type = None
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        self.show_main_menu()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_main_menu(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Hospital Management System", style='Header.TLabel').pack(pady=20)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Doctor Login", command=self.show_doctor_login).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="Doctor Signup", command=self.show_doctor_signup).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(button_frame, text="Patient Login", command=self.show_patient_login).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="Patient Signup", command=self.show_patient_signup).grid(row=1, column=1, padx=10, pady=10)
    
    # Doctor Authentication
    def show_doctor_login(self):
        self.clear_frame()
        self.doctor = Doctor()
        
        ttk.Label(self.main_frame, text="Doctor Login", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.doctor_uname = ttk.Entry(form_frame)
        self.doctor_uname.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.doctor_pwd = ttk.Entry(form_frame, show="*")
        self.doctor_pwd.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.doctor_login).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_main_menu).pack(side=LEFT, padx=5)
    
    def show_doctor_signup(self):
        self.clear_frame()
        self.doctor = Doctor()
        
        ttk.Label(self.main_frame, text="Doctor Signup", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        fields = ["Doctor ID:", "Name:", "Age:", "Department:", "Username:", "Password:"]
        self.doctor_signup_entries = []
        
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky=W)
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.doctor_signup_entries.append(entry)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Signup", command=self.doctor_signup).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_main_menu).pack(side=LEFT, padx=5)
    
    def doctor_login(self):
        uname = self.doctor_uname.get()
        pwd = self.doctor_pwd.get()
        
        if not uname or not pwd:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        doctor = self.doctor.login(uname, pwd)
        if doctor:
            self.current_user = doctor
            self.user_type = "doctor"
            self.show_doctor_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def doctor_signup(self):
        try:
            did = int(self.doctor_signup_entries[0].get())
            name = self.doctor_signup_entries[1].get()
            age = int(self.doctor_signup_entries[2].get())
            dept = self.doctor_signup_entries[3].get()
            uname = self.doctor_signup_entries[4].get()
            pwd = self.doctor_signup_entries[5].get()
            
            if not all([did, name, age, dept, uname, pwd]):
                messagebox.showerror("Error", "All fields are required")
                return
                
            self.doctor.signup(did, name, age, dept, uname, pwd)
            messagebox.showinfo("Success", "Doctor registration successful")
            self.show_main_menu()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid data")
    
    # Patient Authentication
    def show_patient_login(self):
        self.clear_frame()
        self.patient = Patient()
        
        ttk.Label(self.main_frame, text="Patient Login", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.patient_uname = ttk.Entry(form_frame)
        self.patient_uname.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.patient_pwd = ttk.Entry(form_frame, show="*")
        self.patient_pwd.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.patient_login).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_main_menu).pack(side=LEFT, padx=5)
    
    def show_patient_signup(self):
        self.clear_frame()
        self.patient = Patient()
        
        ttk.Label(self.main_frame, text="Patient Signup", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        fields = ["Patient ID:", "First Name:", "Last Name:", "Age:", "Username:", "Password:", "Registration Date (YYYY-MM-DD):"]
        self.patient_signup_entries = []
        
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky=W)
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.patient_signup_entries.append(entry)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Signup", command=self.patient_signup).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_main_menu).pack(side=LEFT, padx=5)
    
    def patient_login(self):
        uname = self.patient_uname.get()
        pwd = self.patient_pwd.get()
        
        if not uname or not pwd:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        patient = self.patient.login(uname, pwd)
        if patient:
            self.current_user = patient
            self.user_type = "patient"
            self.show_patient_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def patient_signup(self):
        try:
            pid = int(self.patient_signup_entries[0].get())
            fname = self.patient_signup_entries[1].get()
            lname = self.patient_signup_entries[2].get()
            age = int(self.patient_signup_entries[3].get())
            uname = self.patient_signup_entries[4].get()
            pwd = self.patient_signup_entries[5].get()
            reg_date = self.patient_signup_entries[6].get()
            
            if not all([pid, fname, lname, age, uname, pwd, reg_date]):
                messagebox.showerror("Error", "All fields are required")
                return
                
            self.patient.signup(pid, fname, lname, age, uname, pwd, reg_date)
            messagebox.showinfo("Success", "Patient registration successful")
            self.show_main_menu()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid data")
    
    # Doctor Dashboard
    def show_doctor_dashboard(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text=f"Welcome Dr. {self.current_user[1]}", style='Header.TLabel').pack(pady=10)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        buttons = [
            ("Add Speciality", self.show_add_speciality),
            ("Manage Appointments", self.show_manage_appointments),
            ("Add Prescription", self.show_add_prescription),
            ("Add Medical Record", self.show_add_medical_record),
            ("Manage Bills", self.show_manage_bills),
            ("Update Patient Details", self.show_update_patient),
            ("Logout", self.show_main_menu)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def show_add_speciality(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Add Speciality", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Doctor ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.speciality_did = ttk.Entry(form_frame)
        self.speciality_did.insert(0, str(self.current_user[0]))
        self.speciality_did.config(state='readonly')
        self.speciality_did.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Speciality:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.speciality_name = ttk.Entry(form_frame)
        self.speciality_name.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_speciality).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def add_speciality(self):
        did = self.speciality_did.get()
        sp = self.speciality_name.get()
        
        if not sp:
            messagebox.showerror("Error", "Please enter a speciality")
            return
            
        try:
            self.doctor.add_speciality(int(did), sp)
            messagebox.showinfo("Success", "Speciality added successfully")
            self.show_doctor_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add speciality: {str(e)}")
    
    def show_manage_appointments(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Manage Appointments", style='Header.TLabel').pack(pady=10)
        
        # Treeview to display appointments
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("ID", "Patient ID", "Date", "Status")
        self.appointments_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=100, anchor=CENTER)
        
        self.appointments_tree.pack(fill=BOTH, expand=True)
        
        # Load appointments
        appointments = self.doctor.get_all_appointments()
        for appt in appointments:
            self.appointments_tree.insert("", END, values=appt)
        
        # Action frame
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(pady=10)
        
        ttk.Label(action_frame, text="Appointment ID:").pack(side=LEFT, padx=5)
        self.appt_id = ttk.Entry(action_frame, width=10)
        self.appt_id.pack(side=LEFT, padx=5)
        
        ttk.Label(action_frame, text="Status:").pack(side=LEFT, padx=5)
        self.appt_status = ttk.Combobox(action_frame, values=["Confirmed", "Cancelled", "Completed"], width=15)
        self.appt_status.pack(side=LEFT, padx=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Update Status", command=self.update_appointment_status).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def update_appointment_status(self):
        aid = self.appt_id.get()
        status = self.appt_status.get()
        
        if not aid or not status:
            messagebox.showerror("Error", "Please select an appointment and status")
            return
            
        try:
            self.doctor.confirm_appointment(int(aid), status)
            messagebox.showinfo("Success", "Appointment status updated")
            self.show_manage_appointments()  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update appointment: {str(e)}")
    
    def show_add_prescription(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Add Prescription", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Appointment ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.prescription_aid = ttk.Entry(form_frame)
        self.prescription_aid.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Prescription:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.prescription_text = Text(form_frame, width=40, height=10)
        self.prescription_text.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_prescription).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def add_prescription(self):
        aid = self.prescription_aid.get()
        text = self.prescription_text.get("1.0", END).strip()
        
        if not aid or not text:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            self.doctor.add_prescription(int(aid), text)
            messagebox.showinfo("Success", "Prescription added successfully")
            self.show_doctor_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add prescription: {str(e)}")
    
    def show_add_medical_record(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Add Medical Record", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.record_pid = ttk.Entry(form_frame)
        self.record_pid.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.record_desc = Text(form_frame, width=40, height=10)
        self.record_desc.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.record_date = ttk.Entry(form_frame)
        self.record_date.grid(row=2, column=1, padx=5, pady=5)
        self.record_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_medical_record).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def add_medical_record(self):
        pid = self.record_pid.get()
        desc = self.record_desc.get("1.0", END).strip()
        rec_date = self.record_date.get()
        
        if not pid or not desc or not rec_date:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            self.doctor.add_medical_record(int(pid), desc, rec_date)
            messagebox.showinfo("Success", "Medical record added successfully")
            self.show_doctor_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medical record: {str(e)}")
    
    def show_manage_bills(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Manage Bills", style='Header.TLabel').pack(pady=10)
        
        # Treeview to display bills
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("Appointment ID", "Amount", "Status")
        self.bills_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.bills_tree.heading(col, text=col)
            self.bills_tree.column(col, width=100, anchor=CENTER)
        
        self.bills_tree.pack(fill=BOTH, expand=True)
        
        # Load bills
        bills = self.doctor.view_unpaid_bills()
        for bill in bills:
            self.bills_tree.insert("", END, values=bill)
        
        # Action frame
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(pady=10)
        
        ttk.Label(action_frame, text="Appointment ID:").pack(side=LEFT, padx=5)
        self.bill_aid = ttk.Entry(action_frame, width=10)
        self.bill_aid.pack(side=LEFT, padx=5)
        
        ttk.Label(action_frame, text="Amount:").pack(side=LEFT, padx=5)
        self.bill_amount = ttk.Entry(action_frame, width=10)
        self.bill_amount.pack(side=LEFT, padx=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Generate Bill", command=self.generate_bill).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Mark as Paid", command=self.mark_bill_paid).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def generate_bill(self):
        aid = self.bill_aid.get()
        amt = self.bill_amount.get()
        
        if not aid or not amt:
            messagebox.showerror("Error", "Please enter both appointment ID and amount")
            return
            
        try:
            self.doctor.generate_bill(int(aid), int(amt))
            messagebox.showinfo("Success", "Bill generated successfully")
            self.show_manage_bills()  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
    
    def mark_bill_paid(self):
        aid = self.bill_aid.get()
        
        if not aid:
            messagebox.showerror("Error", "Please enter appointment ID")
            return
            
        try:
            self.doctor.mark_bill_paid(int(aid))
            messagebox.showinfo("Success", "Bill marked as paid")
            self.show_manage_bills()  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update bill: {str(e)}")
    
    def show_update_patient(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Update Patient Details", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.update_pid = ttk.Entry(form_frame)
        self.update_pid.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Field to Update:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.update_field = ttk.Combobox(form_frame, values=["FirstName", "LastName", "Age"])
        self.update_field.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="New Value:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.update_value = ttk.Entry(form_frame)
        self.update_value.grid(row=2, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Update", command=self.update_patient).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="View Patient", command=self.view_patient_details).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_doctor_dashboard).pack(side=LEFT, padx=5)
    
    def update_patient(self):
        pid = self.update_pid.get()
        field = self.update_field.get()
        value = self.update_value.get()
        
        if not pid or not field or not value:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            self.doctor.update_patient_details(int(pid), field, value)
            messagebox.showinfo("Success", "Patient details updated successfully")
            self.show_update_patient()  # Refresh the form
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update patient: {str(e)}")
    
    def view_patient_details(self):
        pid = self.update_pid.get()
        
        if not pid:
            messagebox.showerror("Error", "Please enter patient ID")
            return
            
        try:
            patient = self.patient.get_patient_details(int(pid))
            if patient:
                details = f"ID: {patient[0]}\nName: {patient[1]} {patient[2]}\nAge: {patient[3]}\nUsername: {patient[4]}\nReg Date: {patient[6]}"
                messagebox.showinfo("Patient Details", details)
            else:
                messagebox.showerror("Error", "Patient not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch patient details: {str(e)}")
    
    # Patient Dashboard
    def show_patient_dashboard(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text=f"Welcome {self.current_user[1]} {self.current_user[2]}", style='Header.TLabel').pack(pady=10)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        buttons = [
            ("Schedule Appointment", self.show_schedule_appointment),
            ("View Appointments", self.show_view_appointments),
            ("View Prescriptions", self.show_view_prescriptions),
            ("View Medical Records", self.show_view_medical_records),
            ("Search Doctors", self.show_search_doctors),
            ("Logout", self.show_main_menu)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def show_schedule_appointment(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Schedule Appointment", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.appt_pid = ttk.Entry(form_frame)
        self.appt_pid.insert(0, str(self.current_user[0]))
        self.appt_pid.config(state='readonly')
        self.appt_pid.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.appt_date = ttk.Entry(form_frame)
        self.appt_date.grid(row=1, column=1, padx=5, pady=5)
        self.appt_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Schedule", command=self.schedule_appointment).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.show_patient_dashboard).pack(side=LEFT, padx=5)
    
    def schedule_appointment(self):
        pid = self.appt_pid.get()
        adate = self.appt_date.get()
        
        if not pid or not adate:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            appt_id = self.patient.schedule_appointment(int(pid), adate)
            messagebox.showinfo("Success", f"Appointment scheduled successfully. Your appointment ID is {appt_id}")
            self.show_patient_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule appointment: {str(e)}")
    
    def show_view_appointments(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Your Appointments", style='Header.TLabel').pack(pady=10)
        
        # Treeview to display appointments
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("ID", "Date", "Status")
        self.patient_appointments_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.patient_appointments_tree.heading(col, text=col)
            self.patient_appointments_tree.column(col, width=100, anchor=CENTER)
        
        self.patient_appointments_tree.pack(fill=BOTH, expand=True)
        
        # Load appointments
        appointments = self.patient.view_appointments(self.current_user[0])
        for appt in appointments:
            self.patient_appointments_tree.insert("", END, values=(appt[0], appt[2], appt[3]))
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Back", command=self.show_patient_dashboard).pack(side=LEFT, padx=5)
    
    def show_view_prescriptions(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Your Prescriptions", style='Header.TLabel').pack(pady=10)
        
        # Treeview to display prescriptions
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("Prescription ID", "Appointment ID", "Text")
        self.prescriptions_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.prescriptions_tree.heading(col, text=col)
            self.prescriptions_tree.column(col, width=100, anchor=CENTER)
        
        self.prescriptions_tree.column("Text", width=300)
        self.prescriptions_tree.pack(fill=BOTH, expand=True)
        
        # Load prescriptions
        prescriptions = self.patient.view_prescriptions(self.current_user[0])
        for pres in prescriptions:
            self.prescriptions_tree.insert("", END, values=pres)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Back", command=self.show_patient_dashboard).pack(side=LEFT, padx=5)
    
    def show_view_medical_records(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Your Medical Records", style='Header.TLabel').pack(pady=10)
        
        # Treeview to display records
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("Record ID", "Description", "Date")
        self.records_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=100, anchor=CENTER)
        
        self.records_tree.column("Description", width=300)
        self.records_tree.pack(fill=BOTH, expand=True)
        
        # Load records
        records = self.patient.view_medical_records(self.current_user[0])
        for rec in records:
            self.records_tree.insert("", END, values=(rec[0], rec[2], rec[3]))
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Back", command=self.show_patient_dashboard).pack(side=LEFT, padx=5)
    
    def show_search_doctors(self):
        self.clear_frame()
        
        ttk.Label(self.main_frame, text="Search Doctors by Speciality", style='Header.TLabel').pack(pady=10)
        
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(pady=10)
        
        ttk.Label(search_frame, text="Speciality:").pack(side=LEFT, padx=5)
        self.search_speciality = ttk.Entry(search_frame)
        self.search_speciality.pack(side=LEFT, padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_doctors).pack(side=LEFT, padx=5)
        
        # Treeview to display doctors
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(pady=10, fill=BOTH, expand=True)
        
        columns = ("Doctor ID", "Name", "Department")
        self.doctors_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.doctors_tree.heading(col, text=col)
            self.doctors_tree.column(col, width=100, anchor=CENTER)
        
        self.doctors_tree.pack(fill=BOTH, expand=True)
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Back", command=self.show_patient_dashboard).pack(side=LEFT, padx=5)
    
    def search_doctors(self):
        sp = self.search_speciality.get()
        
        if not sp:
            messagebox.showerror("Error", "Please enter a speciality")
            return
            
        try:
            doctors = self.patient.search_doctors_by_speciality(sp)
            self.doctors_tree.delete(*self.doctors_tree.get_children())
            for doc in doctors:
                self.doctors_tree.insert("", END, values=doc)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search doctors: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = HospitalApp(root)
    root.mainloop()
