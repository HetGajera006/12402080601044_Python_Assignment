
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=input("Enter MySQL password: "),
        database="college"
    )


def create_table():
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Contact (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20),
            category VARCHAR(50),
            notes TEXT
        )
    """)
    connection.commit()
    cursor.close()


def valid_email(email):
    pattern = r"^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(com|edu|org)$"
    return re.fullmatch(pattern, email, re.IGNORECASE) is not None


def clear_fields():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    category_combo.set("")
    notes_text.delete("1.0", tk.END)


def add_contact():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    category = category_combo.get().strip()
    notes = notes_text.get("1.0", tk.END).strip()

    if not name or not email:
        messagebox.showerror("Error", "Name and email are required.")
        return

    if not valid_email(email):
        messagebox.showerror("Error", "Enter a valid email address.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Contact (name, email, phone, category, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, phone, category, notes))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Success", "Contact added successfully.")
        clear_fields()
        show_contacts()
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Email already exists.")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))


def update_contact():
    contact_id = id_entry.get().strip()

    if not contact_id.isdigit():
        messagebox.showerror("Error", "Enter a valid contact ID.")
        return

    name = name_entry.get().strip()
    email = email_entry.get().strip()

    if not name or not valid_email(email):
        messagebox.showerror("Error", "Enter valid name and email.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE Contact
            SET name=%s, email=%s, phone=%s, category=%s, notes=%s
            WHERE id=%s
        """, (
            name,
            email,
            phone_entry.get().strip(),
            category_combo.get().strip(),
            notes_text.get("1.0", tk.END).strip(),
            int(contact_id)
        ))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Success", "Contact updated.")
        show_contacts()
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Email already exists.")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))


def delete_contact():
    contact_id = id_entry.get().strip()

    if not contact_id.isdigit():
        messagebox.showerror("Error", "Enter a valid contact ID.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM Contact WHERE id=%s",
            (int(contact_id),)
        )
        connection.commit()
        cursor.close()
        messagebox.showinfo("Success", "Delete operation completed.")
        clear_fields()
        show_contacts()
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))


def search_contacts():
    keyword = search_entry.get().strip()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, email, phone, category, notes
            FROM Contact
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

        display_rows(cursor.fetchall())
        cursor.close()
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))


def display_rows(rows):
    for item in contact_table.get_children():
        contact_table.delete(item)

    for row in rows:
        contact_table.insert("", tk.END, values=row)


def show_contacts():
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, email, phone, category, notes
            FROM Contact
            ORDER BY name
        """)
        display_rows(cursor.fetchall())
        cursor.close()
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))


def load_selected(event):
    selected = contact_table.selection()

    if not selected:
        return

    values = contact_table.item(selected[0], "values")
    clear_fields()

    id_entry.insert(0, values[0])
    name_entry.insert(0, values[1])
    email_entry.insert(0, values[2])
    phone_entry.insert(0, values[3] or "")
    category_combo.set(values[4] or "")
    notes_text.insert("1.0", values[5] or "")


# Connect to the database.
try:
    connection = connect_db()
    create_table()
except mysql.connector.Error as error:
    print("Database connection failed:", error)
    raise SystemExit(1)


# Create GUI.
root = tk.Tk()
root.title("Contact Manager")
root.geometry("1000x650")

form = ttk.Frame(root, padding=10)
form.pack(fill="x")

ttk.Label(form, text="Contact ID").grid(row=0, column=0, sticky="w")
id_entry = ttk.Entry(form)
id_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form, text="Name").grid(row=1, column=0, sticky="w")
name_entry = ttk.Entry(form)
name_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(form, text="Email").grid(row=2, column=0, sticky="w")
email_entry = ttk.Entry(form)
email_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(form, text="Phone").grid(row=3, column=0, sticky="w")
phone_entry = ttk.Entry(form)
phone_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(form, text="Category").grid(row=4, column=0, sticky="w")
category_combo = ttk.Combobox(
    form, values=["Family", "Friend", "Faculty", "Work", "Other"]
)
category_combo.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(form, text="Notes").grid(row=5, column=0, sticky="nw")
notes_text = tk.Text(form, height=3, width=25)
notes_text.grid(row=5, column=1, padx=5, pady=5)

buttons = ttk.Frame(form)
buttons.grid(row=6, column=0, columnspan=2, pady=8)

ttk.Button(buttons, text="Add", command=add_contact).pack(side="left", padx=3)
ttk.Button(buttons, text="Update", command=update_contact).pack(side="left", padx=3)
ttk.Button(buttons, text="Delete", command=delete_contact).pack(side="left", padx=3)
ttk.Button(buttons, text="Clear", command=clear_fields).pack(side="left", padx=3)

search_frame = ttk.Frame(root, padding=10)
search_frame.pack(fill="x")

ttk.Label(search_frame, text="Search by name/email/phone:").pack(side="left")
search_entry = ttk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)
ttk.Button(search_frame, text="Search", command=search_contacts).pack(side="left")
ttk.Button(search_frame, text="Show All", command=show_contacts).pack(side="left", padx=5)

columns = ("ID", "Name", "Email", "Phone", "Category", "Notes")
contact_table = ttk.Treeview(root, columns=columns, show="headings")

for column in columns:
    contact_table.heading(column, text=column)
    contact_table.column(column, width=140)

contact_table.pack(fill="both", expand=True, padx=10, pady=10)
contact_table.bind("<<TreeviewSelect>>", load_selected)

show_contacts()


def close_app():
    connection.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
