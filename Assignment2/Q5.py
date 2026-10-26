import getpass
import re
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector
from mysql.connector import Error, errorcode

EMAIL_RE = re.compile(r"^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{10,13}$")
CATEGORIES = ["Faculty", "Student", "Friend", "Family", "Work", "Other"]
SORT_COLUMNS = {"name": "name", "email": "email", "category": "category"}

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS Contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    category VARCHAR(30),
    notes TEXT,
    INDEX idx_name (name),
    INDEX idx_phone (phone)
)"""


class ContactApp:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.rows = []
        self.selected_id = None
        root.title("Contact Manager")

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name")
        self.prefix_var = tk.IntVar(value=0)

        self.build_menu()
        self.build_form()
        self.build_list()
        self.refresh()

    def build_menu(self):
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Refresh", command=self.refresh)
        file_menu.add_command(label="Clear form", command=self.clear_form)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    def build_form(self):
        frm = ttk.LabelFrame(self.root, text="Contact")
        frm.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ttk.Label(frm, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=2)
        ttk.Label(frm, text="Email").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.email_var, width=30).grid(row=1, column=1, pady=2)
        ttk.Label(frm, text="Phone").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.phone_var, width=30).grid(row=2, column=1, pady=2)
        ttk.Label(frm, text="Category").grid(row=3, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.cat_var, values=CATEGORIES, state="readonly", width=27).grid(
            row=3, column=1, pady=2
        )
        ttk.Label(frm, text="Notes").grid(row=4, column=0, sticky="nw")
        self.notes = tk.Text(frm, width=30, height=5)
        self.notes.grid(row=4, column=1, pady=2)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=6)
        ttk.Button(btns, text="Add", command=self.add).pack(side="left", padx=3)
        ttk.Button(btns, text="Update", command=self.update).pack(side="left", padx=3)
        ttk.Button(btns, text="Delete", command=self.delete).pack(side="left", padx=3)
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side="left", padx=3)

    def build_list(self):
        frm = ttk.LabelFrame(self.root, text="Search and list")
        frm.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        top = ttk.Frame(frm)
        top.pack(fill="x")
        ttk.Label(top, text="Search").pack(side="left")
        entry = ttk.Entry(top, textvariable=self.search_var, width=25)
        entry.pack(side="left", padx=4)
        entry.bind("<Return>", lambda e: self.refresh())
        ttk.Button(top, text="Go", command=self.refresh).pack(side="left")
        ttk.Checkbutton(top, text="Prefix only", variable=self.prefix_var).pack(side="left", padx=6)

        sort_row = ttk.Frame(frm)
        sort_row.pack(fill="x", pady=4)
        ttk.Label(sort_row, text="Sort by:").pack(side="left")
        for key in SORT_COLUMNS:
            ttk.Radiobutton(
                sort_row, text=key.title(), value=key, variable=self.sort_var, command=self.refresh
            ).pack(side="left", padx=4)

        box = ttk.Frame(frm)
        box.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(box, width=70, height=18)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(box, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def run(self, sql, params=(), fetch=False):
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()
            self.conn.commit()
            return None
        finally:
            cur.close()

    def read_form(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        category = self.cat_var.get()
        notes = self.notes.get("1.0", "end-1c").strip()
        if not name:
            raise ValueError("Name is required.")
        if not EMAIL_RE.match(email):
            raise ValueError("Invalid email address.")
        if phone and not PHONE_RE.match(phone):
            raise ValueError("Phone must be 10 to 13 digits (optional leading +).")
        return name, email, phone, category, notes

    def add(self):
        try:
            data = self.read_form()
            self.run(
                "INSERT INTO Contact (name, email, phone, category, notes) VALUES (%s, %s, %s, %s, %s)", data
            )
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return
        except Error as e:
            self.show_db_error(e)
            return
        messagebox.showinfo("Contact", "Record inserted.")
        self.clear_form()
        self.refresh()

    def update(self):
        if self.selected_id is None:
            messagebox.showwarning("Update", "Select a contact first.")
            return
        try:
            data = self.read_form()
            self.run(
                "UPDATE Contact SET name=%s, email=%s, phone=%s, category=%s, notes=%s WHERE id=%s",
                data + (self.selected_id,),
            )
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return
        except Error as e:
            self.show_db_error(e)
            return
        messagebox.showinfo("Contact", "Record updated.")
        self.refresh()

    def delete(self):
        if self.selected_id is None:
            messagebox.showwarning("Delete", "Select a contact first.")
            return
        if not messagebox.askyesno("Delete", "Delete this contact?"):
            return
        try:
            self.run("DELETE FROM Contact WHERE id=%s", (self.selected_id,))
        except Error as e:
            self.show_db_error(e)
            return
        self.clear_form()
        self.refresh()

    def show_db_error(self, e):
        if e.errno == errorcode.ER_DUP_ENTRY:
            messagebox.showerror("Duplicate", "A contact with this email already exists.")
        else:
            messagebox.showerror("Database error", str(e))

    def refresh(self):
        term = self.search_var.get().strip()
        order_col = SORT_COLUMNS[self.sort_var.get()]
        sql = "SELECT id, name, email, phone, category, notes FROM Contact"
        params = []
        if term:
            like = term + "%" if self.prefix_var.get() else "%" + term + "%"
            sql += " WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s"
            params = [like, like, like]
        sql += f" ORDER BY {order_col} LIMIT 1000"
        try:
            self.rows = self.run(sql, params, fetch=True)
        except Error as e:
            self.show_db_error(e)
            return
        self.listbox.delete(0, tk.END)
        for r in self.rows:
            self.listbox.insert(tk.END, f"{r[1]} | {r[2]} | {r[3] or '-'} | {r[4] or '-'}")

    def on_select(self, _event):
        sel = self.listbox.curselection()
        if not sel:
            return
        cid, name, email, phone, cat, notes = self.rows[sel[0]]
        self.selected_id = cid
        self.name_var.set(name)
        self.email_var.set(email)
        self.phone_var.set(phone or "")
        self.cat_var.set(cat or CATEGORIES[0])
        self.notes.delete("1.0", tk.END)
        self.notes.insert("1.0", notes or "")

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.cat_var.set(CATEGORIES[0])
        self.notes.delete("1.0", tk.END)


def main():
    host = input("Host [localhost]: ").strip() or "localhost"
    user = input("User: ").strip()
    password = getpass.getpass("Password: ")
    db = input("Database name: ").strip()
    if not re.fullmatch(r"\w+", db):
        print("Invalid database name.")
        return
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
        conn.database = db
        cur.execute(CREATE_TABLE)
        conn.commit()
        cur.close()
    except Error as e:
        print("Database error:", e)
        return
    root = tk.Tk()
    ContactApp(root, conn)
    root.mainloop()
    conn.close()


if __name__ == "__main__":
    main()
