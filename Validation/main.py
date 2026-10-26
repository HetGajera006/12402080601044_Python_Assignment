
import tkinter as tk
from tkinter import messagebox
from validation import validate_username, validate_email


def validate_details():
    username = username_entry.get().strip()
    email = email_entry.get().strip()

    if username == "" or email == "":
        messagebox.showwarning(
            "Warning",
            "Please enter both username and email."
        )
        return

    username_valid = validate_username(username)
    email_valid = validate_email(email)

    if username_valid:
        username_result.config(
            text="Valid Username",
            fg="green"
        )
    else:
        username_result.config(
            text="Invalid Username",
            fg="red"
        )

    if email_valid:
        email_result.config(
            text="Valid Email",
            fg="green"
        )
    else:
        email_result.config(
            text="Invalid Email",
            fg="red"
        )

    if username_valid and email_valid:
        messagebox.showinfo(
            "Success",
            "Username and Email are both valid!"
        )


def clear_fields():
    username_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    username_result.config(text="")
    email_result.config(text="")
    username_entry.focus()


root = tk.Tk()
root.title("Username and Email Validation System")
root.geometry("500x430")
root.resizable(False, False)
root.configure(bg="#f0f4f8")

title = tk.Label(
    root,
    text="Username and Email Validation",
    font=("Arial", 17, "bold"),
    bg="#f0f4f8",
    fg="#17365d"
)
title.pack(pady=20)

username_label = tk.Label(
    root,
    text="Enter Username:",
    font=("Arial", 12),
    bg="#f0f4f8"
)
username_label.pack()

username_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=30
)
username_entry.pack(pady=5)

username_result = tk.Label(
    root,
    text="",
    font=("Arial", 10, "bold"),
    bg="#f0f4f8"
)
username_result.pack(pady=3)

email_label = tk.Label(
    root,
    text="Enter Email:",
    font=("Arial", 12),
    bg="#f0f4f8"
)
email_label.pack(pady=(10, 0))

email_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=30
)
email_entry.pack(pady=5)

email_result = tk.Label(
    root,
    text="",
    font=("Arial", 10, "bold"),
    bg="#f0f4f8"
)
email_result.pack(pady=3)

validate_button = tk.Button(
    root,
    text="Validate",
    font=("Arial", 11, "bold"),
    bg="#1976d2",
    fg="white",
    width=15,
    command=validate_details
)
validate_button.pack(pady=15)

clear_button = tk.Button(
    root,
    text="Clear",
    font=("Arial", 11),
    width=15,
    command=clear_fields
)
clear_button.pack()

rules = tk.Label(
    root,
    text="Username: 3-20 characters, starts with a letter.\n"
         "Letters, numbers and underscores are allowed.\n"
         "Email must follow a basic valid email format.",
    font=("Arial", 9),
    bg="#f0f4f8",
    fg="#444444",
    justify="center"
)
rules.pack(pady=15)

username_entry.focus()

root.mainloop()
