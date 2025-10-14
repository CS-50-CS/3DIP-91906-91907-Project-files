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


class BaseScreen(tk.Frame):
    """Base class for screens.

    Each screen is a tk.Frame that holds its own widgets and can access
    the parent App via self.app. Screens should be instantiated with the
    App instance as their master (App is a tk.Tk subclass), then they can
    call app methods (for navigation, data, and persistence).
    """
    def __init__(self, app):
        super().__init__(app, bg="white")
        self.app = app


class LoginScreen(BaseScreen):
    """Login screen built as a reusable class."""
    def __init__(self, app):
        super().__init__(app)
        # Build the login UI directly on the root (same behavior as before)
        # We intentionally clear the entire window for the login view.
        self.app.clear()
        frame = tk.Frame(self.app, bg="white")
        frame.pack(expand=True)
        tk.Label(frame, text="Login", font=("Arial", 64, "bold"), bg="white").pack(pady=40)

        user_frame = tk.Frame(frame, bg="white", highlightbackground="black", highlightthickness=1)
        user_frame.pack(pady=10, padx=200, fill=tk.X)
        user_frame.grid_columnconfigure(1, weight=1)
        tk.Label(user_frame, text="Username:", font=("Arial", 24), bg="white").grid(row=0, column=0, padx=10, pady=6)
        user_entry = tk.Entry(user_frame, font=("Arial", 24), bd=0)
        user_entry.grid(row=0, column=1, padx=10, sticky="ew")
        tk.Label(user_frame, text=ICON_USER, font=("Arial", 24), bg="white", width=3, anchor="center").grid(row=0, column=2, padx=10)

        pass_frame = tk.Frame(frame, bg="white", highlightbackground="black", highlightthickness=1)
        pass_frame.pack(pady=10, padx=200, fill=tk.X)
        pass_frame.grid_columnconfigure(1, weight=1)
        tk.Label(pass_frame, text="Password: ", font=("Arial", 24), bg="white").grid(row=0, column=0, padx=10, pady=6)
        pass_entry = tk.Entry(pass_frame, font=("Arial", 24), bd=0, show="*")
        pass_entry.grid(row=0, column=1, padx=10, sticky="ew")
        tk.Label(pass_frame, text=ICON_LOCK, font=("Arial", 24), bg="white", width=3, anchor="center").grid(row=0, column=2, padx=10)

        def do_login():
            username = user_entry.get()
            password = pass_entry.get()
            for user in self.app.users:
                if user["username"] == username and user["password"] == password:
                    self.app.username = username
                    self.app.permission = user["permission"]
                    self.app.show_main()
                    return
            messagebox.showerror("Login Failed", "Invalid username or password.")

        user_entry.bind("<Return>", lambda event: do_login())
        pass_entry.bind("<Return>", lambda event: do_login())
        frame.bind("<Return>", lambda event: do_login())
        frame.focus_set()

        tk.Button(frame, text="Login", font=("Arial", 28), bg="white", bd=1, relief="solid",
                  highlightbackground="black", highlightthickness=1, width=16, command=do_login).pack(pady=30)


