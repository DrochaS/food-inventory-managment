import uuid
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Mock database initialized with structured OpenFoodFacts-style data
mock_inventory = [
    {
        "id": "1",
        "barcode": "025293000984",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
        "price": 3.99,
        "stock": 45,
    },
    {
        "id": "2",
        "barcode": "5449000000439",
        "product_name": "Coca-Cola Classic",
        "brands": "The Coca-Cola Company",
        "ingredients_text": "Carbonated water, sugar, color (Caramel E150d), acid (Phosphoric Acid), natural flavorings including caffeine",
        "price": 1.89,
        "stock": 120,
    },
]


def fetch_from_openfoodfacts(barcode):
    """Queries the external OpenFoodFacts API using a product barcode."""
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product_data = data.get("product", {})
                return {
                    "product_name": product_data.get(
                        "product_name", "Unknown Product"
                    ),
                    "brands": product_data.get("brands", "Unknown Brand"),
                    "ingredients_text": product_data.get(
                        "ingredients_text", "No ingredients listed"
                    ),
                }
    except requests.exceptions.RequestException:
        return None
    return None


# --- API ENDPOINTS ---

#GET method to retrieve all items in the inventory
@app.route("/inventory", methods=["GET"])
def get_all_items():
    """Fetch all items from the inventory."""
    return jsonify(mock_inventory), 200


@app.route("/inventory/<string:item_id>", methods=["GET"])
def get_single_item(item_id):
    """Fetch a single item by its ID."""
    item = next((i for i in mock_inventory if i["id"] == item_id), None)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

#POST method to add a new item to the inventory, with optional enrichment from OpenFoodFacts
@app.route("/inventory", methods=["POST"])
def add_item():
    """Add a new item, enriching data from OpenFoodFacts if a barcode is supplied."""
    body = request.get_json() or {}

    barcode = body.get("barcode")
    price = body.get("price", 0.0)
    stock = body.get("stock", 0)

    # Initialize empty base info
    product_name = body.get("product_name", "Unknown Item")
    brands = body.get("brands", "Generic")
    ingredients_text = body.get("ingredients_text", "N/A")

    # If barcode is given, attempt to auto-enrich using OpenFoodFacts API
    if barcode:
        external_data = fetch_from_openfoodfacts(barcode)
        if external_data:
            product_name = external_data["product_name"]
            brands = external_data["brands"]
            ingredients_text = external_data["ingredients_text"]

    new_item = {
        "id": str(uuid.uuid4())[:8],  # Generate a unique shortened identifier
        "barcode": barcode or "Manual Entry",
        "product_name": product_name,
        "brands": brands,
        "ingredients_text": ingredients_text,
        "price": float(price),
        "stock": int(stock),
    }

    mock_inventory.append(new_item)
    return jsonify(new_item), 201




if __name__ == "__main__":
    app.run(port=5000, debug=True)