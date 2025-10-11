import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os

class KioskFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.scan_start_x = 0 # To hold the initial x-coordinate for scrolling
        self._last_canvas_width = 0 # To prevent unnecessary redraws

        # --- Drag vs. Click state ---
        self._is_dragging = False
        self._click_job = None
        self._clicked_item_data = None
        self._resize_job = None
        self.image_cache = {} # To prevent images from being garbage-collected

        # --- Color and Font Scheme ---
        self.colors = {
            'background': '#f0f4f8',
            'card_bg': '#ffffff',
            'text_fg': '#2c3e50',
            'gray_fg': '#7f8c8d',
            'price_fg': '#27ae60',
            'border': '#dfe6e9',
            'disabled_bg': '#f5f6fa',
            'out_of_stock_fg': '#e74c3c'
        }
        self.fonts = {
            'header': tkfont.Font(family="Helvetica", size=24, weight="bold"),
            'name': tkfont.Font(family="Helvetica", size=16, weight="bold"),
            'description': tkfont.Font(family="Helvetica", size=12),
            'price': tkfont.Font(family="Helvetica", size=14, weight="bold"),
            'quantity': tkfont.Font(family="Helvetica", size=12),
            'image_placeholder': tkfont.Font(family="Helvetica", size=14),
            'out_of_stock': tkfont.Font(family="Helvetica", size=14, weight="bold"),
        }
        
        self.items = controller.items
        self.configure(bg=self.colors['background'])
        self.create_widgets()


    def on_canvas_press(self, event):
        """Records the starting y-position and fixed x-position of a mouse drag."""
        self.canvas.scan_mark(event.x, event.y)
        self.scan_start_x = event.x

    def on_canvas_drag(self, event):
        """Moves the canvas view vertically based on mouse drag."""
        # Use the stored scan_start_x to prevent horizontal movement
        self.canvas.scan_dragto(self.scan_start_x, event.y, gain=1)

    def on_item_press(self, event, item_data):
        """Handles the initial press on an item card."""
        # Prepare for a potential drag
        self.on_canvas_press(event)
        # Store item data for a potential click
        self._clicked_item_data = item_data
        # Schedule the click action, but don't execute it yet
        self._click_job = self.after(150, self.perform_item_click)

    def on_item_drag(self, event):
        """Handles dragging that starts on an item card."""
        # If a click was scheduled, cancel it because this is a drag
        if self._click_job:
            self.after_cancel(self._click_job)
            self._click_job = None
        # Perform the canvas drag
        self.on_canvas_drag(event)

    def on_item_release(self, event):
        """Resets state on mouse release."""
        # This is intentionally left simple. The click is handled by the after() job.
        pass

    def perform_item_click(self):
        """Navigates to the item screen. Called only if no drag occurs."""
        if self._clicked_item_data:
            self.controller.show_item(self._clicked_item_data)
    def create_item_card(self, parent, item_data):
        """Creates a single item card widget."""
        card = tk.Frame(
            parent, 
            bg=self.colors['card_bg'], 
            highlightbackground=self.colors['border'], 
            highlightthickness=1
        )

        # 3. Image Placeholder
        image_frame = tk.Frame(card, bg=self.colors['card_bg'], height=150)
        image_frame.pack(fill='x', padx=10, pady=10)
        image_frame.pack_propagate(False) # Prevents child widgets from resizing it
        
        image_label = tk.Label(image_frame, bg=self.colors['card_bg'])
        image_label.pack(expand=True)

        image_path = item_data.get("image")
        if image_path and os.path.exists(image_path):
            try:
                # Open, resize, and display the image
                img = Image.open(image_path)
                
                # Resize image to fit the frame height while maintaining aspect ratio
                base_height = 150
                h_percent = (base_height / float(img.size[1]))
                w_size = int((float(img.size[0]) * float(h_percent)))
                img = img.resize((w_size, base_height), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                image_label.config(image=photo)
                image_label.image = photo # Keep a reference!
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                image_label.config(text="Image Error", font=self.fonts['image_placeholder'], fg=self.colors['gray_fg'])
        else:
            # Show placeholder if no image
            image_label.config(text="No Image", font=self.fonts['image_placeholder'], fg=self.colors['gray_fg'])


        # Frame for text content
        text_frame = tk.Frame(card, bg=self.colors['card_bg'])
        text_frame.pack(fill='x', padx=10)

        # 1. Name of item
        tk.Label(
            text_frame, 
            text=item_data['name'], 
            font=self.fonts['name'], 
            bg=self.colors['card_bg'], 
            fg=self.colors['text_fg'],
            anchor='w'
        ).pack(fill='x', pady=(5, 2))

        # 2. Description
        tk.Label(
            text_frame, 
            text=item_data['description'], 
            font=self.fonts['description'], 
            bg=self.colors['card_bg'], 
            fg=self.colors['gray_fg'],
            wraplength=280,
            justify='left',
            anchor='nw'
        ).pack(fill='x', pady=(0, 10))

        # Frame for price and quantity
        bottom_frame = tk.Frame(card, bg=self.colors['card_bg'])
        bottom_frame.pack(fill='x', padx=10, pady=(0, 10))

        if item_data['quantity'] > 0:
            # 4. Price
            tk.Label(
                bottom_frame, 
                text=f"{self.controller.currency_symbol}{item_data['price']:.2f}", 
                font=self.fonts['price'], 
                bg=self.colors['card_bg'], 
                fg=self.colors['price_fg']
            ).pack(side='left')

            # 5. Quantity available
            tk.Label(
                bottom_frame, 
                text=f"Qty: {item_data['quantity']}", 
                font=self.fonts['quantity'], 
                bg=self.colors['card_bg'], 
                fg=self.colors['gray_fg']
            ).pack(side='right')

            # --- Bind click event to all widgets on the card ---
            # We now need to handle press, drag (motion), and release separately
            press_action = lambda e, data=item_data: self.on_item_press(e, data)
            
            card.bind("<ButtonPress-1>", press_action)
            card.bind("<B1-Motion>", self.on_item_drag)
            card.bind("<ButtonRelease-1>", self.on_item_release)
            for widget in card.winfo_children():
                widget.bind("<ButtonPress-1>", press_action)
                widget.bind("<B1-Motion>", self.on_item_drag)
                widget.bind("<ButtonRelease-1>", self.on_item_release)
                if isinstance(widget, tk.Frame): # Bind children of inner frames too
                    for child in widget.winfo_children():
                        child.bind("<ButtonPress-1>", press_action)
                        child.bind("<B1-Motion>", self.on_item_drag)
                        child.bind("<ButtonRelease-1>", self.on_item_release)
        else: # Item is out of stock
            # Change background of all frames on the card
            disabled_bg = self.colors['disabled_bg']
            card.config(bg=disabled_bg)
            for widget in card.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=disabled_bg)
                    for child in widget.winfo_children():
                        child.config(bg=disabled_bg)

            # Display "Out of Stock" message
            tk.Label(bottom_frame, text="Out of Stock", font=self.fonts['out_of_stock'], bg=disabled_bg, fg=self.colors['out_of_stock_fg']).pack()

        return card

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg=self.colors['background'])
        header.pack(fill='x', padx=20, pady=20)
        tk.Label(header, text="Browse Items", font=self.fonts['header'], bg=self.colors['background'], fg=self.colors['text_fg']).pack(side='left', expand=True)

        cart_button = tk.Button(
            header,
            text="View Cart",
            font=self.fonts['description'],
            bg=self.colors['price_fg'],
            fg=self.colors['card_bg'],
            relief='flat',
            padx=15,
            pady=5,
            command=lambda: self.controller.show_cart()
        )
        cart_button.pack(side='right')

        # Container for the scrollable area to allow centering
        # We bind the resize event here to trigger a grid rebuild.
        scroll_container = tk.Frame(self, bg=self.colors['background'])
        scroll_container.pack(fill='both', expand=True)
        scroll_container.bind('<Configure>', self.on_resize)

        # Scrollable area for items
        self.canvas = tk.Canvas(scroll_container, bg=self.colors['background'], highlightthickness=0)
        # The scrollbar is no longer created or packed.
        scrollable_frame = tk.Frame(self.canvas, bg=self.colors['background'])

        # Bind drag-to-scroll to the frame itself (for the space between items)
        scrollable_frame.bind("<ButtonPress-1>", self.on_canvas_press)
        scrollable_frame.bind("<B1-Motion>", self.on_canvas_drag)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # The canvas window that holds the frame
        self.canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # The yscrollcommand is no longer configured as there is no scrollbar.

        # Populate grid with item cards
        self.populate_items()
        # --- Add Drag-to-Scroll functionality ---
        # We only need to bind to the canvas itself.
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

        self.canvas.pack(side="left", fill="both", expand=True)
        # The scrollbar.pack() call is removed.

    def on_resize(self, event):
        """
        On window resize, checks if the width has changed enough to warrant
        rebuilding the item grid.
        """
        # Cancel any pending resize job to avoid multiple executions
        if self._resize_job:
            self.after_cancel(self._resize_job)

        # Schedule the grid population to run after a short delay
        if abs(event.width - self._last_canvas_width) > 10:
            self._resize_job = self.after(50, self.populate_items)

    def populate_items(self):
        """Clears and repopulates the scrollable frame with item cards."""
        scrollable_frame = self.canvas.nametowidget(self.canvas.itemcget(self.canvas_window, 'window'))

        # Clear existing items
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # --- Dynamic Column Calculation ---
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 2: # Widget not drawn yet, can't calculate
            return

        card_plus_padding_width = 300 + 30 # Approx. card width + (padx * 2)
        num_cols = max(1, canvas_width // card_plus_padding_width)

        self._last_canvas_width = canvas_width # Update last known width

        # Repopulate grid with item cards from the controller's master list
        max_cols = num_cols
        for i, item in enumerate(self.controller.items):
            row = i // max_cols
            col = i % max_cols
            card = self.create_item_card(scrollable_frame, item)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Schedule center_frame to run after the layout has been updated
        # This ensures we get the correct width for the scrollable_frame
        self.after(10, self.center_frame)

    def center_frame(self, event=None):
        """Callback function to center the scrollable frame inside the canvas."""
        scrollable_frame = self.canvas.nametowidget(self.canvas.itemcget(self.canvas_window, 'window'))
        
        # Force the geometry manager to process layout changes
        scrollable_frame.update_idletasks()
        
        canvas_width = self.canvas.winfo_width()
        frame_width = scrollable_frame.winfo_width()
        
        x_pos = (canvas_width - frame_width) / 2
        if x_pos < 0:
            x_pos = 0
            
        self.canvas.coords(self.canvas_window, x_pos, 0)

    def reset_state(self):
        """Resets the kiosk screen to its initial state."""
        self.populate_items()