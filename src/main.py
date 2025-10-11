import tkinter as tk
from kiosk_app import KioskFrame
from selection_screen import SelectionScreen
import json
from admin_screen import AdminScreen
from item_screen import ItemScreen
from cart_screen import CartScreen


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.cart = []

        self.is_fullscreen = True
        self.items_file_path = "item_list.json"
        self.config_path = "config.json"
        self.items = self.load_items_from_json(self.items_file_path)
        self.config = self.load_config_from_json(self.config_path)
        self.currency_symbol = self.config.get("currency_symbol", "$")
        self.title("Vending Machine UI")
        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.handle_escape)

        # The container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (SelectionScreen, KioskFrame, AdminScreen, ItemScreen, CartScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.active_frame_name = None
        self.show_frame("SelectionScreen")

    def load_items_from_json(self, file_path):
        """Loads item data from a JSON file."""
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(
                f"Warning: {file_path} not found. Generating a new one with default items."
            )
            default_items = []
            with open(file_path, "w") as file:
                json.dump(default_items, file, indent=4)
            return default_items
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}.")
            return []

    def load_config_from_json(self, file_path):
        """Loads item data from a JSON file."""
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(
                f"Warning: {file_path} not found. Generating a new one with default items."
            )
            default_config = {"currency_symbol": "$"}
            with open(file_path, "w") as file:
                json.dump(default_config, file, indent=4)
            return default_config
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}.")
            return []

    def save_items_to_json(self):
        """Saves the current item list to the JSON file."""
        with open(self.items_file_path, "w") as file:
            json.dump(self.items, file, indent=4)

    def toggle_fullscreen(self, event=None):
        """Toggles between fullscreen and a windowed 'half-screen' mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

        if self.is_fullscreen:
            # Ensure geometry is set to max for systems like RPi
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        if not self.is_fullscreen:
            # When exiting fullscreen, set a specific size and position
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            width = screen_width // 2
            height = screen_height
            x = screen_width // 2
            self.geometry(f"{width}x{height}+{x}+0")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        self.active_frame_name = page_name
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()

    def show_kiosk(self):
        self.frames["KioskFrame"].reset_state()
        self.show_frame("KioskFrame")

    def show_item(self, item_data):
        """Passes item data to the ItemScreen and displays it."""
        self.frames["ItemScreen"].set_item(item_data)
        self.show_frame("ItemScreen")

    def show_cart(self):
        """Passes cart data to the CartScreen and displays it."""
        self.frames["CartScreen"].update_cart(self.cart)
        self.show_frame("CartScreen")

    def add_to_cart(self, added_item, quantity):
        """Adds an item and its quantity to the cart."""
        # Check if item is already in cart
        for item_info in self.cart:
            if item_info["item"]["name"] == added_item["name"]:
                item_info["quantity"] += quantity
                return  # Exit after updating

        # If not in cart, add as a new entry
        self.cart.append({"item": added_item, "quantity": quantity})

    def remove_from_cart(self, item_to_remove):
        """Removes an item entirely from the cart and restores its quantity."""
        item_found = None
        for item_info in self.cart:
            if item_info["item"]["name"] == item_to_remove["name"]:
                item_found = item_info
                break

        if item_found:
            self.increase_item_quantity(item_found["item"], item_found["quantity"])
            self.cart.remove(item_found)
            self.show_cart()  # Refresh cart screen

    def increase_cart_item_quantity(self, item_to_increase):
        """Increases an item's quantity in the cart by 1."""
        # First, check if there is available stock
        for master_item in self.items:
            if master_item["name"] == item_to_increase["name"]:
                if master_item["quantity"] > 0:
                    master_item["quantity"] -= 1  # Reduce from master list
                    # Now, increase in cart
                    for cart_item_info in self.cart:
                        if cart_item_info["item"]["name"] == item_to_increase["name"]:
                            cart_item_info["quantity"] += 1
                            self.show_cart()  # Refresh cart screen
                            return

    def decrease_cart_item_quantity(self, item_to_decrease):
        """Decreases an item's quantity in the cart by 1."""
        for item_info in self.cart:
            if item_info["item"]["name"] == item_to_decrease["name"]:
                if item_info["quantity"] > 1:
                    item_info["quantity"] -= 1
                    self.increase_item_quantity(item_to_decrease, 1)
                    self.show_cart()  # Refresh cart screen
                else:  # If quantity is 1, remove it completely
                    self.remove_from_cart(item_to_decrease)
                return

    def clear_cart(self):
        """Empties the cart."""
        self.cart.clear()

    def handle_checkout(self, checked_out_items):
        """
        Processes items at checkout. In a real app, this would handle payment.
        Here, we simulate a potential failure.
        Returns True on success, False on failure.
        """

        # TODO: Replace this simulation with real payment processing logic.
        import random

        # Simulate a 50% chance of checkout failure
        if random.random() < 0.5:
            print("Checkout failed. (Simulated)")
            return False

        print("Checkout successful. Items processed:", checked_out_items)
        self.save_items_to_json()  # Persist the new quantities
        return True

    def reduce_item_quantity(self, item, quantity):
        """Reduces the quantity of the item in the KioskFrame."""
        kiosk_frame = self.frames["KioskFrame"]
        for index in range(len(kiosk_frame.items)):
            kiosk_item = kiosk_frame.items[index]
            if kiosk_item["name"] == item["name"]:
                print(f"Reducing {item['name']} quantity by {quantity}")
                self.items[index]["quantity"] -= quantity

    def increase_item_quantity(self, item, quantity):
        """Increases the quantity of an item in the master item list."""
        for master_item in self.items:
            if master_item["name"] == item["name"]:
                master_item["quantity"] += quantity
                return

    def add_item(self, new_item_data):
        """
        Adds a new item to the master list if the name doesn't already exist.
        Saves to JSON on success. Returns True on success, False on failure.
        """
        new_item_name = new_item_data.get("name", "").strip()
        # Check for existing item with the same name (case-insensitive)
        if any(item.get("name", "").strip().lower() == new_item_name.lower() for item in self.items):
            return False  # Item with this name already exists

        self.items.append(new_item_data)
        self.save_items_to_json()
        # Refresh screens that show items
        self.frames["AdminScreen"].populate_items()
        self.frames["KioskFrame"].populate_items()
        return True

    def update_item(self, original_item_name, updated_item_data):
        """Updates an existing item in the master list and saves to JSON."""
        for i, item in enumerate(self.items):
            if item["name"] == original_item_name:
                self.items[i] = updated_item_data
                break
        self.save_items_to_json()
        self.frames["AdminScreen"].populate_items()
        self.frames["KioskFrame"].populate_items()

    def remove_item(self, item_to_remove):
        """Removes an item from the master list and saves to JSON."""
        self.items.remove(item_to_remove)
        self.save_items_to_json()
        self.frames["AdminScreen"].populate_items()

    def show_admin(self):
        self.show_frame("AdminScreen")

    def handle_escape(self, event=None):
        if self.grab_current():
            return
        elif self.active_frame_name == "ItemScreen":
            self.show_frame("KioskFrame")
        elif self.active_frame_name == "CartScreen":
            self.show_frame("KioskFrame")
        elif self.active_frame_name != "SelectionScreen":
            self.show_frame("SelectionScreen")
        else:
            self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
