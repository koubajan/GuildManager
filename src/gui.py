import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from models import Hero, Item, GuildManager


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.config_data = self.load_config_data()

        self.title("Guild Master - D2")
        self.geometry("950x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.create_hero_tab()
        self.create_items_tab()  # NEW TAB
        self.create_report_tab()
        self.create_settings_tab()

    def load_config_data(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    # --- HEROES TAB ---
    def create_hero_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Heroes")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="New Hero", command=self.add_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Manage Inventory", command=self.view_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Stats", command=self.edit_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Hero", command=self.delete_hero).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_heroes).pack(side=tk.LEFT, padx=5)

        cols = ('ID', 'Name', 'Level', 'Gold', 'Active')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill='both', expand=True)
        self.load_heroes()

    # --- ITEMS TAB (NEW) ---
    def create_items_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Items DB")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="New Item", command=self.add_item_to_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Item", command=self.edit_item_in_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Item", command=self.delete_item_from_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_items).pack(side=tk.LEFT, padx=5)

        cols = ('ID', 'Name', 'Rarity', 'Value')
        self.item_tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.item_tree.heading(col, text=col)
            self.item_tree.column(col, width=150)

        self.item_tree.pack(fill='both', expand=True)
        self.load_items()

    # --- REPORT TAB ---
    def create_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Report & Import")

        ttk.Label(frame, text="Guild Report", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(frame, text="Generate Report", command=self.show_report).pack(pady=5)

        self.report_text = tk.Text(frame, height=15)
        self.report_text.pack(fill='x', padx=10)

        import_frame = ttk.LabelFrame(frame, text="Data Import Zone")
        import_frame.pack(fill='x', padx=10, pady=20)

        i_frame = ttk.Frame(import_frame)
        i_frame.pack(fill='x', pady=5)
        ttk.Button(i_frame, text="Import Items (JSON)", command=self.import_json_items).pack(side=tk.LEFT, padx=10)
        ttk.Label(i_frame, text="Adds new weapons/potions to the game database.").pack(side=tk.LEFT)

        h_frame = ttk.Frame(import_frame)
        h_frame.pack(fill='x', pady=5)
        ttk.Button(h_frame, text="Import Heroes (JSON)", command=self.import_json_heroes).pack(side=tk.LEFT, padx=10)
        ttk.Label(h_frame, text="Adds new heroes to the roster.").pack(side=tk.LEFT)

    # --- SETTINGS TAB ---
    def create_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")

        tk.Label(frame, text="Database Configuration (config.json)", font=("Arial", 12, "bold")).pack(pady=15)

        self.entries = {}
        fields = ["host", "user", "password", "database"]

        for field in fields:
            row = ttk.Frame(frame)
            row.pack(fill='x', padx=50, pady=5)
            tk.Label(row, text=f"{field.upper()}:", width=15, anchor='w').pack(side=tk.LEFT)

            entry = tk.Entry(row)
            entry.insert(0, str(self.config_data.get(field, "")))
            entry.pack(side=tk.LEFT, fill='x', expand=True)
            if "password" in field:
                entry.config(show="*")
            self.entries[field] = entry

        ttk.Button(frame, text="Save Configuration", command=self.save_config).pack(pady=20)
        tk.Label(frame, text="Note: Restart application after saving changes.", fg="red").pack()

    # --- LOGIC & ACTIONS ---

    def save_config(self):
        new_config = {field: entry.get() for field, entry in self.entries.items()}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved!\nPlease restart.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_heroes(self):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            heroes = Hero.all()
            for h in heroes:
                self.tree.insert('', 'end', values=(h.id, h.name, h.level, h.gold_balance, h.is_active))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def load_items(self):
        try:
            for i in self.item_tree.get_children():
                self.item_tree.delete(i)
            items = Item.all()
            for item in items:
                self.item_tree.insert('', 'end', values=(item.id, item.name, item.rarity, item.value))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def add_hero(self):
        # Enhanced hero creation with Starter Item Dropdown
        popup = tk.Toplevel(self)
        popup.title("New Hero")
        popup.geometry("350x350")

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

        # Starter Item Selection
        tk.Label(popup, text="Starter Item:").pack(pady=5)

        # Load available items for the dropdown
        try:
            all_items = Item.all()
            item_options = [f"{i.id}: {i.name} ({i.rarity})" for i in all_items]
        except:
            item_options = []

        combo_items = ttk.Combobox(popup, values=item_options, state="readonly")
        combo_items.pack(pady=5)

        def submit():
            name = entry_name.get()
            lvl = entry_level.get()
            gold = entry_gold.get()

            # Parse selected item ID
            selected_str = combo_items.get()
            item_id = None
            if selected_str:
                item_id = int(selected_str.split(":")[0])

            if name:
                try:
                    GuildManager.create_hero_with_starter_pack(name, 1, lvl, gold, item_id)
                    messagebox.showinfo("Success", "Hero created!")
                    popup.destroy()
                    self.load_heroes()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Create", command=submit).pack(pady=20)

    def view_inventory(self):
        # Enhanced Inventory Manager
        hero_id = self.get_selected_id(self.tree)
        if not hero_id: return

        hero_name = self.tree.item(self.tree.selection())['values'][1]

        popup = tk.Toplevel(self)
        popup.title(f"Inventory: {hero_name}")
        popup.geometry("500x400")

        # Inventory Table
        cols = ('InvID', 'Name', 'Rarity', 'Value')
        inv_tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            inv_tree.heading(c, text=c)
            inv_tree.column(c, width=80)
        inv_tree.pack(fill='both', expand=True, pady=10)

        def refresh_inv():
            for i in inv_tree.get_children(): inv_tree.delete(i)
            items = GuildManager.get_hero_inventory(hero_id)
            for i in items:
                inv_tree.insert('', 'end', values=(i['inv_id'], i['name'], i['rarity'], i['value']))

        refresh_inv()

        # Action Buttons
        ctrl_frame = ttk.Frame(popup)
        ctrl_frame.pack(pady=10)

        # Dropdown to add new item
        try:
            all_items = Item.all()
            item_opts = [f"{i.id}: {i.name}" for i in all_items]
        except:
            item_opts = []

        combo_add = ttk.Combobox(ctrl_frame, values=item_opts, state="readonly", width=20)
        combo_add.pack(side=tk.LEFT, padx=5)

        def add_item():
            sel = combo_add.get()
            if sel:
                i_id = int(sel.split(":")[0])
                try:
                    GuildManager.add_item_to_inventory(hero_id, i_id)
                    refresh_inv()
                    self.show_report()  # update report in background
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(ctrl_frame, text="Add Item", command=add_item).pack(side=tk.LEFT, padx=5)

        def remove_item():
            sel_item = inv_tree.selection()
            if not sel_item: return
            inv_id = inv_tree.item(sel_item)['values'][0]  # Get InvID
            try:
                GuildManager.remove_item_from_inventory(inv_id)
                refresh_inv()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(ctrl_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=20)

    # --- CRUD FOR ITEMS DB ---
    def add_item_to_db(self):
        name = simpledialog.askstring("New Item", "Item Name:")
        if name:
            try:
                GuildManager.create_item(name, "Common", 10.0)
                self.load_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_item_in_db(self):
        item_id = self.get_selected_id(self.item_tree)
        if not item_id: return

        vals = self.item_tree.item(self.item_tree.selection())['values']

        popup = tk.Toplevel(self)
        popup.title("Edit Item")

        tk.Label(popup, text="Name:").pack()
        e_name = tk.Entry(popup);
        e_name.insert(0, vals[1]);
        e_name.pack()

        tk.Label(popup, text="Rarity:").pack()
        e_rar = ttk.Combobox(popup, values=["Common", "Rare", "Epic", "Legendary"]);
        e_rar.set(vals[2]);
        e_rar.pack()

        tk.Label(popup, text="Value:").pack()
        e_val = tk.Entry(popup);
        e_val.insert(0, vals[3]);
        e_val.pack()

        def save():
            try:
                GuildManager.update_item(item_id, e_name.get(), e_rar.get(), e_val.get())
                popup.destroy()
                self.load_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Save", command=save).pack(pady=10)

    def delete_item_from_db(self):
        item_id = self.get_selected_id(self.item_tree)
        if item_id:
            if messagebox.askyesno("Confirm", "Delete this item from the shop?"):
                try:
                    GuildManager.delete_item(item_id)
                    self.load_items()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    # --- HELPERS ---
    def get_selected_id(self, tree_widget):
        sel = tree_widget.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a row first.")
            return None
        return tree_widget.item(sel)['values'][0]

    def delete_hero(self):
        hero_id = self.get_selected_id(self.tree)
        if hero_id and messagebox.askyesno("Confirm", "Delete hero?"):
            try:
                GuildManager.delete_hero(hero_id)
                self.load_heroes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_hero(self):
        hero_id = self.get_selected_id(self.tree)
        if not hero_id: return
        vals = self.tree.item(self.tree.selection())['values']

        popup = tk.Toplevel(self)
        popup.title("Edit Stats")
        tk.Label(popup, text="Level:").pack();
        el = tk.Entry(popup);
        el.insert(0, vals[2]);
        el.pack()
        tk.Label(popup, text="Gold:").pack();
        eg = tk.Entry(popup);
        eg.insert(0, vals[3]);
        eg.pack()

        def save():
            GuildManager.update_hero_stats(hero_id, el.get(), eg.get())
            popup.destroy()
            self.load_heroes()

        tk.Button(popup, text="Save", command=save).pack(pady=10)

    def show_report(self):
        try:
            data = GuildManager.get_report()
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Name | Level | Gold | Items | Items Value\n" + "-" * 55 + "\n")
            for row in data:
                val = row['items_value'] if row['items_value'] is not None else 0.0
                self.report_text.insert(tk.END,
                                        f"{row['name']} | {row['level']} | {row['gold_balance']} | {row['item_count']} | {val}\n")

            stats = GuildManager.get_guild_stats()
            self.report_text.insert(tk.END, "\n" + "=" * 55 + "\nGUILD TOTAL STATISTICS\n")
            self.report_text.insert(tk.END, f"Total Guild Items Value: {stats['guild_item_value']}\n")
            self.report_text.insert(tk.END, f"Average Hero Level:      {stats['avg_level']:.1f}\n")
            self.report_text.insert(tk.END, f"Average Gold per Hero:   {stats['avg_gold']:.1f}\n")
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def import_json_items(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f: c = GuildManager.import_items_from_json(f.read())
            messagebox.showinfo("Import", f"Imported {c} items.");
            self.load_items()

    def import_json_heroes(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'r') as f: c = GuildManager.import_heroes_from_json(f.read())
            messagebox.showinfo("Import", f"Imported {c} heroes.");
            self.load_heroes()