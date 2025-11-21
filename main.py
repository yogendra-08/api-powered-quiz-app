import tkinter as tk
from tkinter import ttk, messagebox
from quiz_app import QuizApp
from stats_manager import StatsManager


root = tk.Tk()
root.title("Digital Quiz App")
root.geometry("800x600")
root.resizable(True, True)

quiz = QuizApp()
stats = StatsManager(root)

bg_color = "#1a1a2e"
fg_color = "#ffffff"
button_color = "#7c3aed"
success_color = "#10b981"
error_color = "#ef4444"
accent_color = "#a78bfa"

root.configure(bg=bg_color)



def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def create_label(parent, text, font, **kwargs):
    return tk.Label(parent, text=text, font=font, bg=bg_color, fg=fg_color, **kwargs)


def create_button(parent, text, cmd, color, **kwargs):
    return tk.Button(parent, text=text, command=cmd,
                     font=("Arial", 14, "bold"), bg=color,
                     fg="white", cursor="hand2", **kwargs)


# ------------------ MAIN MENU ------------------
def show_main_menu():
    clear_window()

    create_label(root, "🎯 Digital Quiz App", ("Arial", 32, "bold")).pack(pady=50)
    create_label(root, "Test Your Knowledge with Live Questions",
                 ("Arial", 14)).pack(pady=10)

    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=50)

    create_button(frame, "📝 Start Quiz", show_quiz_setup, button_color,
                  width=20, height=2).pack(pady=15)
    create_button(frame, "📊 View Statistics", show_statistics, success_color,
                  width=20, height=2).pack(pady=15)
    create_button(frame, "❌ Exit", exit_app, error_color,
                  width=20, height=2).pack(pady=15)

    create_label(root, "Powered by Open Trivia Database API",
                 ("Arial", 10)).pack(side="bottom", pady=20)


# ------------------ QUIZ SETUP ------------------
def show_quiz_setup():
    clear_window()

    create_label(root, "⚙️ Quiz Setup", ("Arial", 28, "bold")).pack(pady=30)

    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=20)

    global questions_var, category_var, difficulty_var

    questions_var = tk.StringVar(value="10")
    category_var = tk.StringVar()
    difficulty_var = tk.StringVar()

    # NUMBER OF QUESTIONS
    tk.Label(frame, text="Number of Questions:", font=("Arial", 14),
             bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=20, pady=15)
    tk.Spinbox(frame, from_=5, to=20, textvariable=questions_var,
               font=("Arial", 12), width=15).grid(row=0, column=1)

    # CATEGORY
    categories = list(quiz.get_categories().keys())
    category_var.set(categories[0])

    tk.Label(frame, text="Category:", font=("Arial", 14),
             bg=bg_color, fg=fg_color).grid(row=1, column=0, padx=20, pady=15)
    ttk.Combobox(frame, textvariable=category_var, values=categories,
                 font=("Arial", 12), width=25,
                 state="readonly").grid(row=1, column=1)

    # DIFFICULTY
    difficulties = quiz.get_difficulties()
    difficulty_var.set(difficulties[0])

    tk.Label(frame, text="Difficulty:", font=("Arial", 14),
             bg=bg_color, fg=fg_color).grid(row=2, column=0, padx=20, pady=15)
    ttk.Combobox(frame, textvariable=difficulty_var, values=difficulties,
                 font=("Arial", 12), width=25,
                 state="readonly").grid(row=2, column=1)

    # BUTTONS
    btn_frame = tk.Frame(root, bg=bg_color)
    btn_frame.pack(pady=40)

    create_button(btn_frame, "🚀 Start Quiz", start_quiz,
                  success_color, width=15, height=2).pack(side="left", padx=10)

    create_button(btn_frame, "⬅️ Back", show_main_menu,
                  error_color, width=15, height=2).pack(side="left", padx=10)


# ------------------ START QUIZ ------------------
def start_quiz():
    try:
        num = int(questions_var.get())
        category_name = category_var.get()
        difficulty = difficulty_var.get()

        category_id = quiz.get_categories()[category_name]

        clear_window()
        create_label(root, "⏳ Loading questions...", ("Arial", 16)).pack(pady=20)
        root.update()

        if not quiz.fetch_questions(num, category_id,
                                    None if difficulty == "Any Difficulty" else difficulty):
            messagebox.showerror("Error", "Failed to fetch questions")
            show_quiz_setup()
            return

        show_quiz_window()

    except Exception as e:
        messagebox.showerror("Error", str(e))
        show_quiz_setup()


# ------------------ QUIZ WINDOW ------------------
def show_quiz_window():
    clear_window()

    question = quiz.get_current_question()
    if not question:
        show_results()
        return

    current, total = quiz.get_progress()

    # TOP
    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=10)
    create_label(frame, f"Question {current} of {total}",
                 ("Arial", 14, "bold")).pack()

    create_label(root,
                 f"📁 {question['category']} | ⭐ {question['difficulty'].title()}",
                 ("Arial", 12)).pack()

    # QUESTION BOX
    q_frame = tk.Frame(root, bg="#f8fafc", relief="solid", borderwidth=2)
    q_frame.pack(padx=40, pady=20, fill="x")

    tk.Label(q_frame, text=question['question'], font=("Arial", 16, "bold"),
             bg="#f8fafc", fg="#1a1a2e",
             wraplength=700, justify="center").pack(pady=20)

    # OPTIONS
    global selected_answer
    selected_answer = tk.StringVar()

    opt_frame = tk.Frame(root, bg=bg_color)
    opt_frame.pack(pady=10)

    for ans in question["all_answers"]:
        tk.Radiobutton(opt_frame, text=ans, value=ans, variable=selected_answer,
                       font=("Arial", 13), bg=bg_color, fg=fg_color,
                       activebackground=bg_color,
                       activeforeground=accent_color,
                       selectcolor=accent_color,
                       wraplength=600, justify="left",
                       cursor="hand2").pack(anchor="w", padx=50, pady=6)

    # FEEDBACK
    global feedback_label
    feedback_label = tk.Label(root, text="", font=("Arial", 14, "bold"),
                              bg=bg_color, fg=fg_color)
    feedback_label.pack(pady=10)

    create_button(root, "✅ Submit Answer", submit_answer,
                  success_color, width=20, height=2).pack(pady=15)


