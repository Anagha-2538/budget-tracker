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
        self.root.configure(bg="#000000")

        self.transaction_history = []
        self.current_balance = 0
        self.credit_amounts = []
        self.debit_amounts = []
        self.net_balance = []
        self.regular_categories = {}
        self.user_name = None  # Default user name
        self.pin = None  # Default PIN
        self.biometric_enabled = False  # Default biometric setting
        self.daily_limit = 0.0  # Default daily limit
        self.monthly_limit = 0.0  # Default monthly limit
        
        # added this
        self.greeting_label = None
        self.categories_display_frame = None  # Add this line

        if os.path.exists("regular_categories.json"):
            with open("regular_categories.json", "r") as f:
                self.regular_categories = json.load(f)
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.user_name = settings.get("user_name", "Anna")
                self.pin = settings.get("pin")
                self.biometric_enabled = settings.get("biometric_enabled", False)
                self.daily_limit = settings.get("daily_limit", 0.0)
                self.monthly_limit = settings.get("monthly_limit", 0.0)
        self.setup_ui()

    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 16), padding=8, background="#1e3a8a", foreground="#ffffff")
        self.style.map("TButton", foreground=[("active", "#ffffff")], background=[("active", "#3b82f6")])
        self.style.configure("TLabel", background="#000000", foreground="#ffffff", font=("Segoe UI", 16))
        self.style.configure("TFrame", background="#000000")
        self.style.configure("TLabelframe", background="#1e293b", font=("Segoe UI", 18, "bold"), foreground="#ffffff")
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 20, "bold"), background="#1e293b", foreground="#ffffff")
        self.style.configure("Custom.TEntry", fieldbackground="#2d3748", foreground="#ffffff", font=("Segoe UI", 16))
        self.style.configure("Card.TLabelframe", background="#1e293b", borderwidth=2, relief="flat")
        self.style.configure("CardHover.TLabelframe", background="#2a4365", borderwidth=2, relief="flat")

        # Top navigation bar with gradient effect
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill='x', side='top')
        nav_buttons = ["Home", "Transactions", "Reports", "Settings"]
        for btn_text in nav_buttons:
            btn = ttk.Button(top_frame, text=btn_text, style="TButton", command=lambda x=btn_text: self.switch_view(x))
            btn.pack(side='left', padx=10)

        # Greeting and balances
        greeting_frame = ttk.Frame(self.root, padding=10)
        greeting_frame.pack(fill='x')

        self.greeting_label = ttk.Label(greeting_frame, text=f"Hello, {self.user_name}", font=("Segoe UI", 26, "bold"), foreground="#ffffff")
        self.greeting_label.pack(side='left')

        self.balance_label = ttk.Label(greeting_frame, text=f"Total Balance: ₹{self.current_balance}", font=("Segoe UI", 22, "bold"), foreground="#10b981")
        self.balance_label.pack(side='left', padx=10)

        self.disposable_label = ttk.Label(greeting_frame, text=f"Disposable Balance: ₹{self.get_disposable_balance()}", font=("Segoe UI", 22, "bold"), foreground="#10b981")
        self.disposable_label.pack(side='left', padx=10)

        # Main content with card layout
        self.main_content = ttk.Frame(self.root, padding=20)
        self.main_content.pack(fill='both', expand=True)

        # Home View (default)
        self.home_frame = ttk.Labelframe(self.main_content, text="🏠 Home", padding=15, style="Card.TLabelframe")
        self.home_frame.pack(fill='both', expand=True)

        # Regular Categories Section in Home
        cat_frame = ttk.Labelframe(self.home_frame, text="📋 Set Regular Monthly Categories", padding=10, style="Card.TLabelframe")
        cat_frame.pack(side='left', fill='both', expand=False, padx=10, pady=10)

        self.category_entries = []
        for i in range(5):  # Allow up to 5 categories
            row = ttk.Frame(cat_frame)
            row.pack(fill='x', pady=5)
            ttk.Label(row, text=f"Category {i+1}:", font=("Segoe UI", 16), foreground="#ffffff").pack(side='left')
            cat_entry = ttk.Entry(row, width=20, style="Custom.TEntry", font=("Segoe UI", 24))
            cat_entry.pack(side='left', padx=5)
            ttk.Label(row, text="Expected Amount:", font=("Segoe UI", 16), foreground="#ffffff").pack(side='left')
            amt_entry = ttk.Entry(row, width=10, style="Custom.TEntry", font=("Segoe UI", 24))
            amt_entry.pack(side='left', padx=5)
            self.category_entries.append((cat_entry, amt_entry))
            

        def save_categories():
            updated_categories = self.regular_categories.copy()  # Start with existing categories
            valid_entries = False
            for cat_entry, amt_entry in self.category_entries:
                category = cat_entry.get().strip()
                amount_str = amt_entry.get().strip()
                if category and amount_str:
                    try:
                        amount = float(amount_str)
                        if amount >= 0:
                            updated_categories[category] = amount  # Update or add category
                            valid_entries = True
                        else:
                            messagebox.showerror("Error", f"Amount for '{category}' must be non-negative.")
                            return
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid amount for category '{category}'. Please enter a number.")
                        return
            if not valid_entries:
                messagebox.showerror("Error", "Please enter at least one valid category and amount.")
                return
            
            
            
            self.regular_categories = updated_categories
            with open("regular_categories.json", "w") as f:
                json.dump(self.regular_categories, f)
            self.update_balance_labels()
            self.update_categories_display()
            for cat_entry, amt_entry in self.category_entries:
                cat_entry.delete(0, tk.END)
                amt_entry.delete(0, tk.END)

        self.categories_display_frame = ttk.Labelframe(self.home_frame, text="📋 Regular Categories", padding=10, style="Card.TLabelframe")
        self.categories_display_frame.pack(side='right', fill='y', padx=10, pady=10, anchor='ne')
        self.update_categories_display()            

        # Transaction Input card
        self.input_frame = ttk.Labelframe(self.main_content, text="➕ Add Transaction", padding=15, style="Card.TLabelframe")
        self.input_frame.pack(side='left', fill='y', padx=(0, 20))
        self.input_frame.bind("<Enter>", lambda e: self.input_frame.configure(style="CardHover.TLabelframe"))
        self.input_frame.bind("<Leave>", lambda e: self.input_frame.configure(style="Card.TLabelframe"))

        self.credit_var = tk.BooleanVar()
        self.debit_var = tk.BooleanVar()
        tk.Checkbutton(self.input_frame, text="Credit", variable=self.credit_var, bg="#1e293b", fg="#ffffff", activebackground="#1e293b", activeforeground="#ffffff", selectcolor="#3b82f6", font=("Segoe UI", 18)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Checkbutton(self.input_frame, text="Debit", variable=self.debit_var, bg="#1e293b", fg="#ffffff", activebackground="#1e293b", activeforeground="#ffffff", selectcolor="#3b82f6", font=("Segoe UI", 18)).grid(row=0, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(self.input_frame, text="Category").grid(row=1, column=0, pady=10, sticky='w')
        self.category_entry = ttk.Entry(self.input_frame, width=25, style="Custom.TEntry", font=("Segoe UI", 24))
        self.category_entry.grid(row=1, column=1, pady=10, sticky='w')

        ttk.Label(self.input_frame, text="Amount").grid(row=2, column=0, pady=10, sticky='w')
        self.amount_entry = ttk.Entry(self.input_frame, width=25, style="Custom.TEntry", font=("Segoe UI", 24))
        self.amount_entry.grid(row=2, column=1, pady=10, sticky='w')

        self.amount_entry.bind("<Return>", lambda event: self.save_transaction())
        self.category_entry.bind("<Return>", lambda event: self.amount_entry.focus_set())

        submit_btn = ttk.Button(self.input_frame, text="✅ Submit", command=self.save_transaction, style="TButton")
        submit_btn.grid(row=3, column=0, columnspan=2, pady=15)
        submit_btn.bind("<Enter>", lambda e: submit_btn.configure(style="TButton"))
        submit_btn.bind("<Leave>", lambda e: submit_btn.configure(style="TButton"))

        action_frame = ttk.Frame(self.input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=10)
        view_btn = ttk.Button(action_frame, text="📋 View History", command=self.view_history, style="TButton")
        view_btn.grid(row=0, column=0, padx=10)
        export_btn = ttk.Button(action_frame, text="⬇ Export Data", command=self.export_data, style="TButton")
        export_btn.grid(row=0, column=1, padx=10)
        view_btn.bind("<Enter>", lambda e: view_btn.configure(style="TButton"))
        view_btn.bind("<Leave>", lambda e: view_btn.configure(style="TButton"))
        export_btn.bind("<Enter>", lambda e: export_btn.configure(style="TButton"))
        export_btn.bind("<Leave>", lambda e: export_btn.configure(style="TButton"))

        # Transaction Chart card
        self.chart_frame = ttk.Labelframe(self.main_content, text="📈 Transaction Chart", padding=15, style="Card.TLabelframe")
        self.chart_frame.pack(side='left', fill='both', expand=True)
        self.chart_frame.bind("<Enter>", lambda e: self.chart_frame.configure(style="CardHover.TLabelframe"))
        self.chart_frame.bind("<Leave>", lambda e: self.chart_frame.configure(style="Card.TLabelframe"))

        # Transaction History card
        self.history_frame = ttk.Labelframe(self.root, text="🕒 Transaction History", padding=15, style="Card.TLabelframe")
        self.history_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        self.history_frame.bind("<Enter>", lambda e: self.history_frame.configure(style="CardHover.TLabelframe"))
        self.history_frame.bind("<Leave>", lambda e: self.history_frame.configure(style="Card.TLabelframe"))

        self.history_list = tk.Listbox(self.history_frame, font=("Segoe UI", 16), height=8, bg="#0f172a", fg="#ffffff", highlightthickness=0)
        self.history_list.pack(fill='both', expand=True)

        # Settings View
        self.settings_frame = ttk.Labelframe(self.main_content, text="⚙ Settings", padding=15, style="Card.TLabelframe")
        self.settings_frame.pack(fill='both', expand=True)

        # Account Management
        account_frame = ttk.Labelframe(self.settings_frame, text="👤 Account Management", padding=10, style="Card.TLabelframe")
        account_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(account_frame, text="User Name:").pack(side='left', padx=5)
        self.name_entry = ttk.Entry(account_frame, width=20, style="Custom.TEntry", font=("Segoe UI", 16))
        self.name_entry.insert(0, self.user_name)
        self.name_entry.pack(side='left', padx=5)
        ttk.Button(account_frame, text="Update Name", command=self.update_name, style="TButton").pack(side='left', padx=5)

        # Security Settings
        security_frame = ttk.Labelframe(self.settings_frame, text="🔒 Security Settings", padding=10, style="Card.TLabelframe")
        security_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(security_frame, text="Set PIN:").pack(side='left', padx=5)
        self.pin_entry = ttk.Entry(security_frame, width=10, style="Custom.TEntry", show="*", font=("Segoe UI", 16))
        self.pin_entry.insert(0, self.pin if self.pin else "")
        self.pin_entry.pack(side='left', padx=5)
        ttk.Button(security_frame, text="Update PIN", command=self.update_pin, style="TButton").pack(side='left', padx=5)
        self.biometric_var = tk.BooleanVar(value=self.biometric_enabled)
        tk.Checkbutton(security_frame, text="Enable Biometric", variable=self.biometric_var, bg="#1e293b", fg="#ffffff", activebackground="#1e293b", activeforeground="#ffffff", selectcolor="#3b82f6", font=("Segoe UI", 16)).pack(side='left', padx=5)

        # Transaction Limits
        limits_frame = ttk.Labelframe(self.settings_frame, text="💸 Transaction Limits", padding=10, style="Card.TLabelframe")
        limits_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(limits_frame, text="Daily Limit (₹):").pack(side='left', padx=5)
        self.daily_limit_entry = ttk.Entry(limits_frame, width=10, style="Custom.TEntry", font=("Segoe UI", 16))
        self.daily_limit_entry.insert(0, str(self.daily_limit))
        self.daily_limit_entry.pack(side='left', padx=5)
        ttk.Label(limits_frame, text="Monthly Limit (₹):").pack(side='left', padx=5)
        self.monthly_limit_entry = ttk.Entry(limits_frame, width=10, style="Custom.TEntry", font=("Segoe UI", 16))
        self.monthly_limit_entry.insert(0, str(self.monthly_limit))
        self.monthly_limit_entry.pack(side='left', padx=5)
        ttk.Button(limits_frame, text="Update Limits", command=self.update_limits, style="TButton").pack(side='left', padx=5)

        self.update_graph()
        self.update_balance_labels()

    def update_categories_display(self):
    # Clear existing widgets in the display frame
        for widget in self.categories_display_frame.winfo_children():
            widget.destroy()
        # Display each category and amount
        for category, amount in self.regular_categories.items():
            row = ttk.Frame(self.categories_display_frame)
            row.pack(fill='x', pady=5)
            ttk.Label(row, text=f"{category}:", font=("Segoe UI", 16), foreground="#ffffff").pack(side='left')
            ttk.Label(row, text=f"₹{amount}", font=("Segoe UI", 16), foreground="#10b981").pack(side='left', padx=10)    

    def switch_view(self, view_name):
        self.home_frame.pack_forget()
        self.input_frame.pack_forget()
        self.chart_frame.pack_forget()
        self.settings_frame.pack_forget()
        if view_name == "Home":
            self.home_frame.pack(fill='both', expand=True)
        elif view_name == "Transactions":
            self.input_frame.pack(side='left', fill='y', padx=(0, 20))
        elif view_name == "Reports":
            self.chart_frame.pack(side='left', fill='both', expand=True)
        elif view_name == "Settings":
            self.settings_frame.pack(fill='both', expand=True)

    def get_disposable_balance(self):
        expected_total = sum(self.regular_categories.values()) if self.regular_categories else 0
        return max(0, self.current_balance - expected_total)

    def update_balance_labels(self):
        self.balance_label.config(text=f"Total Balance: ₹{self.current_balance}")
        self.disposable_label.config(text=f"Disposable Balance: ₹{self.get_disposable_balance()}")

    def save_transaction(self):
        try:
            category = self.category_entry.get()
            amount = float(self.amount_entry.get())
            trans_type = "Credit" if self.credit_var.get() else "Debit" if self.debit_var.get() else None

            if trans_type is None:
                messagebox.showerror("Error", "Please select either Credit or Debit")
                return
            if trans_type == "Debit" and amount > self.current_balance:
                messagebox.showerror("Error", "Insufficient balance")
                return

            # Calculate total debits for the current day
            today = datetime.now().strftime("%Y-%m-%d")
            daily_debit_total = sum(t["amount"] for t in self.transaction_history if t["type"] == "Debit" and t["date"].startswith(today))
            if trans_type == "Debit" and self.daily_limit > 0 and (daily_debit_total + amount) > self.daily_limit:
                response = messagebox.askyesno("Daily Limit Exceeded", 
                    f"Daily limit of ₹{self.daily_limit} will be exceeded. Current daily spending: ₹{daily_debit_total}. Do you want to continue?")
                if not response:
                    return

            monthly_total = sum(t["amount"] for t in self.transaction_history if t["type"] == "Debit" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
            if trans_type == "Debit" and self.monthly_limit > 0 and (monthly_total + amount) > self.monthly_limit:
                messagebox.showerror("Error", f"Transaction exceeds monthly limit of ₹{self.monthly_limit}")
                return

            self.add_transaction(category, amount, trans_type)
            self.category_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.credit_var.set(False)
            self.debit_var.set(False)
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
        self.update_balance_labels()
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
            ax.set_title("Transaction Trends")
            ax.legend()
            ax.grid(True, color='#2d3748', linestyle='--', alpha=0.7)

        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='#ffffff')
        ax.spines['bottom'].set_color('#ffffff')
        ax.spines['left'].set_color('#ffffff')
        ax.spines['top'].set_color('#1e293b')
        ax.spines['right'].set_color('#1e293b')
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

    def update_name(self):
        new_name = self.name_entry.get().strip()
        if new_name:
            self.user_name = new_name
            self.save_settings()
            self.root.title(f"My Wallet - Premium ({self.user_name})")
            self.greeting_label.config(text=f"Hello, {self.user_name}")
            messagebox.showinfo("Success", "User name updated successfully!")
        else:
            messagebox.showerror("Error", "Please enter a valid name.")

    def update_pin(self):
        new_pin = self.pin_entry.get().strip()
        if new_pin and new_pin.isdigit() and len(new_pin) >= 4:
            self.pin = new_pin
            self.save_settings()
            messagebox.showinfo("Success", "PIN updated successfully!")
        else:
            messagebox.showerror("Error", "Please enter a valid PIN (at least 4 digits).")

    def update_limits(self):
        try:
            daily_limit = float(self.daily_limit_entry.get())
            monthly_limit = float(self.monthly_limit_entry.get())
            if daily_limit >= 0 and monthly_limit >= 0:
                self.daily_limit = daily_limit
                self.monthly_limit = monthly_limit
                self.save_settings()
                messagebox.showinfo("Success", "Transaction limits updated successfully!")
            else:
                messagebox.showerror("Error", "Limits must be non-negative.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for limits.")

    def save_settings(self):
        settings = {
            "user_name": self.user_name,
            "pin": self.pin,
            "biometric_enabled": self.biometric_var.get(),
            "daily_limit": self.daily_limit,
            "monthly_limit": self.monthly_limit
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.daily_limit = settings.get("daily_limit", 0.0)
                self.monthly_limit = settings.get("monthly_limit", 0.0)
                self.daily_limit_entry.delete(0, tk.END)
                self.daily_limit_entry.insert(0, str(self.daily_limit))
                self.monthly_limit_entry.delete(0, tk.END)
                self.monthly_limit_entry.insert(0, str(self.monthly_limit))

if __name__ == "__main__":
    root = tk.Tk()
    app = WalletApp(root)
    root.mainloop()