class AccountsScreen(BaseScreen):
    """Accounts management screen: list, delete, add users.

    This class implements the same behaviors as the previous show_accounts
    method but enclosed as a tk.Frame subclass so it can be unit-tested or
    reused more easily.
    """
    def __init__(self, app):
        super().__init__(app)
        self.app.clear_content()
        # Only allow Admins to access this page
        if self.app.permission != "Admin":
            messagebox.showerror("Access Denied", "You do not have permission to view this page.")
            self.app.show_welcome()
            return

        # Decide whether to use a scrollable canvas for long lists
        max_visible = 4
        use_scroll = len(self.app.users) > max_visible

        if use_scroll:
            container = tk.Frame(self.app.content_frame, bg="white")
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

            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            inner_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            inner_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

            grid_parent = inner_frame
        else:
            grid_parent = self.app.content_frame

        # Table headers
        tk.Label(grid_parent, text="Username", font=("Arial", 32), bg="white").grid(row=0, column=0, padx=60, pady=20)
        tk.Label(grid_parent, text="Password", font=("Arial", 32), bg="white").grid(row=0, column=1, padx=60, pady=20)
        tk.Label(grid_parent, text="Permissions", font=("Arial", 32), bg="white").grid(row=0, column=2, padx=60, pady=20)
        tk.Label(grid_parent, text="Delete", font=("Arial", 32), bg="white").grid(row=0, column=3, padx=60, pady=20)

        def delete_user(idx):
            user = self.app.users[idx]
            if user["username"] == self.app.username:
                messagebox.showwarning("Delete User", "You cannot delete the currently logged-in user.")
                return
            if messagebox.askyesno("Delete User", f"Are you sure you want to delete user '{user['username']}'?"):
                del self.app.users[idx]
                save_users(self.app.users)
                messagebox.showinfo("Deleted", f"User '{user['username']}' deleted.")
                self.app.show_accounts()

        for i, user in enumerate(self.app.users, 1):
            tk.Label(grid_parent, text=user["username"], font=("Arial", 28), bg="white").grid(row=i, column=0, padx=60, pady=10)
            tk.Label(grid_parent, text="*" * len(user["password"]), font=("Arial", 28), bg="white").grid(row=i, column=1, padx=60, pady=10)
            tk.Label(grid_parent, text=user["permission"], font=("Arial", 28), bg="white").grid(row=i, column=2, padx=60, pady=10)
            del_btn = tk.Button(grid_parent, text="Delete", font=("Arial", 18), bg="#F44336", fg="white",
                                command=lambda idx=i-1: delete_user(idx))
            del_btn.grid(row=i, column=3, padx=20, pady=10)

        # Section to add new users
        row = len(self.app.users) + 2
        tk.Label(grid_parent, text="Add New User", font=("Arial", 28, "bold"), bg="white").grid(row=row, column=0, columnspan=4, pady=(30, 10))
        new_user_var = tk.StringVar()
        new_pass_var = tk.StringVar()
        new_perm_var = tk.StringVar(value="Waiter")
        tk.Entry(grid_parent, textvariable=new_user_var, font=("Arial", 24), width=12).grid(row=row+1, column=0, padx=10, pady=10)
        tk.Entry(grid_parent, textvariable=new_pass_var, font=("Arial", 24), width=12, show="*").grid(row=row+1, column=1, padx=10, pady=10)
        perm_menu = ttk.Combobox(grid_parent, textvariable=new_perm_var, font=("Arial", 20), width=10, values=["Admin", "Waiter"])
        perm_menu.grid(row=row+1, column=2, padx=10, pady=10)

        def add_user():
            username = new_user_var.get().strip()
            password = new_pass_var.get().strip()
            permission = new_perm_var.get().strip()
            if not username or not password or not permission:
                messagebox.showwarning("Input Error", "All fields are required.")
                return
            if len(password) < 4 or len(password) > 14:
                messagebox.showwarning("Input Error", "Password must be between 4 and 14 characters.")
                return
            for user in self.app.users:
                if user["username"] == username:
                    messagebox.showwarning("Input Error", "Username already exists.")
                    return
            self.app.users.append({"username": username, "password": password, "permission": permission})
            save_users(self.app.users)
            messagebox.showinfo("Success", f"User '{username}' added.")
            self.app.show_accounts()

        tk.Button(grid_parent, text="Add User", font=("Arial", 20), command=add_user, bg="white", bd=1, relief="solid",
                  highlightbackground="black", highlightthickness=1).grid(row=row+2, column=0, columnspan=4, pady=10)


