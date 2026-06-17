"""Example test file - demonstrates testing patterns."""
import pytest

@pytest.mark.asyncio
async def test_health_check(api_client):
    """Test that API root endpoint responds."""
    response = await api_client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

@pytest.mark.asyncio
async def test_login_success(api_client, test_db):
    """Test successful login with valid credentials."""
    from backend.core_utils import hash_password
    
    # Create test user
    await test_db.users.insert_one({
        "id": "user_test",
        "email": "user@test.com",
        "password_hash": hash_password("testpass"),
        "role": "sales",
        "status": "active"
    })
    
    # Attempt login
    response = await api_client.post("/api/auth/login", json={
        "email": "user@test.com",
        "password": "testpass"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "user@test.com"

@pytest.mark.asyncio
async def test_login_invalid_credentials(api_client):
    """Test login failure with wrong password."""
    response = await api_client.post("/api/auth/login", json={
        "email": "user@test.com",
        "password": "wrongpass"
    })
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_product(api_client, auth_headers, test_db):
    """Test creating a new product."""
    payload = {
        "sku": "TEST-BATIK-001",
        "name": "Test Batik Product",
        "category": "Batik",
        "price": 150000,
        "base_unit": "meter"
    }
    
    response = await api_client.post(
        "/api/products",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "TEST-BATIK-001"
    
    # Verify in database
    product = await test_db.products.find_one({"sku": "TEST-BATIK-001"})
    assert product is not None
    assert product["name"] == "Test Batik Product"

@pytest.mark.asyncio
async def test_list_products_pagination(api_client, auth_headers, test_db):
    """Test product list with pagination."""
    # Seed 25 test products
    products = [
        {
            "id": f"test_p_{i}",
            "sku": f"TEST-{i:03d}",
            "name": f"Product {i}",
            "category": "Test",
            "price": 100000,
            "status": "active"
        }
        for i in range(25)
    ]
    await test_db.products.insert_many(products)
    
    # Request page 2, limit 10
    response = await api_client.get(
        "/api/products?page=2&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 10
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["total"] == 25
    assert data["pagination"]["pages"] == 3

# Add more tests as needed:
# - test_update_product
# - test_delete_product
# - test_create_order
# - test_stock_reservation
# etc.
