import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from models import Hero, GuildManager


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Load config to fill the Settings tab later
        self.config_data = self.load_config_data()

        self.title("Guild Master - D2")
        self.geometry("900x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.create_hero_tab()
        self.create_report_tab()
        self.create_settings_tab()

    def load_config_data(self):
        # Helper to read raw JSON config safely
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def create_hero_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Heroes")

        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="New Hero", command=self.add_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Stats", command=self.edit_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Hero", command=self.delete_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Table", command=self.load_heroes).pack(side=tk.LEFT, padx=5)

        # Data table configuration
        cols = ('ID', 'Name', 'Level', 'Gold', 'Active')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

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
        # EDITABLE CONFIGURATION TAB
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")

        tk.Label(frame, text="Database Configuration (config.json)", font=("Arial", 12, "bold")).pack(pady=15)

        # Form fields
        self.entries = {}
        # Only DB connection fields
        fields = ["host", "user", "password", "database"]

        for field in fields:
            row = ttk.Frame(frame)
            row.pack(fill='x', padx=50, pady=5)
            tk.Label(row, text=f"{field.upper()}:", width=15, anchor='w').pack(side=tk.LEFT)

            entry = tk.Entry(row)
            # Fill with current config data
            entry.insert(0, str(self.config_data.get(field, "")))
            entry.pack(side=tk.LEFT, fill='x', expand=True)

            # Hide password characters
            if "password" in field:
                entry.config(show="*")

            self.entries[field] = entry

        # Save Button
        ttk.Button(frame, text="Save Configuration", command=self.save_config).pack(pady=20)
        tk.Label(frame, text="Note: Restart application after saving changes.", fg="red").pack()

    def save_config(self):
        # Saves new settings to config.json
        new_config = {field: entry.get() for field, entry in self.entries.items()}

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.json')

        try:
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved!\nPlease restart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def load_heroes(self):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            heroes = Hero.all()
            for h in heroes:
                self.tree.insert('', 'end', values=(h.id, h.name, h.level, h.gold_balance, h.is_active))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def get_selected_hero_id(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a hero first!")
            return None
        return self.tree.item(selected_item)['values'][0]

    def add_hero(self):
        popup = tk.Toplevel(self)
        popup.title("New Hero")
        popup.geometry("300x250")

        tk.Label(popup, text="Name:").pack(pady=5)
        entry_name = tk.Entry(popup)
        entry_name.pack(pady=5)

        tk.Label(popup, text="Level:").pack(pady=5)
        entry_level = tk.Entry(popup)
        entry_level.insert(0, "1")
        entry_level.pack(pady=5)

        tk.Label(popup, text="Gold:").pack(pady=5)
        entry_gold = tk.Entry(popup)
        entry_gold.insert(0, "100.0")
        entry_gold.pack(pady=5)

        def submit():
            name = entry_name.get()
            lvl = entry_level.get()
            gold = entry_gold.get()
            if name:
                try:
                    GuildManager.create_hero_with_starter_pack(name, 1, lvl, gold)
                    messagebox.showinfo("Success", "Hero created!")
                    popup.destroy()
                    self.load_heroes()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Create", command=submit).pack(pady=20)

    def delete_hero(self):
        hero_id = self.get_selected_hero_id()
        if hero_id:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this hero?")
            if confirm:
                try:
                    GuildManager.delete_hero(hero_id)
                    messagebox.showinfo("Deleted", "Hero deleted successfully.")
                    self.load_heroes()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def edit_hero(self):
        hero_id = self.get_selected_hero_id()
        if not hero_id:
            return

        selected_values = self.tree.item(self.tree.selection())['values']
        current_name = selected_values[1]
        current_level = selected_values[2]
        current_gold = selected_values[3]

        popup = tk.Toplevel(self)
        popup.title(f"Edit Hero: {current_name}")
        popup.geometry("300x200")

        tk.Label(popup, text="New Level:").pack(pady=5)
        entry_level = tk.Entry(popup)
        entry_level.insert(0, str(current_level))
        entry_level.pack(pady=5)

        tk.Label(popup, text="New Gold Balance:").pack(pady=5)
        entry_gold = tk.Entry(popup)
        entry_gold.insert(0, str(current_gold))
        entry_gold.pack(pady=5)

        def submit_update():
            try:
                GuildManager.update_hero_stats(hero_id, entry_level.get(), entry_gold.get())
                messagebox.showinfo("Success", "Hero updated!")
                popup.destroy()
                self.load_heroes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Save Changes", command=submit_update).pack(pady=20)

    def show_report(self):
        try:
            data = GuildManager.get_report()
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Name | Level | Items | Value\n" + "-" * 40 + "\n")
            for row in data:
                self.report_text.insert(tk.END,
                                        f"{row['name']} | {row['level']} | {row['item_count']} | {row['total_value']}\n")
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def import_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                c = GuildManager.import_items_from_json(content)
                messagebox.showinfo("Import", f"Imported {c} items.")
            except Exception as e:
                messagebox.showerror("Err", str(e))