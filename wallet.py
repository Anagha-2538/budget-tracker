#TODO: 
# 1. minimum balance and alert 
# 2. refine the graph visually 
# 3. fix view_history button, as nothing opens
# 4. improve the UI

# TODO: integrate my project with real bank account to create publishable and scalable app

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import os

class WalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Wallet - Premium")
        self.root.geometry("1280x800")
        self.root.configure(bg="#1a1a1a")

        # Set live wallpaper (gif or animated image)
        # self.bg_image = tk.PhotoImage(file="metallic_dark_texture.png")  # Placeholder texture image
        self.background_label = tk.Label(self.root)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.transaction_history = []
        self.current_balance = 0
        self.credit_amounts = []
        self.debit_amounts = []
        self.net_balance = []

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=10, background="#1f2937", foreground="#ffffff")
        style.map("TButton", foreground=[("active", "#ffffff")], background=[("active", "#111827")])
        style.configure("TLabel", background="#1a1a1a", foreground="#f9fafb", font=("Segoe UI", 11))
        style.configure("TFrame", background="#1a1a1a")
        style.configure("TLabelframe", background="#111827", font=("Segoe UI", 12, "bold"), foreground="#ffffff")
        style.configure("TLabelframe.Label", font=("Segoe UI", 14, "bold"), background="#111827", foreground="#facc15")

        top_frame = ttk.Frame(self.root, padding=15)
        top_frame.pack(fill='x')

        ttk.Label(top_frame, text="💼 Wallet Dashboard", font=("Segoe UI", 28, "bold"), foreground="#facc15").pack(side='left')
        self.balance_label = ttk.Label(top_frame, text=f"Balance: ₹{self.current_balance}", font=("Segoe UI", 18, "bold"), foreground="#10b981")
        self.balance_label.pack(side='right')

        main_content = ttk.Frame(self.root, padding=20)
        main_content.pack(fill='both', expand=True)

        input_frame = ttk.Labelframe(main_content, text="➕ Add a Transaction", padding=30)
        input_frame.pack(side='left', fill='y', padx=(0, 20))

        self.trans_type = tk.StringVar(value="Credit")
        ttk.Radiobutton(input_frame, text="Credit", variable=self.trans_type, value="Credit").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        ttk.Radiobutton(input_frame, text="Debit", variable=self.trans_type, value="Debit").grid(row=0, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(input_frame, text="Category").grid(row=1, column=0, pady=10, sticky='w')
        self.category_entry = ttk.Entry(input_frame, width=40)
        self.category_entry.grid(row=1, column=1, pady=10, sticky='w')

        ttk.Label(input_frame, text="Amount").grid(row=2, column=0, pady=10, sticky='w')
        self.amount_entry = ttk.Entry(input_frame, width=40)
        self.amount_entry.grid(row=2, column=1, pady=10, sticky='w')

        self.amount_entry.bind("<Return>", lambda event: self.save_transaction())
        self.category_entry.bind("<Return>", lambda event: self.amount_entry.focus_set())

        ttk.Button(input_frame, text="✅ Submit", command=self.save_transaction).grid(row=3, column=0, columnspan=2, pady=20)

        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(action_frame, text="📋 View History", command=self.view_history).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="⬇ Export Data", command=self.export_data).grid(row=0, column=1, padx=5)

        self.chart_frame = ttk.Labelframe(main_content, text="📈 Transaction Chart", padding=20)
        self.chart_frame.pack(side='right', fill='both', expand=True)

        self.history_frame = ttk.Labelframe(self.root, text="🕒 Transaction History", padding=10)
        self.history_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.history_list = tk.Listbox(self.history_frame, font=("Segoe UI", 11), height=8, bg="#0f172a", fg="#f9fafb")
        self.history_list.pack(fill='both', expand=True)

        self.update_graph()

    def update_balance_label(self):
        self.balance_label.config(text=f"Balance: ₹{self.current_balance}")

    def save_transaction(self):
        try:
            category = self.category_entry.get()
            amount = float(self.amount_entry.get())
            trans_type = self.trans_type.get()

            if trans_type == "Debit" and amount > self.current_balance:
                messagebox.showerror("Error", "Insufficient balance")
                return

            self.add_transaction(category, amount, trans_type)
            self.category_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.category_entry.focus_set()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    def add_transaction(self, category, amount, transaction_type):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction = {
            "type": transaction_type,
            "category": category,
            "amount": amount,
            "date": date_time
        }
        self.transaction_history.append(transaction)

        if transaction_type == "Credit":
            self.current_balance += amount
            self.credit_amounts.append(amount)
            self.debit_amounts.append(0)
        else:
            self.current_balance -= amount
            self.debit_amounts.append(amount)
            self.credit_amounts.append(0)

        self.net_balance.append(self.current_balance)
        self.history_list.insert(tk.END, f"{transaction['date']} - {transaction_type}: {category} - ₹{amount}")
        self.update_balance_label()
        self.update_graph()
        self.check_balance_warning()

    def update_graph(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        if self.transaction_history:
            x = np.arange(len(self.transaction_history))
            ax.plot(x, np.cumsum(self.credit_amounts), label="Credit", color='#10b981', marker='o')
            ax.plot(x, np.cumsum(self.debit_amounts), label="Debit", color='#ef4444', marker='o')
            ax.plot(x, self.net_balance, label="Net Balance", color='#3b82f6', marker='o')

            ax.set_xlabel("Transactions")
            ax.set_ylabel("Amount")
            ax.set_title("📊 Transaction Trends")
            ax.legend()
            ax.grid(True)

        fig.patch.set_facecolor('#1a1a1a')
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def check_balance_warning(self):
        if self.current_balance < 2000:
            messagebox.showwarning("⚠ Low Balance", "Your balance is below ₹2000!")

    def view_history(self):
        self.history_list.delete(0, tk.END)
        for t in self.transaction_history:
            self.history_list.insert(tk.END, f"{t['date']} - {t['type']}: {t['category']} - ₹{t['amount']}")

    def export_data(self):
        with open("wallet_data.json", "w") as f:
            json.dump(self.transaction_history, f, indent=4)
        messagebox.showinfo("Exported", "Transaction history exported to wallet_data.json")

if __name__ == "__main__":
    root = tk.Tk()
    app = WalletApp(root)
    root.mainloop()
