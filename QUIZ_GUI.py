import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import random
from datetime import datetime
 
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Color Quiz System")
        self.geometry("750x550")
        self.configure(bg="#f0f8ff")

        # Database
        self.conn = sqlite3.connect("quiz_system.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Variables
        self.username = None
        self.score = 0
        self.current_question = 0
        self.questions = []
        self.timer_id = None
        self.time_left = 30
        self.var = tk.StringVar()

        self.show_login_screen()

    # ---------------- Database Setup ---------------- #
    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, question TEXT, option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT, correct_option TEXT,image_path TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS scores (username TEXT, score INTEGER, timestamp TEXT)")
        self.conn.commit()

        # Ensure admin exists
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ("admin", "admin"))
        self.conn.commit()

        # Add sample questions if empty
        self.cursor.execute("SELECT COUNT(*) FROM questions")
        if self.cursor.fetchone()[0] == 0:
            sample_questions = [
                ("What is the capital of France?", "Paris", "London", "Rome", "Berlin", "a"),
                ("Which planet is known as the Red Planet?", "Earth", "Mars", "Jupiter", "Venus", "b"),
                ("What is the largest ocean on Earth?", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean", "d"),
                ("Who wrote 'To Kill a Mockingbird'?", "Harper Lee", "Mark Twain", "Ernest Hemingway", "F. Scott Fitzgerald", "a"),
                ("What is the chemical symbol for gold?", "Au", "Ag", "Fe", "Pb", "a"),
                ("What is the powerhouse of the cell?", "Mitochondria", "Nucleus", "Ribosome", "Endoplasmic Reticulum", "a"),
                ("The process by which plants make their own food is called what?", "Respiration", "Transpiration", "Photosynthesis", "Germination", "c"),
                ("What does CPU stand for?", "Central Processing Unit", "Computer Personal Unit", "Central Process Utility", "Core Processing Unit", "a"),
                ("Which programming language is often used for data science and machine learning?", "Java", "Python", "C++", "HTML", "b"),
                ("Who was the first President of the United States?", "Thomas Jefferson", "Abraham Lincoln", "George Washington", "John Adams", "c"),
            ]
            self.cursor.executemany("INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?)", sample_questions)
            self.conn.commit()

    # ---------------- Login/Register Screen ---------------- #
    def show_login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self, bg="#e0ffff")
        frame.pack(pady=50)

        tk.Label(frame, text="Quiz System Login", font=("Arial", 18, "bold"), bg="#e0ffff").pack(pady=10)
        tk.Label(frame, text="Username:", bg="#e0ffff").pack()
        self.username_entry = tk.Entry(frame)
        self.username_entry.pack()
        tk.Label(frame, text="Password:", bg="#e0ffff").pack()
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.pack(pady=5)

        btn_frame = tk.Frame(frame, bg="#e0ffff")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Login", bg="#7fffd4", command=self.login).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Register", bg="#7fffd4", command=self.register).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Admin Login", bg="#ff7f50", command=self.admin_login).grid(row=1, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if self.cursor.fetchone():
            if username == "admin":
                messagebox.showinfo("Info", "Use Admin Login button!")
                return
            self.username = username
            self.show_quiz_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "" or password == "":
            messagebox.showwarning("Warning", "Enter both username and password!")
            return
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    def admin_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "admin":
            self.username = username
            self.show_admin_panel()
        else:
            messagebox.showerror("Error", "Invalid Admin credentials!")

    # ---------------- Admin Panel ---------------- #
    def show_admin_panel(self):
        self.clear_screen()
        tk.Label(self, text="Admin Panel", font=("Arial", 18, "bold"), bg="#f0e68c").pack(pady=10)
        tk.Button(self, text="Add Question", bg="#98fb98", width=20, command=self.add_question).pack(pady=5)
        tk.Button(self, text="Edit Question", bg="#98fb98", width=20, command=self.edit_question).pack(pady=5)
        tk.Button(self, text="Delete Question", bg="#98fb98", width=20, command=self.delete_question).pack(pady=5)
        tk.Button(self, text="Manage Scoreboard", bg="#ffa07a", width=20, command=self.manage_scoreboard).pack(pady=5)
        tk.Button(self, text="Logout", bg="#f08080", width=20, command=self.show_login_screen).pack(pady=10)
        tk.Button(self, text="View All Questions", bg="#87cefa", width=20, command=self.view_all_questions).pack(pady=5)


    def add_question(self):
        self.open_question_editor()

    def edit_question(self):
        qid = simpledialog.askinteger("Edit Question", "Enter Question ID to edit:")
        if qid:
            self.cursor.execute("SELECT * FROM questions WHERE id=?", (qid,))
            question = self.cursor.fetchone()
            if question:
                self.open_question_editor(question)
            else:
                messagebox.showerror("Error", "Question ID not found!")
    def open_question_editor(self, question=None):
     win = tk.Toplevel(self)
     win.title("Question Editor")

     labels = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Option (a/b/c/d)"]
     entries = []

     defaults = question[1:7] if question else [""] * 6
     for i, lbl in enumerate(labels):
        tk.Label(win, text=lbl).grid(row=i, column=0, sticky="w")
        e = tk.Entry(win, width=50)
        e.grid(row=i, column=1)
        e.insert(0, defaults[i])
        entries.append(e)

    
    def delete_question(self):
        qid = simpledialog.askinteger("Delete Question", "Enter Question ID to delete:")
        if qid:
            self.cursor.execute("DELETE FROM questions WHERE id=?", (qid,))
            self.conn.commit()
            messagebox.showinfo("Success", "Question deleted!")

    def view_all_questions(self):
      win = tk.Toplevel(self)
      win.title("All Questions")
      win.geometry("750x450")
      win.configure(bg="#f0f8ff")

    # --- Frame + Canvas + Scrollbar setup ---
      frame = tk.Frame(win)
      frame.pack(fill="both", expand=True)

    # Canvas (the scrollable area)
      canvas = tk.Canvas(frame, bg="#f0f8ff")
      canvas.pack(side="left", fill="both", expand=True)

    # Scrollbar
      scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
      scrollbar.pack(side="right", fill="y")

    # Configure canvas scrolling
      canvas.configure(yscrollcommand=scrollbar.set)
      canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Frame inside the canvas for content
      scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
      canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # --- Fetch and Display Questions ---
      self.cursor.execute("SELECT * FROM questions ORDER BY id")
      questions = self.cursor.fetchall()

      if not questions:
        tk.Label(scrollable_frame, text="No questions available.", bg="#f0f8ff", font=("Arial", 12)).pack(pady=10)
      else:
        for q in questions:
            qid, question, a, b, c, d, correct = q
            tk.Label(scrollable_frame, text=f"ID: {qid}", font=("Arial", 10, "bold"), fg="blue", bg="#f0f8ff").pack(anchor="w", padx=10)
            tk.Label(scrollable_frame, text=f"Q: {question}", wraplength=680, justify="left", bg="#f0f8ff").pack(anchor="w", padx=25)
            tk.Label(scrollable_frame, text=f"A) {a}\nB) {b}\nC) {c}\nD) {d}", justify="left", bg="#f0f8ff").pack(anchor="w", padx=40)
            tk.Label(scrollable_frame, text=f"Correct Answer: {correct.upper()}", fg="green", bg="#f0f8ff").pack(anchor="w", padx=25, pady=(0,5))
            tk.Label(scrollable_frame, text="-"*90, fg="gray", bg="#f0f8ff").pack(anchor="w", padx=10, pady=3)

    # --- Close Button ---
      tk.Button(win, text="Close", bg="#ff7f7f", width=15, command=win.destroy).pack(pady=10)



    


    def open_question_editor(self, question=None):
        win = tk.Toplevel(self)
        win.title("Question Editor")
        labels = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Option (a/b/c/d)"]
        entries = []

        defaults = question[1:] if question else [""]*6
        for i, lbl in enumerate(labels):
            tk.Label(win, text=lbl).grid(row=i, column=0, sticky="w")
            e = tk.Entry(win, width=50)
            e.grid(row=i, column=1)
            e.insert(0, defaults[i])
            entries.append(e)

        def save():
            values = [e.get() for e in entries]
            if question:
                self.cursor.execute("UPDATE questions SET question=?, option_a=?, option_b=?, option_c=?, option_d=?, correct_option=? WHERE id=?", (*values, question[0]))
            else:
                self.cursor.execute("INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?)", values)
            self.conn.commit()
            messagebox.showinfo("Saved", "Question saved successfully!")
            win.destroy()

        tk.Button(win, text="Save", bg="#90ee90", command=save).grid(row=6, column=0, columnspan=2, pady=5)

    # ---------------- Quiz Screen ---------------- #
    def show_quiz_screen(self):
        self.clear_screen()
        self.cursor.execute("SELECT * FROM questions")
        self.questions = random.sample(self.cursor.fetchall(), min(5, self.cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]))
        self.current_question = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.clear_screen()
        if self.current_question >= len(self.questions):
            self.end_quiz()
            return

        question = self.questions[self.current_question]
        tk.Label(self, text=f"Q{self.current_question+1}: {question[1]}", font=("Arial", 14), bg="#ffe4e1").pack(pady=20)

        self.var.set(None)
        options = question[2:6]
        colors = ["#ffb6c1", "#add8e6", "#90ee90", "#ffffe0"]
        for i, opt in enumerate(options):
            tk.Radiobutton(self, text=opt, variable=self.var, value=chr(97+i), bg=colors[i], width=30).pack(anchor="w", pady=2)

        # Timer
        self.time_left = 30
        self.timer_label = tk.Label(self, text=f"Time left: {self.time_left}s", font=("Arial", 12), bg="#ffe4b5")
        self.timer_label.pack(pady=10)
        self.countdown()

        tk.Button(self, text="Submit", bg="#20b2aa", command=self.submit_answer).pack(pady=10)
    
    # Display question image if available
        image_path = question[7] if len(question) > 7 else None
        if image_path:
          try:
            img = Image.open(image_path)
            img = img.resize((250, 180))  # Adjust size as needed
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(self, image=photo, bg="#ffe4e1")
            img_label.image = photo
            img_label.pack(pady=5)
          except Exception as e:
            print("Image Error:", e)


    def countdown(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left}s")
            self.time_left -= 1
            self.timer_id = self.after(1000, self.countdown)
        else:
            messagebox.showinfo("Time's up!", f"The correct answer was: {self.questions[self.current_question][6].upper()}")
            self.current_question += 1
            self.show_question()

    def submit_answer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        q = self.questions[self.current_question]
        ans = self.var.get()
        if ans == q[6]:
            self.score += 1
            messagebox.showinfo("Correct!", "Correct answer!")
        else:
            messagebox.showinfo("Wrong!", f"Correct answer was: {q[6].upper()}")
        self.current_question += 1
        self.show_question()

    def end_quiz(self):
        self.clear_screen()
        tk.Label(self, text=f"Quiz Finished! Your Score: {self.score}/{len(self.questions)}", font=("Arial", 16), bg="#fafad2").pack(pady=20)
        self.cursor.execute("INSERT INTO scores VALUES (?, ?, ?)", (self.username, self.score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        tk.Button(self, text="Retry Quiz", bg="#98fb98", command=self.show_quiz_screen).pack(pady=5)
        tk.Button(self, text="View Scoreboard", bg="#87cefa", command=self.show_scoreboard).pack(pady=5)
        tk.Button(self, text="Logout", bg="#f08080", command=self.show_login_screen).pack(pady=5)

    # ---------------- Scoreboard ---------------- #
    def show_scoreboard(self):
        self.clear_screen()
        tk.Label(self, text="Scoreboard", font=("Arial", 16, "bold"), bg="#e6e6fa").pack(pady=10)
        self.cursor.execute("SELECT * FROM scores ORDER BY score DESC")
        scores = self.cursor.fetchall()
        for u, s, t in scores:
            tk.Label(self, text=f"{u:<15} {s:<3} {t}", bg="#f5f5dc").pack(anchor="w", padx=20)
        tk.Button(self, text="Back", bg="#ffa07a", command=self.end_quiz).pack(pady=10)

    # ---------------- Admin Manage Scoreboard ---------------- #
    def manage_scoreboard(self):
        win = tk.Toplevel(self)
        win.title("Manage Scoreboard")
        self.cursor.execute("SELECT rowid, * FROM scores")
        scores = self.cursor.fetchall()

        for i, score in enumerate(scores):
            tk.Label(win, text=f"{score[1]}  {score[2]}  {score[3]}").grid(row=i, column=0, sticky="w")

        def delete_score():
            rowid = simpledialog.askinteger("Delete Score", "Enter RowID to delete:")
            if rowid:
                self.cursor.execute("DELETE FROM scores WHERE rowid=?", (rowid,))
                self.conn.commit()
                messagebox.showinfo("Deleted", "Score deleted!")
                win.destroy()
                self.manage_scoreboard()

        tk.Button(win, text="Delete Score", bg="#ff6347", command=delete_score).grid(row=len(scores), column=0, pady=5)
        tk.Button(win, text="Reset Scores", bg="#ffa500", command=lambda:[self.cursor.execute("DELETE FROM scores"), self.conn.commit(), messagebox.showinfo("Reset", "All scores reset!"), win.destroy()]).grid(row=len(scores)+1, column=0, pady=5)
        tk.Button(win, text="Back", bg="#90ee90", command=win.destroy).grid(row=len(scores)+2, column=0, pady=5)

    # ---------------- Helpers ---------------- #
    def clear_screen(self):
        for w in self.winfo_children():
            w.destroy()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()



