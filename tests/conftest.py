"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from backend.server import app
from backend.core_utils import hash_password

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Provide isolated test database per test function."""
    test_client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db_instance = test_client["kn_test_db"]
    
    yield test_db_instance
    
    # Cleanup: Drop test database after test
    await test_client.drop_database("kn_test_db")
    test_client.close()

@pytest.fixture(scope="function")
async def api_client(test_db):
    """Provide FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
async def admin_token(test_db, api_client):
    """Provide authenticated admin token."""
    # Create test admin user
    await test_db.users.insert_one({
        "id": "test_admin",
        "email": "admin@test.com",
        "name": "Test Admin",
        "password_hash": hash_password("testpass123"),
        "role": "admin",
        "status": "active"
    })
    
    # Login and get token
    response = await api_client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "testpass123"
    })
    
    data = response.json()
    return data["token"]

@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Provide authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
async def sample_product(test_db):
    """Create sample product for testing."""
    product = {
        "id": "test_product_01",
        "sku": "TEST-001",
        "name": "Test Batik",
        "category": "Batik",
        "price": 100000,
        "base_unit": "meter",
        "status": "active"
    }
    await test_db.products.insert_one(product)
    return product

@pytest.fixture(scope="function")
async def sample_customer(test_db):
    """Create sample customer for testing."""
    customer = {
        "id": "test_customer_01",
        "code": "CUST-TEST-001",
        "name": "Test Customer",
        "email": "customer@test.com",
        "phone": "081234567890",
        "city": "Jakarta",
        "type": "Retailer",
        "status": "active",
        "addresses": [{
            "id": "addr_01",
            "label": "Alamat Utama",
            "recipient_name": "Test Customer",
            "phone": "081234567890",
            "city": "Jakarta",
            "address": "Jl. Test No. 123",
            "is_primary": True
        }]
    }
    await test_db.customers.insert_one(customer)
    return customer
