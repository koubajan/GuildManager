import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models import Hero, GuildManager

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guild Master - D2")
        self.geometry("800x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.create_hero_tab()
        self.create_report_tab()
        self.create_settings_tab()

    def create_hero_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Heroes")

        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="New Hero (Transaction)", command=self.add_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Renew Data", command=self.load_heroes).pack(side=tk.LEFT, padx=5)

        # Data table
        cols = ('ID', 'Name', 'Level', 'Gold', 'Active')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        self.load_heroes()

    def create_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Report & Import")

        ttk.Button(frame, text="Generate Report", command=self.show_report).pack(pady=10)
        self.report_text = tk.Text(frame, height=15)
        self.report_text.pack(fill='x', padx=10)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(frame, text="Import sample item JSON", command=self.import_json).pack(pady=10)

    def create_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Info")
        ttk.Label(frame, text="Config file: config.json located in root folder.").pack(pady=20)

    def load_heroes(self):
        # Loads heroes from DB to table
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            heroes = Hero.all()
            for h in heroes:
                self.tree.insert('', 'end', values=(h.id, h.name, h.level, h.gold_balance, h.is_active))
        except Exception as e:
            messagebox.showerror("DB err:", str(e))

    def add_hero(self):
        # Custom window for inputting Name, Level, and Gold
        popup = tk.Toplevel(self)
        popup.title("New Hero Details")
        popup.geometry("300x250")

        # 1. Name Input
        tk.Label(popup, text="Hero Name:").pack(pady=5)
        entry_name = tk.Entry(popup)
        entry_name.pack(pady=5)

        # 2. Level Input
        tk.Label(popup, text="Level (1-100):").pack(pady=5)
        entry_level = tk.Entry(popup)
        entry_level.insert(0, "1") # Default value
        entry_level.pack(pady=5)

        # 3. Gold Input
        tk.Label(popup, text="Starting Gold:").pack(pady=5)
        entry_gold = tk.Entry(popup)
        entry_gold.insert(0, "100.0") # Default value
        entry_gold.pack(pady=5)

        # Save Function
        def submit():
            name = entry_name.get()
            level = entry_level.get()
            gold = entry_gold.get()

            if name:
                try:
                    # Calls the updated model method with 4 arguments
                    GuildManager.create_hero_with_starter_pack(name, 1, level, gold)
                    messagebox.showinfo("OK", "Hero created successfully!")
                    popup.destroy() # Close popup
                    self.load_heroes() # Refresh table
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showwarning("Warning", "Name is required!")

        # Confirm Button
        tk.Button(popup, text="Create Hero", command=submit).pack(pady=20)

    def show_report(self):
        # Displays aggregated report
        try:
            data = GuildManager.get_report()
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Name | Level | Number of Items | Value\n" + "-" * 40 + "\n")
            for row in data:
                self.report_text.insert(tk.END,
                                        f"{row['name']} | {row['level']} | {row['item_count']} | {row['total_value']}\n")
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def import_json(self):
        # Imports items from file
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                c = GuildManager.import_items_from_json(content)
                messagebox.showinfo("Import", f"Imported {c} items.")
            except Exception as e:
                messagebox.showerror("Err", str(e))