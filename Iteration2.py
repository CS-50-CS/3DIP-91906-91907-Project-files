# Import modules for UI, dialogs, files and JSON handling
import tkinter as tk
from tkinter import messagebox
import os
import json

# Path to the JSON file for storing user credentials
PASSWORDS_FILE = os.path.join(os.path.dirname(__file__), "passwords.json")


class User:
    """
    Represents a user with a username and password.
    """

    def __init__(self, username, password):
        self.username = username  # user's login name
        self.password = password  # user's password

    def authenticate(self, password):
        # Check if the provided password matches the stored password
        return self.password == password


class UserManager:
    """
    Handles loading and saving users to a JSON file.
    Provides methods to add and retrieve users.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.users = self.load_users()  # Load users at startup

    def load_users(self):
        # Try to read users from JSON file; if missing or invalid, return empty dict
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                # Convert dict of username:password to User objects
                return {u: User(u, p) for u, p in data.items()}
            except Exception:
                # If file is corrupt or unreadable, start with no users
                return {}
        return {}

    def save_users(self):
        # Save all users to JSON file (overwrites file)
        data = {u: user.password for u, user in self.users.items()}
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add_user(self, username, password):
        # Add a new user and save to file
        self.users[username] = User(username, password)
        self.save_users()

    def get_user(self, username):
        # Return User object for username, or None if not found
        return self.users.get(username)


class LoginWindow(tk.Tk):
    """
    Login window for user authentication and registration.
    Handles placeholder text and input validation.
    """

    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager  # UserManager instance
        self.title("Login")
        self.geometry("400x300")
        self.configure(bg="white")
        self.resizable(False, False)
        self.create_widgets()  # Build UI widgets

    def create_widgets(self):
        # Title label at the top
        tk.Label(self, text="Login", font=("Arial", 32, "bold"), bg="white").pack(pady=30)

        # Username entry with placeholder logic
        self.user_entry = tk.Entry(self, font=("Arial", 18), bd=1, fg="grey")
        self.user_entry.pack(pady=10)
        self.user_entry.insert(0, "Username")
        # Remove placeholder on focus, restore if empty on focus out
        self.user_entry.bind("<FocusIn>", self._clear_user_placeholder)
        self.user_entry.bind("<FocusOut>", self._add_user_placeholder)

        # Password entry; starts with placeholder, switches to masked on focus
        self.pass_entry = tk.Entry(self, font=("Arial", 18), bd=1, show="", fg="grey")
        self.pass_entry.pack(pady=10)
        self.pass_entry.insert(0, "Password")
        self.pass_entry.bind("<FocusIn>", self._clear_pass_placeholder)
        self.pass_entry.bind("<FocusOut>", self._add_pass_placeholder)

        # Login button triggers login/registration logic
        tk.Button(self, text="Login", font=("Arial", 18), command=self.login).pack(pady=20)

    def _clear_user_placeholder(self, event):
        # Remove placeholder when entry is focused
        if self.user_entry.get() == "Username":
            self.user_entry.delete(0, tk.END)
            self.user_entry.config(fg="black")

    def _add_user_placeholder(self, event):
        # Restore placeholder if entry is empty on focus out
        if not self.user_entry.get():
            self.user_entry.insert(0, "Username")
            self.user_entry.config(fg="grey")

    def _clear_pass_placeholder(self, event):
        # Remove password placeholder and mask input
        if self.pass_entry.get() == "Password":
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.config(show="*", fg="black")

    def _add_pass_placeholder(self, event):
        # Restore password placeholder and unmask if empty
        if not self.pass_entry.get():
            self.pass_entry.config(show="", fg="grey")
            self.pass_entry.insert(0, "Password")

    def login(self):
        # Get username and password from entries
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        # Check for empty fields or placeholders
        if not username or not password or username.lower() == "username" or password.lower() == "password":
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        # Try to authenticate user; if not found, offer registration
        user = self.user_manager.get_user(username)
        if user:
            if user.authenticate(password):
                messagebox.showinfo("Success", "Login successful!")
                self.destroy()
                WelcomeWindow(username)
            else:
                messagebox.showerror("Error", "Incorrect password.")
        else:
            # Ask to register new user if username not found
            if messagebox.askyesno("Register", f"Username '{username}' not found. Register as new user?"):
                # Enforce password length constraints on registration
                if len(password) < 4 or len(password) > 14:
                    messagebox.showwarning("Input Error", "Password must be between 4 and 14 characters.")
                    return
                self.user_manager.add_user(username, password)
                messagebox.showinfo("Registered", "User registered and logged in!")
                self.destroy()
                WelcomeWindow(username)


class WelcomeWindow(tk.Tk):
    """
    Main application window after login.
    Shows navigation bar, menu grid, cart, and handles order/payment logic.
    """

    def __init__(self, username):
        super().__init__()
        self.title("Welcome")
        self.geometry("1365x768")  # Large window for menu grid
        self.configure(bg="white")
        self.resizable(False, False)
        self.username = username  # Store logged-in username
        self.create_widgets()  # Build UI
        self.mainloop()

    def create_widgets(self):
        # Top navigation bar with home, order, and exit buttons
        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(fill=tk.X, pady=10)
        # Home button returns to welcome screen
        home_btn = tk.Button(top_frame, text="🏠", font=("Arial", 36), bg="white", bd=0, highlightthickness=0, activebackground="white", command=self.show_welcome)
        home_btn.pack(side=tk.LEFT, padx=(30, 10))
        button_frame = tk.Frame(top_frame, bg="white")
        button_frame.pack(side=tk.LEFT, expand=True)
        button_width = 16
        button_height = 2
        self.order_btns = []
        # Only one order button for now
        for text in ["New Order"]:
            btn = tk.Button(button_frame, text=text, font=("Arial", 18), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=button_width, height=button_height)
            btn.pack(side=tk.LEFT, padx=20, pady=0)
            self.order_btns.append(btn)
        # Exit button closes the app
        exit_btn = tk.Button(top_frame, text="⏻", font=("Arial", 36), bg="white", bd=0, highlightthickness=0, activebackground="white", command=self.destroy)
        exit_btn.pack(side=tk.RIGHT, padx=(10, 30))

        # Divider line and main content area
        tk.Frame(self, height=2, bg="black").pack(fill=tk.X, pady=10)
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.show_welcome()  # Show welcome screen by default
        # Connect order button to order view
        self.order_btns[0].config(command=self.show_order)

    def clear_content(self):
        # Remove all widgets from the main content area
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        # Welcome screen with username
        self.clear_content()
        tk.Label(self.content_frame, text=f"Welcome {self.username}", font=("Arial", 64, "bold"), bg="white").pack(pady=60)

    def show_order(self):
        # Order screen: delivery method, menu grid, and cart actions
        self.clear_content()
        # Top bar for order type selection
        order_bar = tk.Frame(self.content_frame, bg="white")
        order_bar.pack(fill=tk.X, pady=(0,10))
        tk.Label(order_bar, text="New Order", font=("Arial", 32, "bold"), bg="white").pack(side=tk.LEFT, padx=(10, 40))
        tk.Label(order_bar, text="Delivery Method:", font=("Arial", 32, "bold"), bg="white").pack(side=tk.LEFT)
        delivery_var = tk.StringVar()
        delivery_menu = tk.OptionMenu(order_bar, delivery_var, "Pickup", "Delivery", "Dine-in")
        delivery_menu.config(font=("Arial", 20), width=10)
        delivery_menu.pack(side=tk.LEFT, padx=10)

        # Divider line
        tk.Frame(self.content_frame, height=2, bg="black").pack(fill=tk.X, pady=10)

        # Main area: menu grid for food/drink selection
        main_area = tk.Frame(self.content_frame, bg="white")
        main_area.pack(fill=tk.BOTH, expand=True)
        grid_frame = tk.Frame(main_area, bg="white")
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # List of menu items (name and price)
        self.menu_items = [
            {"name": "Cappuccino", "price": 5},
            {"name": "Latte", "price": 5},
            {"name": "Espresso", "price": 4},
            {"name": "Hot Chocolate", "price": 5},
            {"name": "Muffin", "price": 3},
            {"name": "Croissant", "price": 4},
            {"name": "Sandwich", "price": 6},
            {"name": "Juice", "price": 4},
        ]

        # Create a grid of buttons for each menu item (4 columns)
        num_cols = 4
        num_rows = (len(self.menu_items) + num_cols - 1) // num_cols
        button_refs = []
        for r in range(num_rows):
            grid_frame.grid_rowconfigure(r, weight=1)
            for c in range(num_cols):
                grid_frame.grid_columnconfigure(c, weight=1)
                idx = r * num_cols + c
                if idx < len(self.menu_items):
                    item = self.menu_items[idx]
                    # Square frame for button
                    square = tk.Frame(grid_frame, width=140, height=120, bg="white", highlightbackground="black", highlightthickness=2)
                    square.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
                    square.grid_propagate(False)
                    # Button for menu item, opens quantity popup
                    btn = tk.Button(square, text=f"{item['name']}\n${item['price']}", font=("Arial", 14), bg="white", bd=0, wraplength=130, command=lambda i=item: self.show_quantity_popup(i))
                    btn.pack(expand=True, fill="both")
                    button_refs.append(btn)

        # Bottom bar with Cancel and Checkout buttons
        tk.Frame(self.content_frame, height=2, bg="black").pack(fill=tk.X, pady=10)
        bottom_frame = tk.Frame(self.content_frame, bg="white")
        bottom_frame.pack(pady=20)

        def checkout():
            # Show cart summary and payment options
            self.clear_content()
            popup = tk.Frame(self.content_frame, bg="white")
            popup.pack(expand=True)
            tk.Label(popup, text="Cart Summary", font=("Arial", 32, "bold"), bg="white").pack(pady=(20,10))
            cart = getattr(self, 'cart', [])  # Get cart items
            if not cart:
                tk.Label(popup, text="Your cart is empty.", font=("Arial", 20), bg="white", fg="red").pack(pady=20)
            else:
                # Count items and show total
                from collections import Counter
                item_counts = Counter((item['name'], item['price']) for item in cart)
                total = 0
                cart_frame = tk.Frame(popup, bg="white")
                cart_frame.pack(pady=5)
                for (name, price), qty in item_counts.items():
                    tk.Label(cart_frame, text=f"{qty} x {name} ${price} = ${qty*price}", font=("Arial", 20), bg="white").pack(anchor="w")
                    total += qty * price
                tk.Label(popup, text=f"Total: ${total}", font=("Arial", 24, "bold"), bg="white").pack(pady=(10, 20))
            tk.Label(popup, text="Select Payment Method", font=("Arial", 28, "bold"), bg="white").pack(pady=(10, 20))

            def pay_success():
                # Show payment success message and clear cart
                self.clear_content()
                tk.Label(self.content_frame, text="Payment successful!", font=("Arial", 36, "bold"), fg="green", bg="white").pack(expand=True, pady=100)
                self.cart = []
                self.after(1200, self.show_order)

            # Payment buttons for Cash and Card
            tk.Button(popup, text="Cash", font=("Arial", 24), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=12, height=2, command=pay_success).pack(pady=10)
            tk.Button(popup, text="Card", font=("Arial", 24), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=12, height=2, command=pay_success).pack(pady=10)

        # Create Cancel and Checkout buttons and assign commands
        for text in ["Cancel", "Checkout"]:
            if text == "Cancel":
                btn = tk.Button(bottom_frame, text=text, font=("Arial", 24), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=12, height=2, command=self.show_welcome)
            elif text == "Checkout":
                btn = tk.Button(bottom_frame, text=text, font=("Arial", 24), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=12, height=2, command=checkout)
            else:
                btn = tk.Button(bottom_frame, text=text, font=("Arial", 24), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, width=12, height=2)
            btn.pack(side=tk.LEFT, padx=40)

    def show_quantity_popup(self, item):
        # Popup for selecting quantity and adding item to cart
        self.clear_content()
        popup_frame = tk.Frame(self.content_frame, bg="white")
        popup_frame.pack(expand=True)
        tk.Label(popup_frame, text=f"Add {item['name']} to Cart", font=("Arial", 32, "bold"), bg="white").pack(pady=30)
        tk.Label(popup_frame, text=f"Price: ${item['price']}", font=("Arial", 24), bg="white").pack(pady=10)
        tk.Label(popup_frame, text="Quantity:", font=("Arial", 20), bg="white").pack(pady=10)
        qty_var = tk.IntVar(value=1)
        qty_spin = tk.Spinbox(popup_frame, from_=1, to=20, textvariable=qty_var, font=("Arial", 20), width=5)
        qty_spin.pack(pady=10)

        def add_to_cart():
            # Add selected quantity of item to cart
            qty = qty_var.get()
            if not hasattr(self, 'cart'):
                self.cart = []
            for _ in range(qty):
                self.cart.append(item)
            tk.Label(popup_frame, text=f"Added {qty} x {item['name']} to cart!", font=("Arial", 18), fg="green", bg="white").pack(pady=10)

        tk.Button(popup_frame, text="Add to Cart", font=("Arial", 20), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, command=add_to_cart).pack(pady=20)
        tk.Button(popup_frame, text="Return", font=("Arial", 20), bg="white", fg="black", bd=1, relief="solid", highlightbackground="black", highlightthickness=1, command=self.show_order).pack(pady=10)


if __name__ == "__main__":
    # Entry point: create UserManager and start login window
    user_manager = UserManager(PASSWORDS_FILE)
    LoginWindow(user_manager).mainloop()
