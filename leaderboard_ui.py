import tkinter as tk
from tkinter import ttk

def show_visual_leaderboard(scores, highlight_score, final_score_text, reason_text, won):
    root = tk.Tk()
    root.withdraw()
    root.title("Desktop Snake Game - Leaderboard")
    root.geometry("600x520")
    root.configure(bg="#2b2b2b")
    root.attributes("-topmost", True)
    
    # Center the window
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"600x520+{x}+{y}")
    root.deiconify()
    
    main_frame = tk.Frame(root, bg="#2b2b2b", padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_text = "🏆 VICTORY! 🏆" if won else "GAME OVER"
    title_color = "#00ff00" if won else "#ff4444"
    tk.Label(main_frame, text=title_text, font=("Consolas", 24, "bold"), bg="#2b2b2b", fg=title_color).pack(pady=(0, 10))

    tk.Label(main_frame, text=reason_text, font=("Consolas", 12), bg="#2b2b2b", fg="#cccccc", wraplength=550).pack()
    tk.Label(main_frame, text=final_score_text, font=("Consolas", 16, "bold"), bg="#2b2b2b", fg="#ffffff").pack(pady=(10, 20))

    # Leaderboard Container
    leader_frame = tk.Frame(main_frame, bg="#2b2b2b")
    leader_frame.pack(fill=tk.X)

    # Headers
    headers = tk.Frame(leader_frame, bg="#1a1a1a")
    headers.pack(fill=tk.X)
    tk.Label(headers, text="Rank", width=5, font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="#ffd700", anchor="center").pack(side=tk.LEFT)
    tk.Label(headers, text="Score", width=15, font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="#ffd700", anchor="w").pack(side=tk.LEFT)
    tk.Label(headers, text="Difficulty", width=12, font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="#ffd700", anchor="w").pack(side=tk.LEFT)
    tk.Label(headers, text="Date", font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="#ffd700", anchor="w").pack(side=tk.LEFT)

    # Entries
    medals = ['🥇', '🥈', '🥉']
    for i, e in enumerate(scores):
        bg_col = "#3b3b3b" if i%2==0 else "#2b2b2b"
        entry_frame = tk.Frame(leader_frame, bg=bg_col, pady=5)
        entry_frame.pack(fill=tk.X)
        
        medal = medals[i] if i < 3 else f'{i+1}. '
        crown = ' ◀ YOU' if e['score'] == highlight_score else ''
        won_tag = ' 🏆' if e.get('won', False) else ''
        
        fg_col = "#00ffff" if crown else "#ffffff"
        
        tk.Label(entry_frame, text=medal, width=5, font=("Consolas", 12), bg=bg_col, fg=fg_col, anchor="center").pack(side=tk.LEFT)
        tk.Label(entry_frame, text=f"{e['score']:>3}/{e['max']:<3} ({e['pct']:>3}%)", width=15, font=("Consolas", 12), bg=bg_col, fg=fg_col, anchor="w").pack(side=tk.LEFT)
        tk.Label(entry_frame, text=f"{e['difficulty']:<12}", width=12, font=("Consolas", 12), bg=bg_col, fg=fg_col, anchor="w").pack(side=tk.LEFT)
        tk.Label(entry_frame, text=f"{e['date']}{won_tag}{crown}", font=("Consolas", 12), bg=bg_col, fg=fg_col, anchor="w").pack(side=tk.LEFT)

    play_again_res = [False]
    def on_play():
        play_again_res[0] = True
        root.destroy()
    def on_exit():
        play_again_res[0] = False
        root.destroy()
    def on_reset():
        from tkinter import messagebox
        import os
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to completely reset the leaderboard?", parent=root):
            try:
                high_score_file = os.path.join(os.path.expanduser("~"), "Desktop", "snake_game_desktop", "high_scores.json")
                if os.path.exists(high_score_file):
                    os.remove(high_score_file)
                # Dynamically remove visual entries
                for widget in leader_frame.winfo_children():
                    if widget != headers:
                        widget.destroy()
                messagebox.showinfo("Leaderboard Reset", "The leaderboard has been successfully reset.", parent=root)
            except Exception as e:
                messagebox.showerror("Reset Failed", f"An error occurred: {e}", parent=root)

    btn_frame = tk.Frame(main_frame, bg="#2b2b2b")
    btn_frame.pack(fill=tk.X, pady=(20, 0))
    
    tk.Button(btn_frame, text="▶ Play Again", font=("Consolas", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", command=on_play, relief="flat", padx=10, pady=5).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(btn_frame, text="↺ Reset", font=("Consolas", 12, "bold"), bg="#FF9800", fg="white", activebackground="#F57C00", command=on_reset, relief="flat", padx=10, pady=5).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(btn_frame, text="✖ Exit", font=("Consolas", 12, "bold"), bg="#f44336", fg="white", activebackground="#da190b", command=on_exit, relief="flat", padx=10, pady=5).pack(side=tk.RIGHT, expand=True, padx=5)

    root.mainloop()
    return play_again_res[0]