class OrderScreen(BaseScreen):
    """Order screen encapsulated as a class."""
    def __init__(self, app):
        super().__init__(app)
        self.app.clear_content()
        # Reuse the same logic previously in show_order()
        self.app.current_order = []
        self.app.total_cost = 0
        self.app.current_order_counts = {}

        self.app.content_frame.grid_rowconfigure(0, weight=1)
        self.app.content_frame.grid_rowconfigure(1, weight=0)
        self.app.content_frame.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.app.content_frame, bg="white")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = tk.Frame(main_frame, bg="white")
        top_frame.pack(fill=tk.BOTH, expand=True)
        top_frame.grid_rowconfigure(1, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)
        top_frame.grid_columnconfigure(2, weight=1)

        tk.Label(top_frame, text="Menu", font=("Arial", 32, "bold"), bg="white").grid(row=0, column=0, padx=20, pady=20, sticky="w")

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

        order_frame = tk.Frame(top_frame, bg="white", highlightbackground="black", highlightthickness=1)
        order_frame.grid(row=1, column=2, padx=40, sticky="nsew")
        top_frame.grid_columnconfigure(2, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)

        tk.Label(order_frame, text="Current Order", font=("Arial", 28, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)
        # Instead of a Listbox, use a frame with per-item controls
        # Keep the cart column compact by fixing its width and preventing
        # the frame from propagating to larger sizes when text changes.
        # Make the cart frame expand to the available space inside the order box
        self.cart_items_frame = tk.Frame(order_frame, bg="white")
        self.cart_items_frame.grid(row=1, column=0, columnspan=2, padx=20, sticky="nsew")
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)
        order_frame.grid_columnconfigure(1, weight=0)
        # Create a canvas + inner frame so the fixed-size cart can scroll when many items exist
        cart_canvas = tk.Canvas(self.cart_items_frame, bg="white", highlightthickness=0)
        cart_scrollbar = tk.Scrollbar(self.cart_items_frame, orient="vertical", command=cart_canvas.yview)
        cart_canvas.configure(yscrollcommand=cart_scrollbar.set)
        # Use grid inside the cart frame so canvas fills available space
        cart_canvas.grid(row=0, column=0, sticky="nsew")
        cart_scrollbar.grid(row=0, column=1, sticky="ns")
        self.cart_items_frame.grid_rowconfigure(0, weight=1)
        self.cart_items_frame.grid_columnconfigure(0, weight=1)
        self.cart_inner = tk.Frame(cart_canvas, bg="white")
        window_id = cart_canvas.create_window((0, 0), window=self.cart_inner, anchor="nw")

        def _on_inner_configure(event):
            try:
                cart_canvas.configure(scrollregion=cart_canvas.bbox("all"))
                # Make the inner frame match the visible canvas width so rows fill the box
                cart_canvas.itemconfig(window_id, width=cart_canvas.winfo_width())
                # Center the inner content horizontally inside the cart box
                self.cart_inner.update_idletasks()
                inner_w = self.cart_inner.winfo_reqwidth()
                canvas_w = cart_canvas.winfo_width()
                if inner_w < canvas_w:
                    pad = (canvas_w - inner_w) // 2
                    cart_canvas.itemconfig(window_id, x=pad)
            except tk.TclError:
                pass

        self.cart_inner.bind("<Configure>", _on_inner_configure)
        # Mouse wheel support for the cart area
        def _on_mousewheel_cart(event):
            cart_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.cart_inner.bind("<Enter>", lambda e: cart_canvas.bind_all("<MouseWheel>", _on_mousewheel_cart))
        self.cart_inner.bind("<Leave>", lambda e: cart_canvas.unbind_all("<MouseWheel>"))
        self.app.total_label = tk.Label(order_frame, text="Total: $0", font=("Arial", 24, "bold"), bg="white")
        self.app.total_label.grid(row=2, column=0, columnspan=2, pady=20)

        def update_cart_items():
            # Clear inner cart contents
            for widget in self.cart_inner.winfo_children():
                widget.destroy()
            # Set fixed column minimums but allow the main name column to expand
            self.cart_inner.grid_columnconfigure(0, minsize=110, weight=1)
            self.cart_inner.grid_columnconfigure(1, minsize=40)
            self.cart_inner.grid_columnconfigure(2, minsize=60)
            self.cart_inner.grid_columnconfigure(3, minsize=30)
            self.cart_inner.grid_columnconfigure(4, minsize=30)
            self.cart_inner.grid_columnconfigure(5, minsize=60)
            for r, (name, entry) in enumerate(self.app.current_order_counts.items()):
                item = entry['item']
                count = entry['count']
                max_name_len = 18
                display_name = (name[:max_name_len-3] + '...') if len(name) > max_name_len else name
                # Set wraplength relative to the canvas width so names wrap inside the cart box
                wrap_len = max(80, cart_canvas.winfo_width() - 160)
                tk.Label(self.cart_inner, text=f'{display_name}', font=("Arial", 12), bg="white", fg="black",
                         anchor="w", wraplength=wrap_len, justify="left").grid(row=r, column=0, padx=5, pady=4, sticky="ew")
                tk.Label(self.cart_inner, text=f'x{count}', font=("Arial", 12), bg="white", anchor="center").grid(row=r, column=1, padx=5)
                tk.Label(self.cart_inner, text=f'${item["price"] * count}', font=("Arial", 12), bg="white", anchor="e").grid(row=r, column=2, padx=5, sticky="e")

                def make_incr(n=name):
                    def incr():
                        self.app.current_order_counts[n]['count'] += 1
                        self.app.total_cost += self.app.current_order_counts[n]['item']['price']
                        update_cart_items()
                        self.app.total_label.config(text=f"Total: ${self.app.total_cost}")
                    return incr

                def make_decr(n=name):
                    def decr():
                        if self.app.current_order_counts[n]['count'] > 1:
                            self.app.current_order_counts[n]['count'] -= 1
                            self.app.total_cost -= self.app.current_order_counts[n]['item']['price']
                        else:
                            self.app.total_cost -= self.app.current_order_counts[n]['item']['price']
                            del self.app.current_order_counts[n]
                        update_cart_items()
                        self.app.total_label.config(text=f"Total: ${self.app.total_cost}")
                    return decr

                def make_remove(n=name):
                    def remove():
                        cnt = self.app.current_order_counts[n]['count']
                        price = self.app.current_order_counts[n]['item']['price']
                        self.app.total_cost -= cnt * price
                        del self.app.current_order_counts[n]
                        update_cart_items()
                        self.app.total_label.config(text=f"Total: ${self.app.total_cost}")
                    return remove

                tk.Button(self.cart_inner, text="+", width=3, command=make_incr()).grid(row=r, column=3, padx=2)
                tk.Button(self.cart_inner, text="-", width=3, command=make_decr()).grid(row=r, column=4, padx=2)
                tk.Button(self.cart_inner, text="Remove", width=8, command=make_remove()).grid(row=r, column=5, padx=6)
            self.app.total_label.config(text=f"Total: ${self.app.total_cost}")

        update_cart_items()

        def add_to_order(item):
            self.app.current_order.append(item)
            self.app.total_cost += item["price"]
            name = item["name"]
            if name in self.app.current_order_counts:
                self.app.current_order_counts[name]["count"] += 1
            else:
                self.app.current_order_counts[name] = {"item": item, "count": 1}
            update_cart_items()

        for i, item in enumerate(MENU_ITEMS):
            row = i // 2
            col = i % 2
            b = tk.Button(menu_parent, text=f'{item["name"]} - ${item["price"]}', font=("Arial", 18), width=20, height=2,
                          command=lambda item=item: add_to_order(item))
            b.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

        for c in range(2):
            menu_parent.grid_columnconfigure(c, weight=1)

        if use_scroll:
            menu_parent.update_idletasks()
            menu_canvas.config(width=420, height=500)

        bottom_btns = tk.Frame(self.app.content_frame, bg="white")
        bottom_btns.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        for i in range(4):
            bottom_btns.grid_columnconfigure(i, weight=1)

        tk.Button(bottom_btns, text="Clear Order", font=("Arial", 18), width=15, command=lambda: self.app.show_order()).grid(row=0, column=0, padx=20, pady=5)
        tk.Button(bottom_btns, text="Submit Order", font=("Arial", 20, "bold"), width=20, bg="#4CAF50", fg="white", command=self.app.submit_order).grid(row=0, column=2, padx=40, pady=5)
        tk.Button(bottom_btns, text="Checkout", font=("Arial", 20), width=15, bg="#2196F3", fg="white", command=self.app.checkout).grid(row=0, column=3, padx=20, pady=5)


