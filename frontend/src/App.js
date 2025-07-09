import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [sessionToken, setSessionToken] = useState(localStorage.getItem('sessionToken'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (sessionToken) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [sessionToken]);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API}/auth/profile`, {
        headers: { Authorization: sessionToken }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('sessionToken');
        setSessionToken(null);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      localStorage.removeItem('sessionToken');
      setSessionToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, token) => {
    setUser(userData);
    setSessionToken(token);
    localStorage.setItem('sessionToken', token);
  };

  const logout = () => {
    setUser(null);
    setSessionToken(null);
    localStorage.removeItem('sessionToken');
  };

  return (
    <AuthContext.Provider value={{ user, sessionToken, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Landing Page Component
const LandingPage = () => {
  const { user } = useAuth();

  const handleSignIn = () => {
    const redirectUrl = encodeURIComponent(window.location.origin + '/profile');
    window.location.href = `https://auth.emergentagent.com/?redirect=${redirectUrl}`;
  };

  if (user) {
    return <HomePage />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">🥒</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">MVR</h1>
              <p className="text-green-600 text-sm font-medium">non veg pickles</p>
            </div>
          </div>
          <button
            onClick={handleSignIn}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Sign In / Sign Up
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-5xl font-bold text-gray-800 mb-4">
              <span className="text-red-500">MVR</span> Non Veg Pickles
            </h2>
            <p className="text-2xl text-green-600 mb-8 font-medium">
              Spice up your plate..
            </p>
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <img 
                src="https://images.unsplash.com/photo-1610216339841-a0456a6c86a9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxzcGljeSUyMGZvb2R8ZW58MHx8fHJlZHwxNzUyMDI4ODgyfDA&ixlib=rb-4.1.0&q=85"
                alt="Spicy Pickles"
                className="w-full h-64 object-cover rounded-lg mb-6"
              />
              <p className="text-gray-600 text-lg mb-6">
                Authentic homemade non-veg pickles made with traditional recipes and the finest spices.
              </p>
              <button
                onClick={handleSignIn}
                className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-lg font-medium text-lg transition-colors"
              >
                Sign In or Sign Up to Order
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-white">
        <div className="container mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">Why Choose MVR Pickles?</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-red-500 text-2xl">🌶️</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Authentic Spices</h4>
              <p className="text-gray-600">Traditional recipes with handpicked spices</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-green-500 text-2xl">🥩</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Fresh Ingredients</h4>
              <p className="text-gray-600">Only the freshest meat and vegetables</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-orange-500 text-2xl">🚚</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Fast Delivery</h4>
              <p className="text-gray-600">Quick delivery across India</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 px-4">
        <div className="container mx-auto text-center">
          <p className="mb-2">Contact: Madhulatha +91 9963701148</p>
          <p className="mb-4">Bhimavaram</p>
          <p className="text-gray-400">© 2024 MVR Non Veg Pickles. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

// Profile Page Component (handles login redirect)
const ProfilePage = () => {
  const { login } = useAuth();

  useEffect(() => {
    const handleAuth = async () => {
      const hash = window.location.hash;
      if (hash && hash.includes('session_id=')) {
        const sessionId = hash.split('session_id=')[1];
        
        try {
          const response = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (response.ok) {
            const data = await response.json();
            login(data.user, data.session_token);
          } else {
            console.error('Login failed');
          }
        } catch (error) {
          console.error('Login error:', error);
        }
      }
    };

    handleAuth();
  }, [login]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Processing login...</p>
      </div>
    </div>
  );
};

// Home Page Component (after login)
const HomePage = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('menu');
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState({ items: [], total_amount: 0 });
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchMenu();
    fetchCart();
    fetchOrders();
  }, []);

  const fetchMenu = async () => {
    try {
      const response = await fetch(`${API}/menu`);
      const data = await response.json();
      setMenu(data);
    } catch (error) {
      console.error('Error fetching menu:', error);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await fetch(`${API}/cart`, {
        headers: { Authorization: localStorage.getItem('sessionToken') }
      });
      const data = await response.json();
      setCart(data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await fetch(`${API}/orders`, {
        headers: { Authorization: localStorage.getItem('sessionToken') }
      });
      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const addToCart = async (menuItemId, quantity = 1) => {
    try {
      const response = await fetch(`${API}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: localStorage.getItem('sessionToken')
        },
        body: JSON.stringify({ menu_item_id: menuItemId, quantity })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCart(data);
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const removeFromCart = async (menuItemId) => {
    try {
      const response = await fetch(`${API}/cart/item/${menuItemId}`, {
        method: 'DELETE',
        headers: { Authorization: localStorage.getItem('sessionToken') }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCart(data);
      }
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">🥒</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">MVR</h1>
              <p className="text-green-600 text-sm font-medium">non veg pickles</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">Welcome, {user?.name}</span>
            <button
              onClick={logout}
              className="text-red-500 hover:text-red-600 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentView('menu')}
              className={`py-4 px-2 border-b-2 font-medium ${
                currentView === 'menu' ? 'border-red-500 text-red-500' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Menu
            </button>
            <button
              onClick={() => setCurrentView('cart')}
              className={`py-4 px-2 border-b-2 font-medium ${
                currentView === 'cart' ? 'border-red-500 text-red-500' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Cart ({cart.items?.length || 0})
            </button>
            <button
              onClick={() => setCurrentView('orders')}
              className={`py-4 px-2 border-b-2 font-medium ${
                currentView === 'orders' ? 'border-red-500 text-red-500' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              My Orders
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="container mx-auto px-4 py-8">
        {currentView === 'menu' && <MenuView menu={menu} addToCart={addToCart} />}
        {currentView === 'cart' && <CartView cart={cart} removeFromCart={removeFromCart} setCurrentView={setCurrentView} />}
        {currentView === 'checkout' && <CheckoutView cart={cart} setCurrentView={setCurrentView} fetchOrders={fetchOrders} />}
        {currentView === 'orders' && <OrdersView orders={orders} />}
      </main>
    </div>
  );
};

// Menu View Component
const MenuView = ({ menu, addToCart }) => {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-8 text-center">Our Menu</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {menu.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-2">{item.name}</h3>
            <p className="text-gray-600 mb-4">{item.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold text-red-500">₹{item.price}/KG</span>
              <button
                onClick={() => addToCart(item.id)}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Add to Cart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Cart View Component
const CartView = ({ cart, removeFromCart, setCurrentView }) => {
  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="text-center py-16">
        <h2 className="text-3xl font-bold mb-4">Your Cart</h2>
        <p className="text-gray-600 mb-8">Your cart is empty</p>
        <button
          onClick={() => setCurrentView('menu')}
          className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium"
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Your Cart</h2>
      <div className="bg-white rounded-lg shadow-md p-6">
        {cart.items.map((item) => (
          <div key={item.menu_item_id} className="flex justify-between items-center border-b py-4">
            <div>
              <h3 className="font-semibold">{item.menu_item_id}</h3>
              <p className="text-gray-600">Quantity: {item.quantity} KG</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="font-bold">₹{item.price * item.quantity}</span>
              <button
                onClick={() => removeFromCart(item.menu_item_id)}
                className="text-red-500 hover:text-red-600"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
        <div className="mt-6 pt-4 border-t">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xl font-bold">Total: ₹{cart.total_amount}</span>
            <button
              onClick={() => setCurrentView('checkout')}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium"
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Checkout View Component
const CheckoutView = ({ cart, setCurrentView, fetchOrders }) => {
  const [formData, setFormData] = useState({
    delivery_address: '',
    pincode: '',
    phone: '',
    state: ''
  });
  const [courierCharges, setCourierCharges] = useState(0);
  const [totalWeight, setTotalWeight] = useState(0);

  useEffect(() => {
    const weight = cart.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
    setTotalWeight(weight);
  }, [cart]);

  useEffect(() => {
    if (formData.state) {
      fetchCourierCharges();
    }
  }, [formData.state]);

  const fetchCourierCharges = async () => {
    try {
      const response = await fetch(`${API}/courier-charges/${formData.state}`);
      const data = await response.json();
      setCourierCharges(data.charges_per_kg);
    } catch (error) {
      console.error('Error fetching courier charges:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: localStorage.getItem('sessionToken')
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        await fetchOrders();
        setCurrentView('orders');
      }
    } catch (error) {
      console.error('Error creating order:', error);
    }
  };

  const totalCourierCharges = courierCharges * totalWeight;
  const grandTotal = cart.total_amount + totalCourierCharges;

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Checkout</h2>
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4">Delivery Information</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Delivery Address</label>
              <textarea
                value={formData.delivery_address}
                onChange={(e) => setFormData({...formData, delivery_address: e.target.value})}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
                rows="3"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Pincode</label>
              <input
                type="text"
                value={formData.pincode}
                onChange={(e) => setFormData({...formData, pincode: e.target.value})}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">State</label>
              <select
                value={formData.state}
                onChange={(e) => setFormData({...formData, state: e.target.value})}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="">Select State</option>
                <option value="andhra pradesh">Andhra Pradesh</option>
                <option value="telangana">Telangana</option>
                <option value="other">Other States</option>
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-red-500 hover:bg-red-600 text-white py-3 rounded-lg font-medium"
            >
              Place Order
            </button>
          </form>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4">Order Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Subtotal:</span>
              <span>₹{cart.total_amount}</span>
            </div>
            <div className="flex justify-between">
              <span>Weight:</span>
              <span>{totalWeight} KG</span>
            </div>
            <div className="flex justify-between">
              <span>Courier Charges:</span>
              <span>₹{totalCourierCharges}</span>
            </div>
            <div className="border-t pt-2">
              <div className="flex justify-between font-bold text-lg">
                <span>Total:</span>
                <span>₹{grandTotal}</span>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">Courier Charges:</h4>
            <p className="text-sm text-gray-600">
              • Andhra Pradesh: ₹80/KG<br/>
              • Telangana: ₹100/KG<br/>
              • Rest of India: ₹150/KG
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Orders View Component
const OrdersView = ({ orders }) => {
  if (orders.length === 0) {
    return (
      <div className="text-center py-16">
        <h2 className="text-3xl font-bold mb-4">My Orders</h2>
        <p className="text-gray-600">No orders yet</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">My Orders</h2>
      <div className="space-y-4">
        {orders.map((order) => (
          <div key={order.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold">Order #{order.id.substring(0, 8)}</h3>
                <p className="text-sm text-gray-600">
                  {new Date(order.created_at).toLocaleDateString()}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm ${
                order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
              }`}>
                {order.status}
              </span>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Items:</h4>
                {order.items.map((item, index) => (
                  <p key={index} className="text-sm text-gray-600">
                    {item.menu_item_id} - {item.quantity} KG
                  </p>
                ))}
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Delivery:</h4>
                <p className="text-sm text-gray-600">{order.delivery_address}</p>
                <p className="text-sm text-gray-600">{order.pincode}</p>
                <p className="text-sm text-gray-600">{order.phone}</p>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between">
                <span>Subtotal: ₹{order.subtotal}</span>
                <span>Courier: ₹{order.courier_charges}</span>
                <span className="font-bold">Total: ₹{order.total_amount}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState('home');

  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/profile') {
      setCurrentPage('profile');
    } else {
      setCurrentPage('home');
    }
  }, []);

  return (
    <AuthProvider>
      <div className="App">
        {currentPage === 'profile' ? <ProfilePage /> : <LandingPage />}
      </div>
    </AuthProvider>
  );
}

export default App;