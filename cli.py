import sys
import requests

BASE_URL = "http://127.0.0.1:5000"


def show_menu():
    print("\n" + "=" * 40)
    print("      FOOD INVENTORY MANAGEMENT CLI")
    print("=" * 40)
    print("1. View Full Inventory")
    print("2. View Specific Product Details")
    print("3. Add New Inventory Item")
    print("4. Update Item Price or Stock Level")
    print("5. Delete Product")
    print("6. Find Item Info via OpenFoodFacts Barcode")
    print("7. Exit")
    print("=" * 40)


def get_all_items():
    try:
        response = requests.get(f"{BASE_URL}/inventory")
        if response.status_code == 200:
            items = response.json()
            if not items:
                print("Inventory is currently empty.")
                return
            print(
                f"\n{'ID':<10} | {'Product Name':<25} | {'Brand':<15} | {'Price':<8} | {'Stock':<6}"
            )
            print("-" * 72)
            for item in items:
                print(
                    f"{item['id']:<10} | {item['product_name'][:23]:<25} | {item['brands'][:13]:<15} | ${item['price']:<7.2f} | {item['stock']:<6}"
                )
    except requests.exceptions.ConnectionError:
        print(
            "Error: Cannot connect to the Flask server. Is app.py running?"
        )


def get_single_item():
    item_id = input("Enter the ID of the product to view: ").strip()
    try:
        response = requests.get(f"{BASE_URL}/inventory/{item_id}")
        if response.status_code == 200:
            item = response.json()
            print("\n--- Product Profile ---")
            print(f"ID:           {item['id']}")
            print(f"Barcode:      {item['barcode']}")
            print(f"Name:         {item['product_name']}")
            print(f"Brand:        {item['brands']}")
            print(f"Price:        ${item['price']:.2f}")
            print(f"Stock Level:  {item['stock']} units")
            print(f"Ingredients:  {item['ingredients_text']}")
        else:
            print(f"Error: {response.json().get('error')}")
    except requests.exceptions.ConnectionError:
        print("Error: Backend connection failure.")


def add_item():
    print("\n--- Add New Inventory Entry ---")
    barcode = (
        input("Enter Barcode (Press Enter to bypass and type manually): ")
        .strip()
    )
    try:
        price = float(input("Assign retail price ($): ") or 0.0)
        stock = int(input("Initial stock capacity count: ") or 0)
    except ValueError:
        print("Invalid number input. Aborting operations.")
        return

    payload = {"barcode": barcode, "price": price, "stock": stock}

    if not barcode:
        payload["product_name"] = input("Product Name: ").strip()
        payload["brands"] = input("Brand Name: ").strip()

    try:
        print("Processing...")
        response = requests.post(f"{BASE_URL}/inventory", json=payload)
        if response.status_code == 201:
            item = response.json()
            print(
                f"\nSuccess! Added '{item['product_name']}' (ID: {item['id']})."
            )
            if barcode:
                print(
                    "Data was successfully enriched using the OpenFoodFacts API database."
                )
        else:
            print("Failed to store entry.")
    except requests.exceptions.ConnectionError:
        print("Error: Backend connection failure.")


def update_item():
    item_id = input("Enter target product ID to modify: ").strip()
    print("Leave field blank if you do not want to alter it.")
    raw_price = input("Enter updated price ($): ").strip()
    raw_stock = input("Enter updated stock level: ").strip()

    payload = {}
    try:
        if raw_price:
            payload["price"] = float(raw_price)
        if raw_stock:
            payload["stock"] = int(raw_stock)
    except ValueError:
        print("Formatting mismatch detected. Input execution halted.")
        return

    if not payload:
        print("No alterations specified.")
        return

    try:
        response = requests.parse = requests.patch(
            f"{BASE_URL}/inventory/{item_id}", json=payload
        )
        if response.status_code == 200:
            print("Product properties updated successfully.")
        else:
            print(f"Error: {response.json().get('error')}")
    except requests.exceptions.ConnectionError:
        print("Error: Backend connection failure.")


def delete_item():
    item_id = input("Enter product ID to purge from records: ").strip()
    confirm = (
        input(f"Are you sure you want to delete {item_id}? (y/N): ")
        .strip()
        .lower()
    )
    if confirm != "y":
        print("Operation aborted.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if response.status_code == 200:
            print(response.json().get("message"))
        else:
            print(f"Error: {response.json().get('error')}")
    except requests.exceptions.ConnectionError:
        print("Error: Backend connection failure.")


def find_external_item():
    barcode = input("Enter target barcode value to locate: ").strip()
    if not barcode:
        print("Barcode field cannot be blank.")
        return

    try:
        print(f"Querying OpenFoodFacts system databases for: {barcode}...")
        response = requests.get(f"{BASE_URL}/openfoodfacts/{barcode}")
        if response.status_code == 200:
            data = response.json()["data"]
            print("\n--- OpenFoodFacts Entry Found ---")
            print(f"Product Name:  {data['product_name']}")
            print(f"Brand Identity: {data['brands']}")
            print(f"Ingredients:    {data['ingredients_text']}")
        else:
            print(f"Lookup Failed: {response.json().get('message')}")
    except requests.exceptions.ConnectionError:
        print("Error: Backend connection failure.")


def main():
    while True:
        show_menu()
        choice = input("Select an option (1-7): ").strip()
        if choice == "1":
            get_all_items()
        elif choice == "2":
            get_single_item()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            find_external_item()
        elif choice == "7":
            print("System shutting down. Goodbye.")
            sys.exit(0)
        else:
            print("Selection out of bounds. Pick an action from 1 through 7.")


if __name__ == "__main__":
    main()