def submit_answer():
    ans = selected_answer.get()
    if not ans:
        messagebox.showwarning("Warning", "Select an answer!")
        return

    q = quiz.get_current_question()
    correct = quiz.check_answer(ans)

    if correct:
        feedback_label.config(text="✅ Correct!", fg="#10b981")
    else:
        feedback_label.config(text=f"❌ Wrong | Correct: {q['correct_answer']}",
                              fg="#ef4444")

    root.after(1500, lambda:
               show_quiz_window() if quiz.next_question() else show_results())


# ------------------ RESULTS ------------------
def show_results():
    clear_window()

    summary = quiz.get_quiz_summary()
    stats.save_quiz_result(summary)

    create_label(root, "🎊 Quiz Complete!", ("Arial", 32, "bold")).pack(pady=30)

    frame = tk.Frame(root, bg="#f8fafc", relief="solid", borderwidth=3)
    frame.pack(padx=50, pady=20)

    score = summary["score_percentage"]
    color = success_color if score >= 70 else error_color

    tk.Label(frame, text=f"{score:.1f}%", font=("Arial", 48, "bold"),
             bg="#f8fafc", fg=color).pack(pady=20)

    tk.Label(frame, text=f"""
Correct: {summary['correct_answers']}  
Incorrect: {summary['incorrect_answers']}
Total: {summary['total_questions']}
Time: {summary['time_taken_seconds']} sec
    """, font=("Arial", 14), bg="#f8fafc",
             fg="#1a1a2e", justify="left").pack(pady=20)

    # MESSAGE
    msg = "🌟 Outstanding!" if score >= 90 else \
          "👏 Great job!" if score >= 70 else \
          "👍 Good effort!" if score >= 50 else \
          "💪 Keep practicing!"

    create_label(root, msg, ("Arial", 16, "bold")).pack(pady=20)

    f = tk.Frame(root, bg=bg_color)
    f.pack()

    create_button(f, "🔄 Try Again", show_quiz_setup,
                  button_color, width=15, height=2).pack(side="left", padx=10)
    create_button(f, "📊 Stats", show_statistics,
                  success_color, width=15, height=2).pack(side="left", padx=10)
    create_button(f, "🏠 Menu", show_main_menu,
                  error_color, width=15, height=2).pack(side="left", padx=10)


# ------------------ STATISTICS ------------------
def show_statistics():
    clear_window()

    if stats.get_total_quizzes() == 0:
        show_no_stats()
        return

    create_label(root, "📊 Your Statistics", ("Arial", 28, "bold")).pack(pady=20)

    summary = stats.get_statistics_summary()

    canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=bg_color)

    scroll_frame.bind("<Configure>", lambda e:
                      canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((400, 0), window=scroll_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    # MAIN STATS
    main = tk.Frame(scroll_frame, bg="#f8fafc", relief="solid", borderwidth=2)
    main.pack(padx=40, pady=10, fill="x")

    tk.Label(main, text="📈 Overall Performance", font=("Arial", 18, "bold"),
             bg="#f8fafc", fg="#1a1a2e").pack(pady=10)

    tk.Label(main, text=f"""
Total Quizzes: {summary['total_quizzes']}
Total Questions: {summary['total_questions_answered']}

Mean Score: {summary['mean_score']}%
Median Score: {summary['median_score']}%
Mode Score: {summary['mode_score']}%
Std Dev: {summary['std_deviation']:.2f}

Accuracy: {summary['overall_accuracy']}%
Best Score: {summary['best_score']}%
Worst Score: {summary['worst_score']}%
    """, font=("Arial", 13), bg="#f8fafc",
             fg="#1a1a2e", justify="left").pack(pady=10)

    # RECENT QUIZZES
    recent = tk.Frame(scroll_frame, bg="#f8fafc", relief="solid", borderwidth=2)
    recent.pack(padx=40, pady=10, fill="x")

    tk.Label(recent, text="📝 Recent Quizzes", font=("Arial", 18, "bold"),
             bg="#f8fafc", fg="#1a1a2e").pack(pady=10)

    for _, q in stats.get_recent_quizzes(5).iterrows():
        tk.Label(recent, text=f"{q['date']} | {q['category']} | "
                              f"{q['difficulty']} | {q['score_percentage']:.1f}%",
                 font=("Arial", 11), bg="#f8fafc", fg="#4b5563").pack(pady=3)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    create_button(root, "⬅️ Back", show_main_menu,
                  error_color, width=20, height=2).pack(pady=20)


def show_no_stats():
    clear_window()
    create_label(root, "📊 Statistics", ("Arial", 28, "bold")).pack(pady=50)
    create_label(root, "No quiz data available.\nTake a quiz first!",
                 ("Arial", 16), justify="center").pack(pady=40)
    create_button(root, "⬅️ Back", show_main_menu,
                  error_color).pack(pady=30)


# ------------------ EXIT ------------------
def exit_app():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        root.quit()


# ------------------ RUN ------------------
show_main_menu()
root.mainloop()
