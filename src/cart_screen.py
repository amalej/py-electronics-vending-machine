import tkinter as tk
from tkinter import font as tkfont


class CartScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#f0f4f8")
        self.controller = controller

        # --- Colors and Fonts ---
        self.colors = {
            "background": "#f0f4f8",
            "text_fg": "#2c3e50",
            "gray_fg": "#7f8c8d",
            "border": "#dfe6e9",
            "header_bg": "#ffffff",
            "total_fg": "#27ae60",
        }
        self.fonts = {
            "header": tkfont.Font(family="Helvetica", size=24, weight="bold"),
            "item_name": tkfont.Font(family="Helvetica", size=16, weight="bold"),
            "item_details": tkfont.Font(family="Helvetica", size=14),
            "total": tkfont.Font(family="Helvetica", size=20, weight="bold"),
            "qty_btn": tkfont.Font(family="Helvetica", size=14, weight="bold"),
            "action_button": tkfont.Font(family="Helvetica", size=18, weight="bold"),
        }

        # --- Header ---
        header = tk.Frame(
            self,
            bg=self.colors["header_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
        )
        header.pack(fill="x", pady=(0, 10))
        tk.Label(
            header,
            text="Your Cart",
            font=self.fonts["header"],
            bg=header["bg"],
            fg=self.colors["text_fg"],
        ).pack(pady=20)

        # --- Main content area for cart items ---
        self.cart_items_frame = tk.Frame(self, bg=self.colors["background"])
        self.cart_items_frame.pack(fill="both", expand=True, padx=50)

        # --- Footer for totals and buttons ---
        footer = tk.Frame(self, bg=self.colors["background"])
        footer.pack(fill="x", padx=50, pady=20)

        self.total_label = tk.Label(
            footer,
            font=self.fonts["total"],
            bg=footer["bg"],
            fg=self.colors["total_fg"],
        )
        self.total_label.pack(pady=(0, 20))

        action_frame = tk.Frame(footer, bg=self.colors["background"])
        action_frame.pack(fill="x")

        back_button = tk.Button(
            action_frame,
            text="Back to Shopping",
            font=self.fonts["action_button"],
            bg=self.colors["gray_fg"],
            fg=self.colors["background"],
            relief="flat",
            pady=10,
            command=lambda: controller.show_kiosk(),
        )
        back_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.checkout_button = tk.Button(
            action_frame,
            text="Checkout",
            font=self.fonts["action_button"],
            bg=self.colors["total_fg"],
            fg=self.colors["background"],
            relief="flat",
            pady=10,
            command=self.checkout,
        )
        self.checkout_button.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def update_cart(self, cart_items):
        # Clear previous items
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()

        if not cart_items:
            tk.Label(
                self.cart_items_frame,
                text="Your cart is empty.",
                font=self.fonts["item_name"],
                bg=self.colors["background"],
                fg=self.colors["gray_fg"],
            ).pack(pady=50)
            self.total_label.config(text="")
            self.checkout_button.config(state="disabled")
            return

        grand_total = 0
        self.checkout_button.config(state="normal")
        for item_info in cart_items:
            item = item_info["item"]
            quantity = item_info["quantity"]
            total_price = item["price"] * quantity
            grand_total += total_price

            item_frame = tk.Frame(
                self.cart_items_frame,
                bg="white",
                highlightbackground=self.colors["border"],
                highlightthickness=1,
            )
            item_frame.pack(fill="x", pady=5)
            item_frame.grid_columnconfigure(1, weight=1)

            # --- Left side: Name and Price ---
            info_frame = tk.Frame(item_frame, bg="white")
            info_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nw")

            name_label = tk.Label(
                info_frame,
                text=item["name"],
                font=self.fonts["item_name"],
                bg="white",
                fg=self.colors["text_fg"],
                anchor="w",
            )
            name_label.pack(fill="x")

            details_label = tk.Label(
                info_frame,
                text=f"{self.controller.currency_symbol}{item['price']:.2f} each",
                font=self.fonts["item_details"],
                bg="white",
                fg=self.colors["gray_fg"],
                anchor="w",
            )
            details_label.pack(fill="x")

            # --- Right side: Controls and Total ---
            controls_frame = tk.Frame(item_frame, bg="white")
            controls_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nse")

            # Quantity adjustment
            qty_frame = tk.Frame(controls_frame, bg="white")
            qty_frame.pack(side="left", padx=20)

            decrease_btn = tk.Button(
                qty_frame,
                text="-",
                font=self.fonts["qty_btn"],
                bg=self.colors["background"],
                fg=self.colors["text_fg"],
                relief="flat",
                width=2,
                command=lambda i=item: self.controller.decrease_cart_item_quantity(i),
            )
            decrease_btn.pack(side="left")

            qty_label = tk.Label(
                qty_frame,
                text=str(quantity),
                font=self.fonts["item_details"],
                bg="white",
                fg=self.colors["text_fg"],
                width=3,
            )
            qty_label.pack(side="left", padx=5)

            increase_btn = tk.Button(
                qty_frame,
                text="+",
                font=self.fonts["qty_btn"],
                bg=self.colors["background"],
                fg=self.colors["text_fg"],
                relief="flat",
                width=2,
                command=lambda i=item: self.controller.increase_cart_item_quantity(i),
            )
            increase_btn.pack(side="left")

            # Total price for the item line
            price_label = tk.Label(
                controls_frame,
                text=f"{self.controller.currency_symbol}{total_price:.2f}",
                font=self.fonts["item_name"],
                bg="white",
                fg=self.colors["text_fg"],
                width=10,
                anchor="e",
            )
            price_label.pack(side="left", padx=20)

            # Delete button
            delete_btn = tk.Button(
                controls_frame,
                text="✕",
                font=self.fonts["qty_btn"],
                bg="white",
                fg="#e74c3c",
                relief="flat",
                command=lambda i=item: self.controller.remove_from_cart(i),
            )
            delete_btn.pack(side="left")

        self.total_label.config(
            text=f"Grand Total: {self.controller.currency_symbol}{grand_total:.2f}"
        )

    def checkout(self):
        print("Checkout process initiated.")
        # The controller's handle_checkout now returns True for success, False for failure.
        checkout_successful = self.controller.handle_checkout(self.controller.cart)

        if checkout_successful:
            self.controller.clear_cart()
            tk.messagebox.showinfo(
                "Checkout Complete",
                "Your purchase was successful and the cart has been cleared.",
            )
            self.controller.show_kiosk()
        else:
            # If checkout fails, show an error and do NOT clear the cart.
            # The quantities have already been restored by the controller.
            tk.messagebox.showerror(
                "Checkout Failed",
                "There was a problem processing your order. Please try again.",
            )
