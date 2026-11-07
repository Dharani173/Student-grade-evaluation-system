"""
Run: python student_grade_system.py

This is a simple Student Grade Evaluation System prototype using Tkinter.
It allows entering student details, adding multiple subjects, and generating/printing a marksheet.
"""
import tkinter as tk
from tkinter import messagebox, ttk
import os

class GradeSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Evaluation System")
        self.root.geometry("800x700")
        self.root.configure(bg="#ffffff")
        
        self.subjects = []
        
        # Styles for basic table and buttons
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TLabel", background="#ffffff", foreground="#333333", font=("Arial", 10))
        style.configure("TFrame", background="#ffffff")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#0055aa", pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Student Grade Evaluation System", font=("Arial", 16, "bold"), bg="#0055aa", fg="#ffffff").pack()
        tk.Label(header_frame, text="Enter student and subject details to generate the academic result.", font=("Arial", 10), bg="#0055aa", fg="#ffffff").pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Student Details Section
        student_frame = tk.LabelFrame(main_frame, text="Student Details", bg="#ffffff", font=("Arial", 10, "bold"), padx=10, pady=10)
        student_frame.pack(fill=tk.X, pady=(0, 10))
        
        labels = ["Student Name:", "Roll Number:", "Department:", "Semester:", "Section:"]
        self.entries = {}
        for i, lbl in enumerate(labels):
            tk.Label(student_frame, text=lbl, bg="#ffffff").grid(row=i//3, column=(i%3)*2, sticky=tk.W, pady=5, padx=5)
            ent = tk.Entry(student_frame, width=20, bg="#f9f9f9", bd=1, relief="solid")
            ent.grid(row=i//3, column=(i%3)*2 + 1, pady=5, padx=5)
            self.entries[lbl.replace(":", "")] = ent
            
        # Subject Details Section
        subject_frame = tk.LabelFrame(main_frame, text="Subject Details", bg="#ffffff", font=("Arial", 10, "bold"), padx=10, pady=10)
        subject_frame.pack(fill=tk.X, pady=(0, 10))
        
        sub_labels = ["Subject Name:", "Subject Code:", "Marks Obtained:", "Maximum Marks:"]
        self.sub_entries = {}
        for i, lbl in enumerate(sub_labels):
            tk.Label(subject_frame, text=lbl, bg="#ffffff").grid(row=0, column=i*2, sticky=tk.W, pady=5, padx=5)
            ent = tk.Entry(subject_frame, width=15, bg="#f9f9f9", bd=1, relief="solid")
            ent.grid(row=0, column=i*2 + 1, pady=5, padx=5)
            self.sub_entries[lbl.replace(":", "")] = ent
            
        add_btn = tk.Button(subject_frame, text="Add Subject", command=self.add_subject, bg="#0055aa", fg="#ffffff", relief="flat", padx=10)
        add_btn.grid(row=1, column=0, columnspan=8, pady=10)
        
        # Added Subjects Table
        self.tree = ttk.Treeview(main_frame, columns=("SubName", "SubCode", "Marks", "MaxMarks"), show="headings", height=5)
        self.tree.heading("SubName", text="Subject Name")
        self.tree.heading("SubCode", text="Subject Code")
        self.tree.heading("Marks", text="Marks Obtained")
        self.tree.heading("MaxMarks", text="Maximum Marks")
        self.tree.pack(fill=tk.X, pady=(0, 10))
        
        # Bottom Buttons
        btn_frame = tk.Frame(main_frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Generate Result", command=self.display_result, bg="#008800", fg="#ffffff", font=("Arial", 11, "bold"), relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Reset", command=self.reset, bg="#880000", fg="#ffffff", font=("Arial", 11, "bold"), relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Print Result", command=self.print_result, bg="#555555", fg="#ffffff", font=("Arial", 11, "bold"), relief="flat", padx=15, pady=5).pack(side=tk.RIGHT, padx=10)
        
        self.result_data = None
        self.student_data = None

    def validate_marks(self, marks_str, max_str):
        """Validates numeric values and conditions for marks"""
        try:
            marks = float(marks_str)
            max_marks = float(max_str)
            if max_marks <= 0:
                return False, "Maximum marks must be greater than 0."
            if marks < 0 or marks > max_marks:
                return False, "Marks obtained must be between 0 and maximum marks."
            return True, (marks, max_marks)
        except ValueError:
            return False, "Marks must be numeric values."

    def calculate_grade(self, marks, max_marks):
        """Calculates grade and pass/fail status based on exact percentage rules"""
        percentage = (marks / max_marks) * 100
        if percentage >= 90:
            return "A+", "Pass"
        elif percentage >= 80:
            return "A", "Pass"
        elif percentage >= 70:
            return "B", "Pass"
        elif percentage >= 60:
            return "C", "Pass"
        elif percentage >= 50:
            return "D", "Pass"
        else:
            return "F", "Fail"

    def calculate_percentage(self, obtained, total):
        """Calculates and formats percentage to two decimal places"""
        if total == 0:
            return 0.0
        return round((obtained / total) * 100, 2)

    def evaluate_result(self, subjects):
        """Evaluates overall totals, percentage, passes, fails, and overall result"""
        total_obtained = 0
        total_max = 0
        passed_subjects = 0
        failed_subjects = 0
        
        for sub in subjects:
            total_obtained += sub["marks"]
            total_max += sub["max_marks"]
            if sub["grade"] == "F" or sub["result"] == "Fail":
                failed_subjects += 1
            else:
                passed_subjects += 1
                
        percentage = self.calculate_percentage(total_obtained, total_max)
        overall_result = "FAIL" if failed_subjects > 0 else "PASS"
        
        return {
            "total_obtained": total_obtained,
            "total_max": total_max,
            "percentage": percentage,
            "passed_subjects": passed_subjects,
            "failed_subjects": failed_subjects,
            "overall_result": overall_result
        }

    def add_subject(self):
        """Gets input from UI and adds to subject list"""
        name = self.sub_entries["Subject Name"].get().strip()
        code = self.sub_entries["Subject Code"].get().strip()
        marks_str = self.sub_entries["Marks Obtained"].get().strip()
        max_str = self.sub_entries["Maximum Marks"].get().strip()
        
        if not all([name, code, marks_str, max_str]):
            messagebox.showerror("Input Error", "Please fill all subject details.")
            return
            
        valid, result = self.validate_marks(marks_str, max_str)
        if not valid:
            messagebox.showerror("Validation Error", result)
            return
            
        marks, max_marks = result
        grade, res = self.calculate_grade(marks, max_marks)
        
        sub_data = {
            "name": name,
            "code": code,
            "marks": marks,
            "max_marks": max_marks,
            "grade": grade,
            "result": res
        }
        self.subjects.append(sub_data)
        
        # Format for display
        disp_marks = int(marks) if marks.is_integer() else marks
        disp_max = int(max_marks) if max_marks.is_integer() else max_marks
        self.tree.insert("", tk.END, values=(name, code, disp_marks, disp_max))
        
        # Clear specific entry fields
        self.sub_entries["Subject Name"].delete(0, tk.END)
        self.sub_entries["Subject Code"].delete(0, tk.END)
        self.sub_entries["Marks Obtained"].delete(0, tk.END)
        self.sub_entries["Maximum Marks"].delete(0, tk.END)

    def display_result(self):
        """Validates student details, evaluates overall data, and generates the marksheet window"""
        self.student_data = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(self.student_data.values()):
            messagebox.showerror("Input Error", "Please fill all student details.")
            return
            
        if not self.subjects:
            messagebox.showerror("Data Error", "Please add at least one subject.")
            return
            
        self.result_data = self.evaluate_result(self.subjects)
        
        # Create Result Window
        res_win = tk.Toplevel(self.root)
        res_win.title("Marksheet")
        res_win.geometry("700x600")
        res_win.configure(bg="#ffffff")
        
        # Marksheet Header
        tk.Label(res_win, text="STUDENT MARKSHEET", font=("Arial", 16, "bold"), bg="#ffffff", fg="#0055aa").pack(pady=10)
        
        info_frame = tk.Frame(res_win, bg="#ffffff")
        info_frame.pack(fill=tk.X, padx=20)
        
        row_idx = 0
        for k, v in self.student_data.items():
            tk.Label(info_frame, text=f"{k}:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=row_idx//2, column=(row_idx%2)*2, sticky=tk.W, pady=2, padx=5)
            tk.Label(info_frame, text=v, bg="#ffffff").grid(row=row_idx//2, column=(row_idx%2)*2+1, sticky=tk.W, pady=2, padx=5)
            row_idx += 1
            
        # Result Table
        table_frame = tk.Frame(res_win, bg="#ffffff", pady=20)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        columns = ("Subject", "Subject Code", "Marks", "Grade", "Result")
        res_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        for col in columns:
            res_tree.heading(col, text=col)
            res_tree.column(col, width=120, anchor=tk.CENTER)
        res_tree.pack(fill=tk.X)
        
        for sub in self.subjects:
            disp_marks = int(sub["marks"]) if sub["marks"].is_integer() else sub["marks"]
            res_tree.insert("", tk.END, values=(
                sub["name"], 
                sub["code"], 
                disp_marks, 
                sub["grade"], 
                sub["result"]
            ))
            
        # Summary Box
        summary_frame = tk.Frame(res_win, bg="#f0f8ff", bd=1, relief="solid", padx=20, pady=10)
        summary_frame.pack(fill=tk.X, padx=20, pady=20)
        
        disp_obt = int(self.result_data['total_obtained']) if self.result_data['total_obtained'].is_integer() else self.result_data['total_obtained']
        disp_max = int(self.result_data['total_max']) if self.result_data['total_max'].is_integer() else self.result_data['total_max']
        
        summary_text = (
            f"Total Marks: {disp_obt} / {disp_max}\n"
            f"Percentage: {self.result_data['percentage']:.2f}%\n"
            f"Passed Subjects: {self.result_data['passed_subjects']}\n"
            f"Failed Subjects: {self.result_data['failed_subjects']}\n"
        )
        tk.Label(summary_frame, text=summary_text, font=("Arial", 11), bg="#f0f8ff", justify=tk.LEFT).pack(side=tk.LEFT)
        
        res_color = "green" if self.result_data['overall_result'] == "PASS" else "red"
        tk.Label(summary_frame, text=f"Overall Result: {self.result_data['overall_result']}", font=("Arial", 14, "bold"), bg="#f0f8ff", fg=res_color).pack(side=tk.RIGHT)

    def reset(self):
        """Clears all UI entries and resets the underlying data structures"""
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        for ent in self.sub_entries.values():
            ent.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.subjects.clear()
        self.result_data = None
        self.student_data = None
        messagebox.showinfo("Reset", "All fields have been cleared.")

    def print_result(self):
        """Exports the finalized result to a text file fallback since direct printing involves external tools"""
        if not self.result_data or not self.student_data:
            messagebox.showwarning("Print Error", "Please generate the result first.")
            return
            
        filename = "marksheet.txt"
        try:
            with open(filename, "w") as f:
                f.write("="*50 + "\n")
                f.write(" " * 15 + "STUDENT MARKSHEET\n")
                f.write("="*50 + "\n")
                for k, v in self.student_data.items():
                    f.write(f"{k}: {v}\n")
                f.write("-" * 50 + "\n")
                f.write(f"{'Subject':<20} | {'Code':<8} | {'Marks':<6} | {'Grade':<5} | {'Result':<5}\n")
                f.write("-" * 50 + "\n")
                for sub in self.subjects:
                    disp_marks = int(sub["marks"]) if sub["marks"].is_integer() else sub["marks"]
                    f.write(f"{sub['name'][:19]:<20} | {sub['code'][:7]:<8} | {disp_marks:<6} | {sub['grade']:<5} | {sub['result']:<5}\n")
                f.write("-" * 50 + "\n")
                
                disp_obt = int(self.result_data['total_obtained']) if self.result_data['total_obtained'].is_integer() else self.result_data['total_obtained']
                disp_max = int(self.result_data['total_max']) if self.result_data['total_max'].is_integer() else self.result_data['total_max']
                
                f.write(f"Total Marks: {disp_obt} / {disp_max}\n")
                f.write(f"Percentage: {self.result_data['percentage']:.2f}%\n")
                f.write(f"Passed Subjects: {self.result_data['passed_subjects']}\n")
                f.write(f"Failed Subjects: {self.result_data['failed_subjects']}\n")
                f.write(f"Overall Result: {self.result_data['overall_result']}\n")
                f.write("="*50 + "\n")
                
            abs_path = os.path.abspath(filename)
            messagebox.showinfo("Print Success", f"Marksheet saved successfully at:\n{abs_path}")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to save marksheet: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeSystemApp(root)
    root.mainloop()