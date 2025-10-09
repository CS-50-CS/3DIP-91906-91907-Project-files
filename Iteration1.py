# Import required modules for GUI, file handling, and JSON
import tkinter as tk
from tkinter import messagebox
import os
import json

# Path to the JSON file storing user passwords
PASSWORDS_FILE = os.path.join(os.path.dirname(__file__), "passwords.json")


# Represents a single user with username and password
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self, password):
        """Check if the provided password matches the user's password."""
        return self.password == password


# Manages loading, saving, and accessing users from the password file
class UserManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.users = self.load_users()

    def load_users(self):
        """Load users from the JSON file. Returns a dict of username: User."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                # Create User objects for each entry
                return {u: User(u, p) for u, p in data.items()}
            except Exception:
                # If file is corrupt or unreadable, return empty dict
                return {}
        return {}

    def save_users(self):
        """Save all users to the JSON file."""
        data = {u: user.password for u, user in self.users.items()}
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add_user(self, username, password):
        """Add a new user and save to file."""
        self.users[username] = User(username, password)
        self.save_users()

    def get_user(self, username):
        """Retrieve a User object by username."""
        return self.users.get(username)


# Main login window for user authentication and registration
class LoginWindow(tk.Tk):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.title("Login")
        self.geometry("400x300")
        self.configure(bg="white")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        """Create and layout all widgets for the login window."""
        tk.Label(self, text="Login", font=("Arial", 32, "bold"), bg="white").pack(pady=30)

        # Username entry with placeholder
        self.user_entry = tk.Entry(self, font=("Arial", 18), bd=1, fg="grey")
        self.user_entry.pack(pady=10)
        self.user_entry.insert(0, "Username")
        self.user_entry.bind("<FocusIn>", self._clear_user_placeholder)
        self.user_entry.bind("<FocusOut>", self._add_user_placeholder)


    # Password entry with placeholder
    self.pass_entry = tk.Entry(self, font=("Arial", 18), bd=1, show="", fg="grey")
    self.pass_entry.pack(pady=10)
    self.pass_entry.insert(0, "Password")
    self.pass_entry.bind("<FocusIn>", self._clear_pass_placeholder)
    self.pass_entry.bind("<FocusOut>", self._add_pass_placeholder)

    # Login button
    tk.Button(self, text="Login", font=("Arial", 18), command=self.login).pack(pady=20)


    # --- Placeholder logic for entry fields ---
    def _clear_user_placeholder(self, event):
        """Remove placeholder text from username entry when focused."""
        if self.user_entry.get() == "Username":
            self.user_entry.delete(0, tk.END)
            self.user_entry.config(fg="black")

    def _add_user_placeholder(self, event):
        """Restore placeholder text if username entry is empty when unfocused."""
        if not self.user_entry.get():
            self.user_entry.insert(0, "Username")
            self.user_entry.config(fg="grey")

    def _clear_pass_placeholder(self, event):
        """Remove placeholder text from password entry when focused."""
        if self.pass_entry.get() == "Password":
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.config(show="*", fg="black")

    def _add_pass_placeholder(self, event):
        """Restore placeholder text if password entry is empty when unfocused."""
        if not self.pass_entry.get():
            self.pass_entry.config(show="", fg="grey")
            self.pass_entry.insert(0, "Password")


    def login(self):
        """Handle login button click: authenticate or register user."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        user = self.user_manager.get_user(username)
        if user:
            # User exists, check password
            if user.authenticate(password):
                messagebox.showinfo("Success", "Login successful!")
                self.destroy()
                MainWindow(username)
            else:
                messagebox.showerror("Error", "Incorrect password.")
        else:
            # User does not exist, offer registration
            if messagebox.askyesno("Register", f"Username '{username}' not found. Register as new user?"):
                self.user_manager.add_user(username, password)
                messagebox.showinfo("Registered", "User registered and logged in!")
                self.destroy()
                MainWindow(username)


# Main application window shown after successful login
class MainWindow(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.title("Welcome")
        self.geometry("400x200")
        # Display welcome message
        tk.Label(self, text=f"Welcome, {username}!", font=("Arial", 24)).pack(pady=60)
        self.mainloop()


# Entry point: create UserManager and launch LoginWindow
if __name__ == "__main__":
    user_manager = UserManager(PASSWORDS_FILE)
    app = LoginWindow(user_manager)
    app.mainloop()