class OrderHistoryScreen(BaseScreen):
    """Order history screen as a class (newest-first display)."""
    def __init__(self, app):
        super().__init__(app)
        self.app.clear_content()
        tk.Label(self.app.content_frame, text="Order History", font=("Arial", 32, "bold"), bg="white").pack(pady=20)

        if not self.app.order_history:
            tk.Label(self.app.content_frame, text="No past orders.", font=("Arial", 24), bg="white").pack(pady=40)
            return

        max_visible = 4
        use_scroll = len(self.app.order_history) > max_visible

        if use_scroll:
            container = tk.Frame(self.app.content_frame, bg="white")
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
            parent = self.app.content_frame

        total_orders = len(self.app.order_history)
        for display_idx, order in enumerate(reversed(self.app.order_history)):
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
                def make_paid_closure(order_idx=orig_idx):
                    def mark_as_paid():
                        self.app.order_history[order_idx]["paid"] = True
                        save_orders(self.app.order_history)
                        messagebox.showinfo("Order Paid", f"Order #{self.app.order_history[order_idx]['order_number']} marked as paid.")
                        self.app.show_order_history()
                    return mark_as_paid
                tk.Button(frame, text="Mark as Paid", font=("Arial", 16), bg="#4CAF50", fg="white",
                          command=make_paid_closure()).pack(anchor="e", padx=20, pady=(0, 10))

                # Allow cancelling unpaid order: removes it from history
                def make_cancel_closure(order_idx=orig_idx):
                    def cancel_order():
                        if messagebox.askyesno("Cancel Order", f"Remove Order #{self.app.order_history[order_idx]['order_number']} permanently?"):
                            del self.app.order_history[order_idx]
                            save_orders(self.app.order_history)
                            messagebox.showinfo("Cancelled", "Order removed.")
                            self.app.show_order_history()
                    return cancel_order
                tk.Button(frame, text="Cancel Order", font=("Arial", 14), bg="#E53935", fg="white",
                          command=make_cancel_closure()).pack(anchor="e", padx=20, pady=(0, 10))
            else:
                # For paid orders, provide an undo button to mark as unpaid
                def make_undo_closure(order_idx=orig_idx):
                    def undo_paid():
                        if messagebox.askyesno("Undo Paid", f"Mark Order #{self.app.order_history[order_idx]['order_number']} as unpaid?"):
                            self.app.order_history[order_idx]["paid"] = False
                            save_orders(self.app.order_history)
                            messagebox.showinfo("Updated", "Order marked as unpaid.")
                            self.app.show_order_history()
                    return undo_paid
                tk.Button(frame, text="Undo Paid", font=("Arial", 14), bg="#FFB300", fg="black",
                          command=make_undo_closure()).pack(anchor="e", padx=20, pady=(0, 10))

        if use_scroll:
            def on_frame_configure(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(window_id, width=canvas.winfo_width())

            inner_frame.bind("<Configure>", on_frame_configure)

            def _on_mousewheel(event):
                try:
                    if getattr(event, 'num', None) == 4:
                        canvas.yview_scroll(-1, "units")
                    elif getattr(event, 'num', None) == 5:
                        canvas.yview_scroll(1, "units")
                    else:
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except tk.TclError:
                    pass

            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

            def disable_scroll_events():
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

            self.app.update_idletasks()
            on_frame_configure()
            self.app.after(200, on_frame_configure)

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
        # Instantiate the LoginScreen class which handles its own UI
        LoginScreen(self)

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
        # Instantiate the AccountsScreen class which builds the accounts UI
        AccountsScreen(self)


        # --- Function: show_order ---
    def show_order(self):
        # Instantiate the OrderScreen which will build the order UI
        OrderScreen(self)


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
        # Instantiate the OrderHistoryScreen which builds the history view
        OrderHistoryScreen(self)

# Add main entry point to run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
