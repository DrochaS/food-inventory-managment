import pytest
from unittest.mock import patch
from app import app, mock_inventory

@pytest.fixture
def client():
    """Sets up a clean, isolated Flask test client before every single test run."""
    app.config["TESTING"] = True
    # Save a copy of the starting inventory state to reset it after each test
    original_inventory = mock_inventory.copy()
    
    with app.test_client() as client:
        yield client
        
    # Reset the mock inventory back to normal so tests don't pollute each other
    mock_inventory.clear()
    mock_inventory.extend(original_inventory)

# ==========================================
# 1. TESTING READ ACTIONS (GET ROUTES)
# ==========================================

def test_get_all_items(client):
    """Verifies GET /inventory returns a 200 OK and a list of products."""
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) > 0

def test_get_single_item_success(client):
    """Verifies GET /inventory/<id> finds an existing item successfully."""
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"

def test_get_single_item_not_found(client):
    """Verifies GET /inventory/<id> returns a 404 error if the ID is invalid."""
    response = client.get("/inventory/99999")
    assert response.status_code == 404
    assert "error" in response.get_json()

# ==========================================
# 2. TESTING CREATE ACTIONS (POST ROUTE)
# ==========================================

@patch('app.fetch_from_openfoodfacts')
def test_create_item_with_api_enrichment(mock_fetch, client):
    """Verifies POST /inventory intercepts the barcode and auto-enriches data."""
    # Mocking the external internet API so the test runs instantly offline
    mock_fetch.return_value = {
        "product_name": "Test Avocado Oil",
        "brands": "Test Brand",
        "ingredients_text": "100% Avocado Oil"
    }
    
    new_payload = {"barcode": "111111", "price": "9.99", "stock": "10"}
    response = client.post("/inventory", json=new_payload)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Test Avocado Oil"  # Proves API enrichment worked!
    assert data["price"] == 9.99

# ==========================================
# 3. TESTING UPDATE ACTIONS (PATCH ROUTE)
# ==========================================

def test_update_item_price_and_stock(client):
    """Verifies PATCH /inventory/<id> mutates metrics while preserving text."""
    update_payload = {"price": "5.50", "stock": "100"}
    response = client.patch("/inventory/1", json=update_payload)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 5.50
    assert data["stock"] == 100
    assert data["product_name"] == "Organic Almond Milk"  # Name remained untouched

# ==========================================
# 4. TESTING DELETE ACTIONS (DELETE ROUTE)
# ==========================================

def test_delete_item_success(client):
    """Verifies DELETE /inventory/<id> completely removes an item from memory."""
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    
    # Verify it's actually gone by trying to fetch it again
    check_response = client.get("/inventory/1")
    assert check_response.status_code == 404