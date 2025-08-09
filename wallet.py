import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import os

class WalletApp:
    def __init__(self, root):
        print("WalletApp v3 - TIGHT scrollbars and ₹5000 limit dialog - August 2025")  # Debug to confirm code version
        self.root = root
        self.root.title("My Wallet - Premium")
        self.root.geometry("1280x800")

        self.transaction_history = []
        self.current_balance = 0
        self.credit_amounts = []
        self.debit_amounts = []
        self.net_balance = []
        self.regular_categories = {}
        self.user_name = None
        self.pin = None
        self.biometric_enabled = False
        self.daily_limit = 0.0
        self.monthly_limit = 0.0
        
        self.greeting_label = None
        self.categories_display_frame = None
        self.amount_var = None

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
        self.style = ttk.Style("darkly")
        
        # Sidebar
        sidebar = ttk.Frame(self.root, width=200, bootstyle="dark")
        sidebar.pack(side="left", fill="y")
        nav_buttons = [
            ("🏠 Home", self.switch_view),
            ("➕ Transactions", self.switch_view),
            ("📈 Reports", self.switch_view),
            ("⚙ Settings", self.switch_view)
        ]
        for text, cmd in nav_buttons:
            btn = ttk.Button(sidebar, text=text, bootstyle="primary", command=lambda x=text.split()[1]: cmd(x))
            btn.pack(fill="x", padx=10, pady=5)
            ToolTip(btn, text=f"Go to {text.split()[1]} view", bootstyle="inverse")

        # Header
        header = ttk.Frame(self.root, bootstyle="dark")
        header.pack(fill="x", pady=10)
        self.greeting_label = ttk.Label(header, text=f"Hello, {self.user_name}", font=("Segoe UI", 26, "bold"), bootstyle="light")
        self.greeting_label.pack(side="left", padx=20)
        self.balance_label = ttk.Label(header, text=f"Total Balance: ₹{self.current_balance}", font=("Segoe UI", 22, "bold"), bootstyle="success")
        self.balance_label.pack(side="left", padx=20)
        self.disposable_label = ttk.Label(header, text=f"Disposable Balance: ₹{self.get_disposable_balance()}", font=("Segoe UI", 22, "bold"), bootstyle="success")
        self.disposable_label.pack(side="left", padx=20)

        # Main content
        self.main_content = ttk.Frame(self.root)
        self.main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Home View
        self.home_frame = ttk.Frame(self.main_content, bootstyle="dark")
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        cat_frame = ttk.Labelframe(self.home_frame, text="📋 Set Regular Monthly Categories", padding=10, bootstyle="primary")
        cat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(1, weight=1)

        self.category_entries = []
        for i in range(5):
            row = ttk.Frame(cat_frame)
            row.grid(row=i, column=0, sticky="ew", pady=5)
            ttk.Label(row, text=f"Category {i+1}:", font=("Segoe UI", 16)).grid(row=0, column=0, padx=5)
            cat_entry = ttk.Entry(row, width=20, font=("Segoe UI", 16))
            cat_entry.grid(row=0, column=1, padx=5)
            ToolTip(cat_entry, text="Enter category name", bootstyle="inverse")
            ttk.Label(row, text="Amount:", font=("Segoe UI", 16)).grid(row=0, column=2, padx=5)
            amt_entry = ttk.Entry(row, width=10, font=("Segoe UI", 16))
            amt_entry.grid(row=0, column=3, padx=5)
            ToolTip(amt_entry, text="Enter expected amount in ₹", bootstyle="inverse")
            self.category_entries.append((cat_entry, amt_entry))

        save_cat_btn = ttk.Button(cat_frame, text="💾 Save Categories", command=self.save_categories, bootstyle="primary")
        save_cat_btn.grid(row=5, column=0, columnspan=4, pady=10)
        ToolTip(save_cat_btn, text="Save regular categories", bootstyle="inverse")

        self.categories_display_frame = ttk.Labelframe(self.home_frame, text="📋 Regular Categories", padding=10, bootstyle="primary")
        self.categories_display_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.update_categories_display()

        # Transactions View
        self.input_frame = ttk.Labelframe(self.main_content, text="➕ Add Transaction", padding=15, bootstyle="primary")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.credit_var = tk.BooleanVar()
        self.debit_var = tk.BooleanVar()
        ttk.Checkbutton(self.input_frame, text="Credit", variable=self.credit_var, bootstyle="success-round-toggle").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Checkbutton(self.input_frame, text="Debit", variable=self.debit_var, bootstyle="danger-round-toggle").grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self.input_frame, text="Category", font=("Segoe UI", 16)).grid(row=1, column=0, pady=10, sticky="w")
        self.category_entry = ttk.Combobox(self.input_frame, values=list(self.regular_categories.keys()), font=("Segoe UI", 16), bootstyle="dark")
        self.category_entry.grid(row=1, column=1, pady=10, sticky="w")
        ToolTip(self.category_entry, text="Select or enter a category", bootstyle="inverse")

        ttk.Label(self.input_frame, text="Amount", font=("Segoe UI", 16)).grid(row=2, column=0, pady=10, sticky="w")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(self.input_frame, textvariable=self.amount_var, width=25, font=("Segoe UI", 16), bootstyle="dark")
        self.amount_entry.grid(row=2, column=1, pady=10, sticky="w")
        ToolTip(self.amount_entry, text="Enter amount in ₹", bootstyle="inverse")
        self.amount_var.trace("w", self.validate_amount)

        self.amount_entry.bind("<Return>", lambda event: self.save_transaction())
        self.category_entry.bind("<Return>", lambda event: self.amount_entry.focus_set())

        submit_btn = ttk.Button(self.input_frame, text="✅ Submit", command=self.save_transaction, bootstyle="primary")
        submit_btn.grid(row=3, column=0, columnspan=2, pady=15)
        ToolTip(submit_btn, text="Submit transaction", bootstyle="inverse")

        action_frame = ttk.Frame(self.input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=10)
        view_btn = ttk.Button(action_frame, text="📋 View History", command=self.view_history, bootstyle="secondary")
        view_btn.grid(row=0, column=0, padx=10)
        ToolTip(view_btn, text="View transaction history", bootstyle="inverse")
        export_btn = ttk.Button(action_frame, text="⬇ Export Data", command=self.export_data, bootstyle="secondary")
        export_btn.grid(row=0, column=1, padx=10)
        ToolTip(export_btn, text="Export transactions to JSON", bootstyle="inverse")
        test_dialog_btn = ttk.Button(action_frame, text="🔔 Test Dialog", command=self.test_dialog, bootstyle="secondary")
        test_dialog_btn.grid(row=0, column=2, padx=10)
        ToolTip(test_dialog_btn, text="Test dialog functionality", bootstyle="inverse")

        # Reports View
        self.chart_frame = ttk.Labelframe(self.main_content, text="📈 Transaction Chart", padding=15, bootstyle="primary")
        self.chart_frame.grid(row=0, column=0, sticky="nsew")

        # Transaction History (Lower Half, Left Side)
        self.lower_frame = ttk.Frame(self.root)
        self.lower_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.lower_frame.grid_columnconfigure(0, weight=1)
        self.lower_frame.grid_columnconfigure(1, weight=1)

        self.history_frame = ttk.Labelframe(self.lower_frame, text="🕒 Transaction History", padding=0, bootstyle="primary")
        self.history_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Create a canvas and scrollbars for the Treeview
        history_canvas = tk.Canvas(self.history_frame, height=200, bg="#1e293b", highlightthickness=0)
        history_canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        v_scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=history_canvas.yview)
        v_scrollbar.pack(side="right", fill="y", padx=0, pady=0)
        
        h_scrollbar = ttk.Scrollbar(self.history_frame, orient="horizontal", command=history_canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x", padx=0, pady=0)

        history_inner_frame = ttk.Frame(history_canvas)
        history_canvas.create_window((0, 0), window=history_inner_frame, anchor="nw")

        self.history_list = ttk.Treeview(history_inner_frame, columns=("Date", "Type", "Category", "Amount"), show="headings", bootstyle="dark")
        self.history_list.heading("Date", text="Date", anchor="center")
        self.history_list.heading("Type", text="Type", anchor="center")
        self.history_list.heading("Category", text="Category", anchor="center")
        self.history_list.heading("Amount", text="Amount", anchor="center")
        self.history_list.column("Date", width=200, anchor="center")
        self.history_list.column("Type", width=100, anchor="center")
        self.history_list.column("Category", width=150, anchor="center")
        self.history_list.column("Amount", width=100, anchor="center")
        self.history_list.pack(fill="both", expand=True, padx=0, pady=0)

        history_inner_frame.bind("<Configure>", lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))
        history_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Settings View
        self.settings_frame = ttk.Frame(self.main_content, bootstyle="dark")
        self.settings_frame.grid(row=0, column=0, sticky="nsew")

        account_frame = ttk.Labelframe(self.settings_frame, text="👤 Account Management", padding=10, bootstyle="primary")
        account_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ttk.Label(account_frame, text="User Name:", font=("Segoe UI", 16)).pack(side="left", padx=5)
        self.name_entry = ttk.Entry(account_frame, width=20, font=("Segoe UI", 16), bootstyle="dark")
        self.name_entry.insert(0, self.user_name)
        self.name_entry.pack(side="left", padx=5)
        ToolTip(self.name_entry, text="Enter your name", bootstyle="inverse")
        update_name_btn = ttk.Button(account_frame, text="Update Name", command=self.update_name, bootstyle="primary")
        update_name_btn.pack(side="left", padx=5)
        ToolTip(update_name_btn, text="Update user name", bootstyle="inverse")

        security_frame = ttk.Labelframe(self.settings_frame, text="🔒 Security Settings", padding=10, bootstyle="primary")
        security_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        ttk.Label(security_frame, text="Set PIN:", font=("Segoe UI", 16)).pack(side="left", padx=5)
        self.pin_entry = ttk.Entry(security_frame, width=10, show="*", font=("Segoe UI", 16), bootstyle="dark")
        self.pin_entry.insert(0, self.pin if self.pin else "")
        self.pin_entry.pack(side="left", padx=5)
        ToolTip(self.pin_entry, text="Enter a 4+ digit PIN", bootstyle="inverse")
        update_pin_btn = ttk.Button(security_frame, text="Update PIN", command=self.update_pin, bootstyle="primary")
        update_pin_btn.pack(side="left", padx=5)
        ToolTip(update_pin_btn, text="Update PIN", bootstyle="inverse")
        self.biometric_var = tk.BooleanVar(value=self.biometric_enabled)
        biometric_check = ttk.Checkbutton(security_frame, text="Enable Biometric", variable=self.biometric_var, bootstyle="primary-round-toggle")
        biometric_check.pack(side="left", padx=5)
        ToolTip(biometric_check, text="Enable biometric authentication", bootstyle="inverse")

        limits_frame = ttk.Labelframe(self.settings_frame, text="💸 Transaction Limits", padding=10, bootstyle="primary")
        limits_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        ttk.Label(limits_frame, text="Daily Limit (₹):", font=("Segoe UI", 16)).pack(side="left", padx=5)
        self.daily_limit_entry = ttk.Entry(limits_frame, width=10, font=("Segoe UI", 16), bootstyle="dark")
        self.daily_limit_entry.insert(0, str(self.daily_limit))
        self.daily_limit_entry.pack(side="left", padx=5)
        ToolTip(self.daily_limit_entry, text="Enter daily transaction limit", bootstyle="inverse")
        ttk.Label(limits_frame, text="Monthly Limit (₹):", font=("Segoe UI", 16)).pack(side="left", padx=5)
        self.monthly_limit_entry = ttk.Entry(limits_frame, width=10, font=("Segoe UI", 16), bootstyle="dark")
        self.monthly_limit_entry.insert(0, str(self.monthly_limit))
        self.monthly_limit_entry.pack(side="left", padx=5)
        ToolTip(self.monthly_limit_entry, text="Enter monthly transaction limit", bootstyle="inverse")
        update_limits_btn = ttk.Button(limits_frame, text="Update Limits", command=self.update_limits, bootstyle="primary")
        update_limits_btn.pack(side="left", padx=5)
        ToolTip(update_limits_btn, text="Update transaction limits", bootstyle="inverse")

        self.update_graph()
        self.update_balance_labels()
        self.switch_view("Home")

    def validate_amount(self, *args):
        value = self.amount_var.get()
        try:
            if value:
                amount = float(value)
                if amount < 0:
                    self.amount_entry.configure(bootstyle="danger")
                    ToolTip(self.amount_entry, text="Amount cannot be negative", bootstyle="danger")
                else:
                    self.amount_entry.configure(bootstyle="dark")
                    ToolTip(self.amount_entry, text="Enter amount in ₹", bootstyle="inverse")
            else:
                self.amount_entry.configure(bootstyle="dark")
                ToolTip(self.amount_entry, text="Enter amount in ₹", bootstyle="inverse")
        except ValueError:
            self.amount_entry.configure(bootstyle="danger")
            ToolTip(self.amount_entry, text="Enter a valid number", bootstyle="danger")

    def test_dialog(self):
        try:
            response = messagebox.askyesno("Test Dialog", "This is a test dialog. Do you want to continue?", bootstyle="warning")
            print(f"Test dialog response: {response}")
            if response:
                messagebox.showinfo("Test Result", "You clicked Yes!", bootstyle="success")
            else:
                messagebox.showinfo("Test Result", "You clicked No!", bootstyle="info")
        except Exception as e:
            print(f"Error in test_dialog: {e}")
            messagebox.showerror("Error", "Failed to display test dialog.", bootstyle="danger")

    def save_categories(self):
        updated_categories = self.regular_categories.copy()
        valid_entries = False
        for cat_entry, amt_entry in self.category_entries:
            category = cat_entry.get().strip()
            amount_str = amt_entry.get().strip()
            if category and amount_str:
                try:
                    amount = float(amount_str)
                    if amount >= 0:
                        updated_categories[category] = amount
                        valid_entries = True
                    else:
                        messagebox.showerror("Error", f"Amount for '{category}' must be non-negative.", bootstyle="danger")
                        return
                except ValueError:
                    messagebox.showerror("Error", f"Invalid amount for category '{category}'. Please enter a number.", bootstyle="danger")
                    return
        if not valid_entries:
            messagebox.showerror("Error", "Please enter at least one valid category and amount.", bootstyle="danger")
            return
        
        self.regular_categories = updated_categories
        with open("regular_categories.json", "w") as f:
            json.dump(self.regular_categories, f)
        self.update_balance_labels()
        self.update_categories_display()
        self.category_entry.configure(values=list(self.regular_categories.keys()))
        for cat_entry, amt_entry in self.category_entries:
            cat_entry.delete(0, tk.END)
            amt_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Categories saved successfully!", bootstyle="success")

    def update_categories_display(self):
        for widget in self.categories_display_frame.winfo_children():
            widget.destroy()
        for category, amount in self.regular_categories.items():
            row = ttk.Frame(self.categories_display_frame)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=f"{category}:", font=("Segoe UI", 16)).pack(side="left")
            ttk.Label(row, text=f"₹{amount}", font=("Segoe UI", 16), bootstyle="success").pack(side="left", padx=10)

    def switch_view(self, view_name):
        self.home_frame.grid_remove()
        self.input_frame.grid_remove()
        self.chart_frame.grid_remove()
        self.settings_frame.grid_remove()
        if view_name == "Home":
            self.home_frame.grid(row=0, column=0, sticky="nsew")
        elif view_name == "Transactions":
            self.input_frame.grid(row=0, column=0, sticky="nsew")
            self.category_entry.configure(values=list(self.regular_categories.keys()))
        elif view_name == "Reports":
            self.chart_frame.grid(row=0, column=0, sticky="nsew")
        elif view_name == "Settings":
            self.settings_frame.grid(row=0, column=0, sticky="nsew")

    def get_disposable_balance(self):
        expected_total = sum(self.regular_categories.values()) if self.regular_categories else 0
        return max(0, self.current_balance - expected_total)

    def update_balance_labels(self):
        self.balance_label.configure(text=f"Total Balance: ₹{self.current_balance}")
        self.disposable_label.configure(text=f"Disposable Balance: ₹{self.get_disposable_balance()}")

    def save_transaction(self):
        try:
            category = self.category_entry.get().strip()
            amount = float(self.amount_entry.get())
            trans_type = "Credit" if self.credit_var.get() else "Debit" if self.debit_var.get() else None

            print(f"Transaction attempt: Type={trans_type}, Category={category}, Amount={amount}")
            print(f"Current transaction history: {self.transaction_history}")

            if trans_type is None:
                messagebox.showerror("Error", "Please select either Credit or Debit", bootstyle="danger")
                return
            if trans_type == "Debit" and amount > self.current_balance:
                messagebox.showerror("Error", "Insufficient balance", bootstyle="danger")
                return

            today = datetime.now().strftime("%Y-%m-%d")
            daily_debit_total = sum(t["amount"] for t in self.transaction_history if t["type"] == "Debit" and t["date"].startswith(today))
            print(f"Daily debit total: {daily_debit_total}, New amount: {amount}, Total with new: {daily_debit_total + amount}")

            # Hardcoded daily limit check of ₹5000
            if trans_type == "Debit" and (daily_debit_total + amount) > 5000:
                print("Daily limit of ₹5000 exceeded - showing dialog")
                try:
                    response = messagebox.askyesno("Daily Limit Exceeded",
                        f"Transaction of ₹{amount} exceeds ₹5000 daily limit. "
                        f"Current spending: ₹{daily_debit_total}. Proceed?", bootstyle="warning")
                    print(f"Dialog response: {response}")
                    if not response:
                        messagebox.showinfo("Cancelled", "Transaction cancelled due to daily limit.", bootstyle="info")
                        print("Transaction aborted")
                        return
                    else:
                        print("Transaction approved")
                except Exception as e:
                    print(f"Error showing dialog: {e}")
                    messagebox.showerror("Error", "Failed to show limit dialog. Transaction aborted.", bootstyle="danger")
                    return

            monthly_total = sum(t["amount"] for t in self.transaction_history if t["type"] == "Debit" and t["date"].startswith(datetime.now().strftime("%Y-%m")))
            print(f"Monthly debit total: {monthly_total}, New amount: {amount}, Total with new: {monthly_total + amount}")
            if trans_type == "Debit" and self.monthly_limit > 0 and (monthly_total + amount) > self.monthly_limit:
                messagebox.showerror("Error", f"Transaction exceeds monthly limit of ₹{self.monthly_limit}", bootstyle="danger")
                print("Transaction aborted due to monthly limit")
                return

            print("Proceeding with transaction")
            self.add_transaction(category, amount, trans_type)
            self.category_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.credit_var.set(False)
            self.debit_var.set(False)
            self.category_entry.focus_set()
            messagebox.showinfo("Success", f"{trans_type} transaction of ₹{amount} for {category} added!", bootstyle="success")
            print("Transaction added")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount", bootstyle="danger")
            print("Invalid amount entered")

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
        self.history_list.insert("", "end", values=(date_time, transaction_type, category, f"₹{amount}"))
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
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def check_balance_warning(self):
        if self.current_balance < 2000:
            messagebox.showwarning("⚠ Low Balance", "Your balance is below ₹2000!", bootstyle="warning")

    def view_history(self):
        for item in self.history_list.get_children():
            self.history_list.delete(item)
        for t in self.transaction_history:
            self.history_list.insert("", "end", values=(t["date"], t["type"], t["category"], f"₹{t['amount']}"))

    def export_data(self):
        with open("wallet_data.json", "w") as f:
            json.dump(self.transaction_history, f, indent=4)
        messagebox.showinfo("Exported", "Transaction history exported to wallet_data.json", bootstyle="success")

    def update_name(self):
        new_name = self.name_entry.get().strip()
        if new_name:
            self.user_name = new_name
            self.save_settings()
            self.root.title(f"My Wallet - Premium ({self.user_name})")
            self.greeting_label.configure(text=f"Hello, {self.user_name}")
            messagebox.showinfo("Success", "User name updated successfully!", bootstyle="success")
        else:
            messagebox.showerror("Error", "Please enter a valid name.", bootstyle="danger")

    def update_pin(self):
        new_pin = self.pin_entry.get().strip()
        if new_pin and new_pin.isdigit() and len(new_pin) >= 4:
            self.pin = new_pin
            self.save_settings()
            messagebox.showinfo("Success", "PIN updated successfully!", bootstyle="success")
        else:
            messagebox.showerror("Error", "Please enter a valid PIN (at least 4 digits).", bootstyle="danger")

    def update_limits(self):
        try:
            daily_limit = float(self.daily_limit_entry.get())
            monthly_limit = float(self.monthly_limit_entry.get())
            if daily_limit >= 0 and monthly_limit >= 0:
                self.daily_limit = daily_limit
                self.monthly_limit = monthly_limit
                self.save_settings()
                messagebox.showinfo("Success", "Transaction limits updated successfully!", bootstyle="success")
            else:
                messagebox.showerror("Error", "Limits must be non-negative.", bootstyle="danger")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for limits.", bootstyle="danger")

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

if __name__ == "__main__":
    root = ttk.Window(themename="default")
    app = WalletApp(root)
    root.mainloop()


