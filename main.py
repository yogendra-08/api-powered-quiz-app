import tkinter as tk
from tkinter import ttk, messagebox
from quiz_app import QuizApp
from stats_manager import StatsManager


class QuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Quiz App with Stats")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.quiz = QuizApp()
        self.stats = StatsManager(root)
        self.bg_color, self.fg_color = "#1a1a2e", "#ffffff"
        self.button_color, self.success_color, self.error_color = "#7c3aed", "#10b981", "#ef4444"
        self.accent_color, self.hover_color = "#a78bfa", "#8b5cf6"
        self.root.configure(bg=self.bg_color)
        self.show_main_menu()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def _create_label(self, parent, text, font, **kwargs):
        return tk.Label(parent, text=text, font=font, bg=self.bg_color, fg=self.fg_color, **kwargs)
    
    def _create_button(self, parent, text, command, color, **kwargs):
        return tk.Button(parent, text=text, font=("Arial", 14, "bold"), bg=color, fg="white", 
                        command=command, cursor="hand2", **kwargs)
    
    def show_main_menu(self):
        self.clear_window()
        self._create_label(self.root, "🎯 Digital Quiz App", ("Arial", 32, "bold")).pack(pady=50)
        self._create_label(self.root, "Test Your Knowledge with Live Questions", ("Arial", 14)).pack(pady=10)
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=50)
        for text, cmd, color in [("📝 Start Quiz", self.show_quiz_setup, self.button_color),
                                  ("📊 View Statistics", self.show_statistics, self.success_color),
                                  ("❌ Exit", self.exit_app, self.error_color)]:
            self._create_button(button_frame, text, cmd, color, width=20, height=2).pack(pady=15)
        self._create_label(self.root, "Powered by Open Trivia Database API", ("Arial", 10)).pack(side="bottom", pady=20)
    
    def show_quiz_setup(self):
        self.clear_window()
        self._create_label(self.root, "⚙️ Quiz Setup", ("Arial", 28, "bold")).pack(pady=30)
        setup_frame = tk.Frame(self.root, bg=self.bg_color)
        setup_frame.pack(pady=20)
        
        self.questions_var = tk.StringVar(value="10")
        tk.Label(setup_frame, text="Number of Questions:", font=("Arial", 14), bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        tk.Spinbox(setup_frame, from_=5, to=20, textvariable=self.questions_var, font=("Arial", 12), width=15).grid(row=0, column=1, padx=20, pady=15)
        
        categories = list(self.quiz.get_categories().keys())
        self.category_var = tk.StringVar(value=categories[0])
        tk.Label(setup_frame, text="Category:", font=("Arial", 14), bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, padx=20, pady=15, sticky="w")
        ttk.Combobox(setup_frame, textvariable=self.category_var, values=categories, font=("Arial", 12), width=25, state="readonly").grid(row=1, column=1, padx=20, pady=15)
        
        difficulties = self.quiz.get_difficulties()
        self.difficulty_var = tk.StringVar(value=difficulties[0])
        tk.Label(setup_frame, text="Difficulty:", font=("Arial", 14), bg=self.bg_color, fg=self.fg_color).grid(row=2, column=0, padx=20, pady=15, sticky="w")
        ttk.Combobox(setup_frame, textvariable=self.difficulty_var, values=difficulties, font=("Arial", 12), width=25, state="readonly").grid(row=2, column=1, padx=20, pady=15)
        
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=40)
        self._create_button(button_frame, "🚀 Start Quiz", self.start_quiz, self.success_color, width=15, height=2).pack(side="left", padx=10)
        self._create_button(button_frame, "⬅️ Back", self.show_main_menu, self.error_color, width=15, height=2).pack(side="left", padx=10)
    
    def start_quiz(self):
        try:
            num_questions = int(self.questions_var.get())
            category_name = self.category_var.get()
            difficulty = self.difficulty_var.get()
            category_id = self.quiz.get_categories()[category_name]
            self.quiz.quiz_category = category_name
            self.quiz.quiz_difficulty = difficulty if difficulty != "Any Difficulty" else "Mixed"
            self._create_label(self.root, "⏳ Loading questions...", ("Arial", 16)).pack(pady=20)
            self.root.update()
            if self.quiz.fetch_questions(num_questions, category_id, None if difficulty == "Any Difficulty" else difficulty):
                self.show_quiz_window()
            else:
                messagebox.showerror("Error", "Failed to fetch questions. Please check your internet connection.")
                self.show_quiz_setup()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.show_quiz_setup()
    
    def show_quiz_window(self):
        self.clear_window()
        question = self.quiz.get_current_question()
        if not question:
            self.show_results()
            return
        
        current, total = self.quiz.get_progress()
        progress_frame = tk.Frame(self.root, bg=self.bg_color)
        progress_frame.pack(fill="x", padx=20, pady=10)
        self._create_label(progress_frame, f"Question {current} of {total}", ("Arial", 14, "bold")).pack()
        self._create_label(self.root, f"📁 {question['category']} | ⭐ {question['difficulty'].title()}", ("Arial", 12)).pack(pady=5)
        
        question_frame = tk.Frame(self.root, bg="#f8fafc", relief="solid", borderwidth=2)
        question_frame.pack(padx=40, pady=20, fill="both", expand=True)
        tk.Label(question_frame, text=question['question'], font=("Arial", 16, "bold"), bg="#f8fafc", fg="#1a1a2e", wraplength=700, justify="center").pack(pady=30)
        
        self.selected_answer = tk.StringVar()
        options_frame = tk.Frame(self.root, bg=self.bg_color)
        options_frame.pack(pady=20)
        for answer in question['all_answers']:
            tk.Radiobutton(options_frame, text=answer, variable=self.selected_answer, value=answer, font=("Arial", 13),
                          bg=self.bg_color, fg=self.fg_color, selectcolor=self.accent_color, activebackground=self.bg_color,
                          activeforeground=self.accent_color, wraplength=600, justify="left", cursor="hand2").pack(anchor="w", padx=50, pady=8)
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 13, "bold"), bg=self.bg_color, fg=self.fg_color)
        self.feedback_label.pack(pady=10)
        self._create_button(self.root, "✅ Submit Answer", self.submit_answer, self.success_color, width=20, height=2).pack(pady=20)
    
    def submit_answer(self):
        answer = self.selected_answer.get()
        if not answer:
            messagebox.showwarning("Warning", "Please select an answer!")
            return
        current_q = self.quiz.get_current_question()
        is_correct = self.quiz.check_answer(answer)
        if is_correct:
            self.feedback_label.config(text="✅ Correct! Well done!", fg=self.success_color)
        else:
            self.feedback_label.config(text=f"❌ Incorrect. Correct answer: {current_q['correct_answer']}", fg=self.error_color)
        self.root.after(1500, lambda: self.show_quiz_window() if self.quiz.next_question() else self.show_results())
    
    def show_results(self):
        self.clear_window()
        summary = self.quiz.get_quiz_summary()
        self.stats.save_quiz_result(summary)
        self._create_label(self.root, "🎊 Quiz Complete!", ("Arial", 32, "bold")).pack(pady=30)
        
        score_frame = tk.Frame(self.root, bg="#f8fafc", relief="solid", borderwidth=3)
        score_frame.pack(padx=50, pady=20)
        score_percentage = summary['score_percentage']
        tk.Label(score_frame, text=f"{score_percentage:.1f}%", font=("Arial", 48, "bold"), bg="#f8fafc",
                fg=self.success_color if score_percentage >= 70 else self.error_color).pack(pady=20)
        tk.Label(score_frame, text=f"""Correct Answers: {summary['correct_answers']} ✅
Incorrect Answers: {summary['incorrect_answers']} ❌
Total Questions: {summary['total_questions']}
Time Taken: {summary['time_taken_seconds']} seconds""", font=("Arial", 14), bg="#f8fafc", fg="#1a1a2e", justify="left").pack(pady=20, padx=40)
        
        message = "🌟 Outstanding! You're a genius!" if score_percentage >= 90 else "👏 Great job! Well done!" if score_percentage >= 70 else "👍 Good effort! Keep practicing!" if score_percentage >= 50 else "💪 Don't give up! Try again!"
        self._create_label(self.root, message, ("Arial", 16, "bold")).pack(pady=20)
        
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=20)
        for text, cmd, color in [("🔄 Try Again", self.show_quiz_setup, self.button_color),
                                  ("📊 View Stats", self.show_statistics, self.success_color),
                                  ("🏠 Main Menu", self.show_main_menu, self.error_color)]:
            self._create_button(button_frame, text, cmd, color, width=15, height=2).pack(side="left", padx=10)
    
    def show_statistics(self):
        self.clear_window()
        if self.stats.get_total_quizzes() == 0:
            self.show_no_stats()
            return
        self._create_label(self.root, "📊 Your Statistics", ("Arial", 28, "bold")).pack(pady=20)
        stats_summary = self.stats.get_statistics_summary()
        
        canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((400, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_stats_frame = tk.Frame(scrollable_frame, bg="#f8fafc", relief="solid", borderwidth=2)
        main_stats_frame.pack(padx=40, pady=10, fill="x")
        tk.Label(main_stats_frame, text="📈 Overall Performance", font=("Arial", 18, "bold"), bg="#f8fafc", fg="#1a1a2e").pack(pady=10)
        tk.Label(main_stats_frame, text=f"""Total Quizzes Taken: {stats_summary['total_quizzes']}
Total Questions Answered: {stats_summary['total_questions_answered']}

📊 Score Statistics (Using SciPy & NumPy):
Mean Score: {stats_summary['mean_score']}%
Median Score: {stats_summary['median_score']}%
Mode Score: {stats_summary['mode_score']}%
Standard Deviation: {stats_summary['std_deviation']:.2f}

🎯 Performance:
Overall Accuracy: {stats_summary['overall_accuracy']}%
Best Score: {stats_summary['best_score']}%
Worst Score: {stats_summary['worst_score']}%""", font=("Arial", 13), bg="#f8fafc", fg="#1a1a2e", justify="left").pack(pady=15, padx=20)
        
        recent_frame = tk.Frame(scrollable_frame, bg="#f8fafc", relief="solid", borderwidth=2)
        recent_frame.pack(padx=40, pady=10, fill="x")
        tk.Label(recent_frame, text="📝 Recent Quizzes", font=("Arial", 18, "bold"), bg="#f8fafc", fg="#1a1a2e").pack(pady=10)
        for _, quiz in self.stats.get_recent_quizzes(5).iterrows():
            tk.Label(recent_frame, text=f"{quiz['date']} | {quiz['category']} | {quiz['difficulty']} | Score: {quiz['score_percentage']:.1f}%",
                    font=("Arial", 11), bg="#f8fafc", fg="#4b5563").pack(pady=3, padx=20, anchor="w")
        tk.Label(recent_frame, text="", bg="#f8fafc").pack(pady=5)
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        self._create_button(self.root, "⬅️ Back to Menu", self.show_main_menu, self.error_color, width=20, height=2).pack(side="bottom", pady=20)
    
    def show_no_stats(self):
        self.clear_window()
        self._create_label(self.root, "📊 Statistics", ("Arial", 28, "bold")).pack(pady=50)
        self._create_label(self.root, "No quiz data available yet.\n\nTake a quiz to see your statistics!", ("Arial", 16), justify="center").pack(pady=50)
        self._create_button(self.root, "⬅️ Back to Menu", self.show_main_menu, self.error_color, width=20, height=2).pack(pady=30)
    
    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()


def main():
    root = tk.Tk()
    app = QuizGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()