import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import os
import datetime

ICON_HOME = "\U0001F3E0"
ICON_EXIT = "\u21B5"
ICON_USER = "\U0001F464"
ICON_LOCK = "\U0001F512"

ORDERS_FILE = os.path.join(os.path.dirname(__file__), "orders.json")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                # Read file and handle empty-file edge case (tolerant read)
                content = f.read().strip()
                if not content:
                    return []
                # Parse JSON; may raise JSONDecodeError which we catch above
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

MENU_ITEMS = [
    {"name": "Cappuccino", "price": 5},
    {"name": "Latte", "price": 5},
    {"name": "Espresso", "price": 4},
    {"name": "Hot Chocolate", "price": 4},
    {"name": "Muffin", "price": 6},
    {"name": "Flat White", "price": 4},
    {"name": "Mocha", "price": 5},
    {"name": "Long Black", "price": 4},
    {"name": "Tea", "price": 3},
    {"name": "Iced Coffee", "price": 6},
    {"name": "Bagel", "price": 5},
    {"name": "Brownie", "price": 4},
    {"name": "Scone", "price": 3},
    {"name": "Sandwich", "price": 7},
    {"name": "Juice", "price": 4},
]


def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                # Same tolerant read as users: empty file -> empty list
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cafe System")
        self.geometry("1365x768")
        self.configure(bg="white")
        self.resizable(True, True)
        self.order_history = load_orders()
        self.username = None
        self.permission = None
        # Set order_number to next available number
        if self.order_history:
            self.order_number = max(order.get("order_number", 0) for order in self.order_history) + 1
        else:
            self.order_number = 1
        self.users = load_users()
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True)
        tk.Label(frame, text="Login", font=("Arial", 64, "bold"), bg="white").pack(pady=40)
        # Use grid layout inside frames so label, entry, and icon align and
        # both username and password rows have the same visual width.
        user_frame = tk.Frame(frame, bg="white", highlightbackground="black", highlightthickness=1)
        user_frame.pack(pady=10, padx=200, fill=tk.X)
        user_frame.grid_columnconfigure(1, weight=1)  # make entry column expand
        tk.Label(user_frame, text="Username:", font=("Arial", 24), bg="white").grid(row=0, column=0, padx=10, pady=6)
        user_entry = tk.Entry(user_frame, font=("Arial", 24), bd=0)
        user_entry.grid(row=0, column=1, padx=10, sticky="ew")
        # Icon centered in its grid cell
        tk.Label(user_frame, text=ICON_USER, font=("Arial", 24), bg="white", width=3, anchor="center").grid(row=0, column=2, padx=10)

        pass_frame = tk.Frame(frame, bg="white", highlightbackground="black", highlightthickness=1)
        pass_frame.pack(pady=10, padx=200, fill=tk.X)
        pass_frame.grid_columnconfigure(1, weight=1)
        tk.Label(pass_frame, text="Password: ", font=("Arial", 24), bg="white").grid(row=0, column=0, padx=10, pady=6)
        pass_entry = tk.Entry(pass_frame, font=("Arial", 24), bd=0, show="*")
        pass_entry.grid(row=0, column=1, padx=10, sticky="ew")
        tk.Label(pass_frame, text=ICON_LOCK, font=("Arial", 24), bg="white", width=3, anchor="center").grid(row=0, column=2, padx=10)

        def do_login():
            # Read entries and authenticate against loaded users
            username = user_entry.get()
            password = pass_entry.get()
            for user in self.users:
                if user["username"] == username and user["password"] == password:
                    self.username = username
                    self.permission = user["permission"]
                    self.show_main()
                    return
            messagebox.showerror("Login Failed", "Invalid username or password.")

        # Bind Enter key to login for both entry fields and the frame
        user_entry.bind("<Return>", lambda event: do_login())
        pass_entry.bind("<Return>", lambda event: do_login())
        frame.bind("<Return>", lambda event: do_login())
        frame.focus_set()

        tk.Button(frame, text="Login", font=("Arial", 28), bg="white", bd=1, relief="solid",
                  highlightbackground="black", highlightthickness=1, width=16, command=do_login).pack(pady=30)

    def show_main(self):
        self.clear()
        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(fill=tk.X, pady=10)

        home_label = tk.Label(top_frame, text=ICON_HOME, font=("Arial", 48), bg="white", cursor="hand2")
        home_label.pack(side=tk.LEFT, padx=(30, 10))
        home_label.bind("<Button-1>", lambda e: self.show_welcome())

        button_frame = tk.Frame(top_frame, bg="white")
        button_frame.pack(side=tk.LEFT, expand=True)

        # Only show 'Accounts' button for Admins
        menu_buttons = [
            ("New Order", self.show_order),
            ("Order List", self.show_order_history),
        ]
        if self.permission == "Admin":
            menu_buttons.append(("Accounts", self.show_accounts))

        for text, cmd in menu_buttons:
            btn = tk.Button(button_frame, text=text, font=("Arial", 20), bg="white", fg="black", bd=1, relief="solid",
                            highlightbackground="black", highlightthickness=2, width=16, height=2, command=cmd)
            btn.pack(side=tk.LEFT, padx=40)

        exit_label = tk.Label(top_frame, text=ICON_EXIT, font=("Arial", 48), bg="white", cursor="hand2")
        exit_label.pack(side=tk.RIGHT, padx=(10, 30))
        exit_label.bind("<Button-1>", lambda e: self.destroy())
        tk.Frame(self, height=2, bg="black").pack(fill=tk.X, pady=10)

        self.show_welcome()

    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Welcome {self.username}", font=("Arial", 64, "bold"), bg="white").pack(pady=60)

    def clear_content(self):
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True)


    def show_accounts(self):
        # Only allow Admins to access this page
        if self.permission != "Admin":
            messagebox.showerror("Access Denied", "You do not have permission to view this page.")
            self.show_welcome()
            return
        self.clear_content()

        # Only use scrollable canvas if more than 4 users
        max_visible = 4
        use_scroll = len(self.users) > max_visible

        if use_scroll:
            container = tk.Frame(self.content_frame, bg="white")
            container.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(container, bg="white", highlightthickness=0)
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            inner_frame = tk.Frame(canvas, bg="white")
            window_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(window_id, width=canvas.winfo_width())
            inner_frame.bind("<Configure>", on_frame_configure)

            # Mouse wheel scrolling support
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            inner_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            inner_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

            # Use the inner_frame as the parent for grid content when scrolling
            grid_parent = inner_frame
        else:
            grid_parent = self.content_frame

                # --- Create table headers for the user account list ---
        tk.Label(grid_parent, text="Username", font=("Arial", 32), bg="white").grid(row=0, column=0, padx=60, pady=20)
        tk.Label(grid_parent, text="Password", font=("Arial", 32), bg="white").grid(row=0, column=1, padx=60, pady=20)
        tk.Label(grid_parent, text="Permissions", font=("Arial", 32), bg="white").grid(row=0, column=2, padx=60, pady=20)
        tk.Label(grid_parent, text="Delete", font=("Arial", 32), bg="white").grid(row=0, column=3, padx=60, pady=20)

        # --- Function to delete a user account ---
        def delete_user(idx):
            user = self.users[idx]

            # Prevent deleting the currently logged-in user
            if user["username"] == self.username:
                messagebox.showwarning("Delete User", "You cannot delete the currently logged-in user.")
                return

            # Confirm deletion before removing user
            if messagebox.askyesno("Delete User", f"Are you sure you want to delete user '{user['username']}'?"):
                del self.users[idx]          # Remove user from list
                save_users(self.users)       # Save changes to file
                messagebox.showinfo("Deleted", f"User '{user['username']}' deleted.")
                self.show_accounts()         # Refresh account screen

        # --- Display each user in a new row ---
        for i, user in enumerate(self.users, 1):
            # Show username
            tk.Label(grid_parent, text=user["username"], font=("Arial", 28), bg="white").grid(row=i, column=0, padx=60, pady=10)
            # Hide password with asterisks
            tk.Label(grid_parent, text="*" * len(user["password"]), font=("Arial", 28), bg="white").grid(row=i, column=1, padx=60, pady=10)
            # Show permission level (Admin or Waiter)
            tk.Label(grid_parent, text=user["permission"], font=("Arial", 28), bg="white").grid(row=i, column=2, padx=60, pady=10)
            # Add delete button for each user
            del_btn = tk.Button(
                grid_parent,
                text="Delete",
                font=("Arial", 18),
                bg="#F44336",  # red
                fg="white",
                command=lambda idx=i-1: delete_user(idx)
            )
            del_btn.grid(row=i, column=3, padx=20, pady=10)

        # --- Section for adding new users ---
        row = len(self.users) + 2
        tk.Label(grid_parent, text="Add New User", font=("Arial", 28, "bold"), bg="white").grid(row=row, column=0, columnspan=4, pady=(30, 10))

        # Input fields for new user data
        new_user_var = tk.StringVar()
        new_pass_var = tk.StringVar()
        new_perm_var = tk.StringVar(value="Waiter")  # Default role

        # Entry boxes for username, password, and permission type
        tk.Entry(grid_parent, textvariable=new_user_var, font=("Arial", 24), width=12).grid(row=row+1, column=0, padx=10, pady=10)
        tk.Entry(grid_parent, textvariable=new_pass_var, font=("Arial", 24), width=12, show="*").grid(row=row+1, column=1, padx=10, pady=10)
        perm_menu = ttk.Combobox(
            grid_parent,
            textvariable=new_perm_var,
            font=("Arial", 20),
            width=10,
            values=["Admin", "Waiter"]
        )
        perm_menu.grid(row=row+1, column=2, padx=10, pady=10)

        # --- Function to add a new user ---
        def add_user():
            username = new_user_var.get().strip()
            password = new_pass_var.get().strip()
            permission = new_perm_var.get().strip()

            # Check that all fields are filled
            if not username or not password or not permission:
                messagebox.showwarning("Input Error", "All fields are required.")
                return

            # Enforce password length constraints (min 4, max 14)
            if len(password) < 4 or len(password) > 14:
                messagebox.showwarning("Input Error", "Password must be between 4 and 14 characters.")
                return

            # Check for duplicate usernames
            for user in self.users:
                if user["username"] == username:
                    messagebox.showwarning("Input Error", "Username already exists.")
                    return

            # Add new user to list and save
            self.users.append({"username": username, "password": password, "permission": permission})
            save_users(self.users)
            messagebox.showinfo("Success", f"User '{username}' added.")
            self.show_accounts()  # Refresh user list

        # "Add User" button
        tk.Button(
            grid_parent,
            text="Add User",
            font=("Arial", 20),
            command=add_user,
            bg="white",
            bd=1,
            relief="solid",
            highlightbackground="black",
            highlightthickness=1
        ).grid(row=row+2, column=0, columnspan=4, pady=10)


        # --- Function: show_order ---
    def show_order(self):
        # Clear any previous content before showing new order screen
        self.clear_content()
        self.current_order = []
        self.total_cost = 0
        self.current_order_counts = {}  # Track item name, details, and count

        # Configure layout for the order screen
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=0)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Main frame for order content
        main_frame = tk.Frame(self.content_frame, bg="white")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Top section holds the menu and order display
        top_frame = tk.Frame(main_frame, bg="white")
        top_frame.pack(fill=tk.BOTH, expand=True)
        top_frame.grid_rowconfigure(1, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)
        top_frame.grid_columnconfigure(2, weight=1)

        # Menu title label
        tk.Label(
            top_frame,
            text="Menu",
            font=("Arial", 32, "bold"),
            bg="white"
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Only use scrollable canvas if more than 10 menu items
        max_visible = 10
        use_scroll = len(MENU_ITEMS) > max_visible

        if use_scroll:
            menu_canvas = tk.Canvas(top_frame, bg="white", highlightthickness=0)
            menu_canvas.grid(row=1, column=0, padx=20, sticky="nsew")
            menu_scrollbar = tk.Scrollbar(top_frame, orient="vertical", command=menu_canvas.yview)
            menu_scrollbar.grid(row=1, column=0, sticky="nse")
            menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
            menu_inner = tk.Frame(menu_canvas, bg="white")
            menu_canvas.create_window((0, 0), window=menu_inner, anchor="nw")

            def on_frame_configure(event):
                menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
            menu_inner.bind("<Configure>", on_frame_configure)

            def _on_mousewheel(event):
                menu_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            menu_inner.bind("<Enter>", lambda e: menu_canvas.bind_all("<MouseWheel>", _on_mousewheel))
            menu_inner.bind("<Leave>", lambda e: menu_canvas.unbind_all("<MouseWheel>"))
            menu_parent = menu_inner
        else:
            menu_parent = top_frame

        # Create a frame to display the current order
        order_frame = tk.Frame(top_frame, bg="white", highlightbackground="black", highlightthickness=1)
        order_frame.grid(row=1, column=2, padx=40, sticky="nsew")

        # Allow the order frame to expand properly within the grid layout
        top_frame.grid_columnconfigure(2, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)

        # Title label for the order section
        tk.Label(
            order_frame,
            text="Current Order",
            font=("Arial", 28, "bold"),
            bg="white"
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Listbox to show items added to the current order
        self.order_listbox = tk.Listbox(order_frame, font=("Arial", 20), width=30, height=12)
        self.order_listbox.grid(row=1, column=0, columnspan=2, padx=20, sticky="nsew")

        # Label to show the running total of the order
        self.total_label = tk.Label(order_frame, text="Total: $0", font=("Arial", 24, "bold"), bg="white")
        self.total_label.grid(row=2, column=0, columnspan=2, pady=20)

        # Function to refresh the order display after changes
        def update_order_listbox():
            # Clear the listbox before reloading items
            self.order_listbox.delete(0, tk.END)

            # Go through each item and show its count, name, and total price
            for name, entry in self.current_order_counts.items():
                count = entry["count"]
                item = entry["item"]
                if count > 1:
                    # Show quantity when more than one of the same item is ordered
                    self.order_listbox.insert(tk.END, f'{count}x {item["name"]} - ${item["price"] * count}')
                else:
                    # Show single item
                    self.order_listbox.insert(tk.END, f'{item["name"]} - ${item["price"]}')

            # Update the total cost label
            self.total_label.config(text=f"Total: ${self.total_cost}")

        # Function to add a selected item to the current order
        def add_to_order(item):
            # Add the item to the list of ordered items
            self.current_order.append(item)

            # Increase the running total
            self.total_cost += item["price"]

            # Update item count (for duplicates)
            name = item["name"]
            if name in self.current_order_counts:
                self.current_order_counts[name]["count"] += 1
            else:
                self.current_order_counts[name] = {"item": item, "count": 1}

            # Refresh the order display
            update_order_listbox()

        # Note: current_order_counts stores aggregated counts per item name.
        # This avoids duplicate entries in the Listbox and makes computing totals simpler.

        # Create menu item buttons dynamically from MENU_ITEMS
        for i, item in enumerate(MENU_ITEMS):
            # Arrange buttons in two columns (row and column math)
            row = i // 2
            col = i % 2

            # Create a button for each menu item
            b = tk.Button(
                menu_parent,
                text=f'{item["name"]} - ${item["price"]}',
                font=("Arial", 18),
                width=20,
                height=2,
                # When clicked, call add_to_order with that specific item
                command=lambda item=item: add_to_order(item)
            )
            # Place button in grid
            b.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

        # Make both columns expand evenly
        for c in range(2):
            menu_parent.grid_columnconfigure(c, weight=1)

        # Adjust scroll area if scrolling is used
        if use_scroll:
            menu_parent.update_idletasks()
            menu_canvas.config(width=420, height=500)

        # --- Bottom Button Section (Clear, Cancel, Submit, Checkout) ---
        bottom_btns = tk.Frame(self.content_frame, bg="white")
        bottom_btns.grid(row=1, column=0, sticky="ew", pady=(10, 10))

        # Allow buttons to resize evenly across the bottom
        bottom_btns.grid_columnconfigure(0, weight=1)
        bottom_btns.grid_columnconfigure(1, weight=1)
        bottom_btns.grid_columnconfigure(2, weight=1)
        bottom_btns.grid_columnconfigure(3, weight=1)

        # "Clear Order" button - shows the order screen again (likely resets it)
        tk.Button(
            bottom_btns,
            text="Clear Order",
            font=("Arial", 18),
            width=15,
            command=lambda: self.show_order()
        ).grid(row=0, column=0, padx=20, pady=5)

        # "Cancel Order" button - goes back to the welcome screen
        tk.Button(
            bottom_btns,
            text="Cancel Order",
            font=("Arial", 18),
            width=15,
            command=self.show_welcome
        ).grid(row=0, column=1, padx=20, pady=5)

        # "Submit Order" button - saves order as unpaid
        tk.Button(
            bottom_btns,
            text="Submit Order",
            font=("Arial", 20, "bold"),
            width=20,
            bg="#4CAF50",  # green
            fg="white",
            command=self.submit_order
        ).grid(row=0, column=2, padx=40, pady=5)

        # "Checkout" button - records order as paid
        tk.Button(
            bottom_btns,
            text="Checkout",
            font=("Arial", 20),
            width=15,
            bg="#2196F3",  # blue
            fg="white",
            command=self.checkout
        ).grid(row=0, column=3, padx=20, pady=5)


    # --- Function: checkout ---
    def checkout(self):
        # Warn user if order is empty
        if not self.current_order:
            messagebox.showwarning("No Items", "No items in order.")
            return

        # Record the order as paid
        self.record_order(paid=True)

        # Notify user that the order is complete and paid
        messagebox.showinfo("Order Complete", f"Order #{self.order_number - 1} has been placed and paid.")

        # Show updated order screen
        self.show_order()


    # --- Function: submit_order ---
    def submit_order(self):
        # Warn user if order is empty
        if not self.current_order:
            messagebox.showwarning("No Items", "No items in order.")
            return

        # Record the order as unpaid
        self.record_order(paid=False)

        # Notify user that the order has been placed but not paid
        messagebox.showinfo("Order Submitted", f"Order #{self.order_number - 1} has been placed and is unpaid.")

        # Refresh or return to the order screen
        self.show_order()


    def record_order(self, paid=True):
        # Stack items for saving as well
        if hasattr(self, 'current_order_counts') and self.current_order_counts:
            items = []
            for entry in self.current_order_counts.values():
                item = entry["item"].copy()
                count = entry["count"]
                item["count"] = count
                items.append(item)
        else:
            # fallback to old behavior
            items = self.current_order
        order_record = {
            "order_number": self.order_number,
            "items": items,
            "total": self.total_cost,
            "staff": self.username,
            "paid": paid,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.order_history.append(order_record)
        save_orders(self.order_history)
        self.order_number += 1

    # After saving the order, incrementing order_number ensures uniqueness
    # across app restarts (order_number was initialized from existing history).

    def show_order_history(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Order History", font=("Arial", 32, "bold"), bg="white").pack(pady=20)

        # Always show something, even if no orders
        if not self.order_history:
            tk.Label(self.content_frame, text="No past orders.", font=("Arial", 24), bg="white").pack(pady=40)
            return

        max_visible = 4
        use_scroll = len(self.order_history) > max_visible

        if use_scroll:
            container = tk.Frame(self.content_frame, bg="white")
            container.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(container, bg="white", highlightthickness=0)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)
            inner_frame = tk.Frame(canvas, bg="white")
            window_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            parent = inner_frame
        else:
            parent = self.content_frame

        # Show newest orders first: iterate the reversed list for display.
        total_orders = len(self.order_history)
        for display_idx, order in enumerate(reversed(self.order_history)):
            orig_idx = total_orders - 1 - display_idx
            frame = tk.Frame(parent, bg="white", highlightbackground="black", highlightthickness=1)
            frame.pack(pady=10, padx=20, fill=tk.X)
            paid_str = " - Paid" if order.get("paid") else " - Unpaid"
            date_str = f" | {order.get('date', '')}"
            tk.Label(frame, text=f"Order #{order['order_number']}  -  Staff: {order['staff']}{paid_str}{date_str}", font=("Arial", 24, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)

            items_strs = []
            for item in order["items"]:
                count = item.get("count", 1)
                if count > 1:
                    items_strs.append(f"{count}x {item['name']} (${item['price'] * count})")
                else:
                    items_strs.append(f"{item['name']} (${item['price']})")
            items_str = ", ".join(items_strs)
            tk.Label(frame, text=f"Items: {items_str}", font=("Arial", 20), bg="white", wraplength=1200, justify="left").pack(anchor="w", padx=20)
            tk.Label(frame, text=f"Total: ${order['total']}", font=("Arial", 20, "bold"), bg="white").pack(anchor="w", padx=20, pady=(5, 10))

            if not order.get("paid"):
                # Capture the original index for the closure so updates modify
                # the correct record in self.order_history.
                def make_paid_closure(order_idx=orig_idx):
                    def mark_as_paid():
                        self.order_history[order_idx]["paid"] = True
                        save_orders(self.order_history)
                        messagebox.showinfo("Order Paid", f"Order #{self.order_history[order_idx]['order_number']} marked as paid.")
                        self.show_order_history()
                    return mark_as_paid
                tk.Button(frame, text="Mark as Paid", font=("Arial", 16), bg="#4CAF50", fg="white",
                          command=make_paid_closure()).pack(anchor="e", padx=20, pady=(0, 10))

        # Now bind mousewheel and update scrollregion
        if use_scroll:
            def on_frame_configure(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(window_id, width=canvas.winfo_width())

            # Bind resize and content changes
            inner_frame.bind("<Configure>", on_frame_configure)

            # Cross-platform mouse wheel handler (handles Windows/Mac and Linux)
            def _on_mousewheel(event):
                try:
                    if getattr(event, 'num', None) == 4:  # Linux scroll up
                        canvas.yview_scroll(-1, "units")
                    elif getattr(event, 'num', None) == 5:  # Linux scroll down
                        canvas.yview_scroll(1, "units")
                    else:
                        # Windows/Mac event.delta is non-zero
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except tk.TclError:
                    pass  # Canvas destroyed

            # Bind the handler to common wheel events
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

            # Unbind safely when leaving the page
            def disable_scroll_events():
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

            # Example: when navigating away or redrawing the page, call disable_scroll_events()


            # Force Tk to calculate everything now
            self.update_idletasks()
            # Call it once now
            on_frame_configure()
            # Call it again after 1 frame of rendering
            self.after(200, on_frame_configure)

# Add main entry point to run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
