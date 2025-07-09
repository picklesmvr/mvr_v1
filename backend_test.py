#!/usr/bin/env python3
import unittest
import requests
import json
import os
import requests_mock
from dotenv import load_dotenv

# Load environment variables from frontend .env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class TestMVRNonVegPicklesBackend(unittest.TestCase):
    def setUp(self):
        # Mock user data for authentication
        self.mock_user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/profile.jpg"
        }
        
        # Session token to store after login
        self.session_token = None
    
    def test_01_auth_login(self):
        """Test the authentication login endpoint"""
        print("\n=== Testing Emergent Managed Google Auth Backend ===")
        
        # Mock session ID for testing
        session_id = "test-session-id"
        
        # Create a session with requests_mock to intercept the call to Emergent Auth API
        with requests_mock.Mocker() as m:
            # Mock the Emergent Auth API response
            m.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                json=self.mock_user_data,
                status_code=200
            )
            
            # Make the login request
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"session_id": session_id}
            )
            
            # Check if the request was successful
            self.assertEqual(response.status_code, 200, f"Login failed with status {response.status_code}: {response.text}")
            
            # Parse the response
            data = response.json()
            
            # Verify the response structure
            self.assertIn("user", data, "Response missing 'user' field")
            self.assertIn("session_token", data, "Response missing 'session_token' field")
            
            # Store the session token for subsequent tests
            self.session_token = data["session_token"]
            
            # Verify user data
            self.assertEqual(data["user"]["email"], self.mock_user_data["email"])
            self.assertEqual(data["user"]["name"], self.mock_user_data["name"])
            
            print("✅ Authentication login endpoint working correctly")
    
    def test_02_auth_profile(self):
        """Test the profile endpoint"""
        # Skip if login test failed
        if not self.session_token:
            self.skipTest("Login test failed, skipping profile test")
        
        # Make the profile request
        response = requests.get(
            f"{API_URL}/auth/profile",
            headers={"Authorization": self.session_token}
        )
        
        # Check if the request was successful
        self.assertEqual(response.status_code, 200, f"Profile retrieval failed with status {response.status_code}: {response.text}")
        
        # Parse the response
        data = response.json()
        
        # Verify user data
        self.assertEqual(data["email"], self.mock_user_data["email"])
        self.assertEqual(data["name"], self.mock_user_data["name"])
        
        print("✅ Authentication profile endpoint working correctly")
    
    def test_03_menu_api(self):
        """Test the menu API endpoint"""
        print("\n=== Testing Menu API endpoints ===")
        
        # Make the menu request
        response = requests.get(f"{API_URL}/menu")
        
        # Check if the request was successful
        self.assertEqual(response.status_code, 200, f"Menu retrieval failed with status {response.status_code}: {response.text}")
        
        # Parse the response
        menu_items = response.json()
        
        # Verify menu items count
        self.assertEqual(len(menu_items), 5, f"Expected 5 menu items, got {len(menu_items)}")
        
        # Expected menu items with prices
        expected_items = {
            "Chicken": 800.0,
            "Chicken Boneless": 1000.0,
            "Prawns Small Size": 1200.0,
            "Prawns Big Size": 1400.0,
            "Mutton": 1500.0
        }
        
        # Verify each menu item and its price
        for item in menu_items:
            self.assertIn("name", item, "Menu item missing 'name' field")
            self.assertIn("price", item, "Menu item missing 'price' field")
            
            item_name = item["name"]
            self.assertIn(item_name, expected_items, f"Unexpected menu item: {item_name}")
            self.assertEqual(item["price"], expected_items[item_name], 
                            f"Price mismatch for {item_name}: expected {expected_items[item_name]}, got {item['price']}")
        
        print("✅ Menu API endpoint working correctly with exact pricing")
    
    def test_04_cart_management(self):
        """Test cart management APIs"""
        print("\n=== Testing Cart Management APIs ===")
        
        # Skip if login test failed
        if not self.session_token:
            self.skipTest("Login test failed, skipping cart tests")
        
        # 1. Add item to cart
        add_cart_response = requests.post(
            f"{API_URL}/cart/add",
            json={"menu_item_id": "chicken", "quantity": 2},
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(add_cart_response.status_code, 200, 
                        f"Add to cart failed with status {add_cart_response.status_code}: {add_cart_response.text}")
        
        cart_data = add_cart_response.json()
        self.assertIn("items", cart_data, "Cart response missing 'items' field")
        self.assertIn("total_amount", cart_data, "Cart response missing 'total_amount' field")
        
        # Verify cart item
        self.assertEqual(len(cart_data["items"]), 1, "Expected 1 item in cart")
        self.assertEqual(cart_data["items"][0]["menu_item_id"], "chicken")
        self.assertEqual(cart_data["items"][0]["quantity"], 2)
        self.assertEqual(cart_data["items"][0]["price"], 800.0)
        
        # Verify total amount (2 * 800 = 1600)
        self.assertEqual(cart_data["total_amount"], 1600.0, 
                        f"Total amount mismatch: expected 1600.0, got {cart_data['total_amount']}")
        
        print("✅ Add to cart API working correctly")
        
        # 2. Get cart
        get_cart_response = requests.get(
            f"{API_URL}/cart",
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(get_cart_response.status_code, 200, 
                        f"Get cart failed with status {get_cart_response.status_code}: {get_cart_response.text}")
        
        get_cart_data = get_cart_response.json()
        self.assertIn("items", get_cart_data, "Cart response missing 'items' field")
        self.assertEqual(len(get_cart_data["items"]), 1, "Expected 1 item in cart")
        
        print("✅ Get cart API working correctly")
        
        # 3. Add another item to cart
        add_cart_response2 = requests.post(
            f"{API_URL}/cart/add",
            json={"menu_item_id": "mutton", "quantity": 1},
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(add_cart_response2.status_code, 200, 
                        f"Add to cart failed with status {add_cart_response2.status_code}: {add_cart_response2.text}")
        
        cart_data2 = add_cart_response2.json()
        self.assertEqual(len(cart_data2["items"]), 2, "Expected 2 items in cart")
        
        # Verify total amount (2 * 800 + 1 * 1500 = 3100)
        self.assertEqual(cart_data2["total_amount"], 3100.0, 
                        f"Total amount mismatch: expected 3100.0, got {cart_data2['total_amount']}")
        
        # 4. Remove item from cart
        remove_cart_response = requests.delete(
            f"{API_URL}/cart/item/chicken",
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(remove_cart_response.status_code, 200, 
                        f"Remove from cart failed with status {remove_cart_response.status_code}: {remove_cart_response.text}")
        
        remove_cart_data = remove_cart_response.json()
        self.assertEqual(len(remove_cart_data["items"]), 1, "Expected 1 item in cart after removal")
        self.assertEqual(remove_cart_data["items"][0]["menu_item_id"], "mutton")
        
        # Verify total amount (1 * 1500 = 1500)
        self.assertEqual(remove_cart_data["total_amount"], 1500.0, 
                        f"Total amount mismatch after removal: expected 1500.0, got {remove_cart_data['total_amount']}")
        
        print("✅ Remove from cart API working correctly")
    
    def test_05_courier_charges(self):
        """Test location-based courier charges API"""
        print("\n=== Testing Location-based Courier Charges ===")
        
        # Test courier charges for Andhra Pradesh
        ap_response = requests.get(f"{API_URL}/courier-charges/Andhra Pradesh")
        self.assertEqual(ap_response.status_code, 200, 
                        f"Courier charges for AP failed with status {ap_response.status_code}: {ap_response.text}")
        
        ap_data = ap_response.json()
        self.assertEqual(ap_data["charges_per_kg"], 80.0, 
                        f"Courier charges for AP mismatch: expected 80.0, got {ap_data['charges_per_kg']}")
        
        # Test courier charges for Telangana
        ts_response = requests.get(f"{API_URL}/courier-charges/Telangana")
        self.assertEqual(ts_response.status_code, 200, 
                        f"Courier charges for Telangana failed with status {ts_response.status_code}: {ts_response.text}")
        
        ts_data = ts_response.json()
        self.assertEqual(ts_data["charges_per_kg"], 100.0, 
                        f"Courier charges for Telangana mismatch: expected 100.0, got {ts_data['charges_per_kg']}")
        
        # Test courier charges for other states
        other_response = requests.get(f"{API_URL}/courier-charges/Karnataka")
        self.assertEqual(other_response.status_code, 200, 
                        f"Courier charges for other states failed with status {other_response.status_code}: {other_response.text}")
        
        other_data = other_response.json()
        self.assertEqual(other_data["charges_per_kg"], 150.0, 
                        f"Courier charges for other states mismatch: expected 150.0, got {other_data['charges_per_kg']}")
        
        print("✅ Courier charges API working correctly for all regions")
    
    def test_06_order_management(self):
        """Test order management system"""
        print("\n=== Testing Order Management System ===")
        
        # Skip if login test failed
        if not self.session_token:
            self.skipTest("Login test failed, skipping order tests")
        
        # 1. Add items to cart first
        requests.post(
            f"{API_URL}/cart/add",
            json={"menu_item_id": "chicken", "quantity": 2},
            headers={"Authorization": self.session_token}
        )
        
        requests.post(
            f"{API_URL}/cart/add",
            json={"menu_item_id": "prawns_small", "quantity": 1},
            headers={"Authorization": self.session_token}
        )
        
        # 2. Create an order
        order_data = {
            "delivery_address": "123 Test Street, Test City",
            "pincode": "500001",
            "phone": "9876543210",
            "state": "Telangana"
        }
        
        create_order_response = requests.post(
            f"{API_URL}/orders",
            json=order_data,
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(create_order_response.status_code, 200, 
                        f"Create order failed with status {create_order_response.status_code}: {create_order_response.text}")
        
        order = create_order_response.json()
        
        # Verify order details
        self.assertIn("id", order, "Order response missing 'id' field")
        self.assertIn("items", order, "Order response missing 'items' field")
        self.assertIn("subtotal", order, "Order response missing 'subtotal' field")
        self.assertIn("courier_charges", order, "Order response missing 'courier_charges' field")
        self.assertIn("total_amount", order, "Order response missing 'total_amount' field")
        
        # Verify items in order (2 chicken + 1 prawns_small)
        self.assertEqual(len(order["items"]), 2, f"Expected 2 items in order, got {len(order['items'])}")
        
        # Calculate expected values
        expected_subtotal = 2 * 800.0 + 1 * 1200.0  # 2 chicken + 1 prawns_small
        expected_courier_charges = 100.0 * 3  # Telangana rate * total quantity
        expected_total = expected_subtotal + expected_courier_charges
        
        # Verify calculations
        self.assertEqual(order["subtotal"], expected_subtotal, 
                        f"Subtotal mismatch: expected {expected_subtotal}, got {order['subtotal']}")
        
        self.assertEqual(order["courier_charges"], expected_courier_charges, 
                        f"Courier charges mismatch: expected {expected_courier_charges}, got {order['courier_charges']}")
        
        self.assertEqual(order["total_amount"], expected_total, 
                        f"Total amount mismatch: expected {expected_total}, got {order['total_amount']}")
        
        # Verify order status
        self.assertEqual(order["status"], "pending", f"Expected order status 'pending', got {order['status']}")
        
        print("✅ Order creation API working correctly")
        
        # 3. Get order history
        get_orders_response = requests.get(
            f"{API_URL}/orders",
            headers={"Authorization": self.session_token}
        )
        
        self.assertEqual(get_orders_response.status_code, 200, 
                        f"Get orders failed with status {get_orders_response.status_code}: {get_orders_response.text}")
        
        orders = get_orders_response.json()
        self.assertIsInstance(orders, list, "Orders response should be a list")
        self.assertGreaterEqual(len(orders), 1, "Expected at least 1 order in history")
        
        # Verify the latest order matches the one we just created
        latest_order = orders[0]
        self.assertEqual(latest_order["id"], order["id"], "Order ID mismatch in order history")
        
        print("✅ Order history API working correctly")
        
        # 4. Verify cart is cleared after order creation
        get_cart_response = requests.get(
            f"{API_URL}/cart",
            headers={"Authorization": self.session_token}
        )
        
        cart_after_order = get_cart_response.json()
        self.assertEqual(len(cart_after_order["items"]), 0, "Cart should be empty after order creation")
        
        print("✅ Cart clearing after order creation working correctly")


if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import requests_mock
    except ImportError:
        print("Installing required packages...")
        os.system("pip install requests_mock")
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)