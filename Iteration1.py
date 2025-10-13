# Import required modules for GUI, file handling, and JSON
import tkinter as tk
from tkinter import messagebox
import os
import json

# Path to the JSON file used to persist usernames and passwords.
# It is stored in the same directory as this script.
PASSWORDS_FILE = os.path.join(os.path.dirname(__file__), "passwords.json")


class User:
    """Representation of a user.

    Attributes:
        username (str): the user's login name
        password (str): the user's password
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self, password):
        # Return True if the supplied password matches this user's password.
        return self.password == password


class UserManager:
    # Manages loading, saving and basic operations on users appended to a JSON file.
    def __init__(self, filepath):
        self.filepath = filepath
        # Load existing users
        self.users = self.load_users()

    def load_users(self):
        """Load users from self.filepath and return a dict of User objects.

        If the file doesn't exist or is invalid the method returns an empty dict.
        """
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                return {u: User(u, p) for u, p in data.items()}
            except Exception:
                # If reading/parsing fails, don't crash the application — return an empty store.
                return {}
        # File doesn't exist yet, start with an empty user store.
        return {}

    def save_users(self):
        # Append the current user to the JSON file.
        data = {u: user.password for u, user in self.users.items()}
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add_user(self, username, password):
        # Create a new User and save the updated store to JSON file.
        self.users[username] = User(username, password)
        self.save_users()

    def get_user(self, username):
        # Return the User object for a username, or None if not found.
        return self.users.get(username)


class LoginWindow(tk.Tk):
   # Tkinter-based login window that allows signing in or registering.
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.title("Login")
        self.geometry("400x300")
        self.configure(bg="white")
        # Prevent the user from resizing the window which keeps layout consistent
        self.resizable(False, False)
        # Create widgets (labels, entry boxes, and button)
        self.create_widgets()

    def create_widgets(self):
        # Heading label
        tk.Label(self, text="Login", font=("Arial", 32, "bold"), bg="white").pack(pady=30)

        # Username entry with placeholder behavior implemented via focus events
        self.user_entry = tk.Entry(self, font=("Arial", 18), bd=1, fg="grey")
        self.user_entry.pack(pady=10)
        self.user_entry.insert(0, "Username")
        # Bind focus events to show/hide placeholder text
        self.user_entry.bind("<FocusIn>", self._clear_user_placeholder)
        self.user_entry.bind("<FocusOut>", self._add_user_placeholder)

        # Password entry. Initially shows placeholder text and no masking
        # When focused it will switch to masked input (show="*").
        self.pass_entry = tk.Entry(self, font=("Arial", 18), bd=1, show="", fg="grey")
        self.pass_entry.pack(pady=10)
        self.pass_entry.insert(0, "Password")
        self.pass_entry.bind("<FocusIn>", self._clear_pass_placeholder)
        self.pass_entry.bind("<FocusOut>", self._add_pass_placeholder)

        # Login button triggers the login flow
        tk.Button(self, text="Login", font=("Arial", 18), command=self.login).pack(pady=20)

    # --- Placeholder helper methods ---
    def _clear_user_placeholder(self, event):
        #Clear the username placeholder when the entry receives focus.
        if self.user_entry.get() == "Username":
            self.user_entry.delete(0, tk.END)
            self.user_entry.config(fg="black")

    def _add_user_placeholder(self, event):
        #Re-add username placeholder if the field is left empty on focus out.
        if not self.user_entry.get():
            self.user_entry.insert(0, "Username")
            self.user_entry.config(fg="grey")

    def _clear_pass_placeholder(self, event):
        #Clear the password placeholder and enable masking when focused.
        if self.pass_entry.get() == "Password":
            self.pass_entry.delete(0, tk.END)
            # Use '*' to mask the password characters and set text color to black
            self.pass_entry.config(show="*", fg="black")

    def _add_pass_placeholder(self, event):
        #Show the password placeholder and disable masking when empty on focus out.
        if not self.pass_entry.get():
            # Disable masking so the placeholder is readable
            self.pass_entry.config(show="", fg="grey")
            self.pass_entry.insert(0, "Password")

    def login(self):
        """Handle the login button press. Read username and password from the entry widgets. 
        If validated open MainWindow. If user doesn't exist, prompt to register and create the user.
        """
        # Trim whitespace from input fields
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        # Simple validation: both fields required
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        # Lookup user in the manager
        user = self.user_manager.get_user(username)
        if user:
            # User exists: check password
            if user.authenticate(password):
                messagebox.showinfo("Success", "Login successful!")
                # Close login window and open the main application window
                self.destroy()
                MainWindow(username)
            else:
                # Password mismatch
                messagebox.showerror("Error", "Incorrect password.")
        else:
            # User not found: offer to register as a new user
            if messagebox.askyesno("Register", f"Username '{username}' not found. Register as new user?"):
                self.user_manager.add_user(username, password)
                messagebox.showinfo("Registered", "User registered and logged in!")
                self.destroy()
                MainWindow(username)


class MainWindow(tk.Tk):
    # Main application window shown after successful login or registration.

    def __init__(self, username):
        super().__init__()
        self.title("Welcome")
        self.geometry("400x200")
        tk.Label(self, text=f"Welcome, {username}!", font=("Arial", 24)).pack(pady=60)
        self.mainloop()


if __name__ == "__main__":
    # Initialize the UserManager with the JSON file and start the login UI.
    user_manager = UserManager(PASSWORDS_FILE)
    app = LoginWindow(user_manager)
    app.mainloop()
