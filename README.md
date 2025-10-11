# Electronics Vending Machine UI

A touch-friendly graphical user interface for an electronics component vending machine, built with Python and Tkinter. This application provides a simple interface for customers to browse and purchase items, as well as a password-protected admin panel for inventory management.

 <!-- Placeholder: Replace with a real screenshot URL -->

## Features

- **Kiosk Mode:**
  - Visually browse a grid of available electronic components with images.
  - View item details including name, description, price, and stock quantity.
  - Add items to a shopping cart.
  - Drag-to-scroll and mouse-wheel support for easy navigation.
- **Shopping Cart:**
  - View all items in the cart.
  - Adjust item quantities or remove items.
  - See a running grand total.
  - "Checkout" functionality (simulated).
- **Admin Panel:**
  - View a complete list of all items in the inventory.
  - **Add** new items to the inventory via a pop-up form.
  - **Edit** existing item details (name, description, price, quantity, image path).
  - **Remove** items from the inventory with a confirmation dialog.
  - Changes are saved directly to `item_list.json`.

## Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

- Python 3.6 or newer. You can download it from python.org.
- `pip` (Python's package installer), which is usually included with Python.

### Steps

1.  **Clone the repository or download the source code.**
    If you have Git installed, you can use:

    ```sh
    git clone https://github.com/amalej/py-electronics-vending-machine.git
    cd py-electronics-vending-machine
    ```

2.  **Create and activate a virtual environment.**
    It's highly recommended to use a virtual environment to keep dependencies isolated.

    - On **Windows**:
      ```sh
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - On **macOS and Linux**:
      ```sh
      python3 -m venv venv
      . /venv/bin/activate
      ```

3.  **Install the required dependencies.**
    Run the following command in your terminal. This will install the `Pillow` library, which is needed for image handling.
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application, navigate to the `src` directory and execute the `main.py` script from the project root:

```sh
python src/main.py
```

The application will start in fullscreen mode, presenting the Kiosk/Admin selection screen.
