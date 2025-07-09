from fastapi import FastAPI, APIRouter, HTTPException, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import requests

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MenuItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

class CartItem(BaseModel):
    menu_item_id: str
    quantity: int
    price: float

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem]
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem]
    subtotal: float
    courier_charges: float
    total_amount: float
    delivery_address: str
    pincode: str
    phone: str
    state: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Session(BaseModel):
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuthRequest(BaseModel):
    session_id: str

class AddToCartRequest(BaseModel):
    menu_item_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    delivery_address: str
    pincode: str
    phone: str
    state: str

# Helper functions
def get_courier_charge(state: str) -> float:
    state_lower = state.lower()
    if 'andhra' in state_lower or 'ap' in state_lower:
        return 80.0
    elif 'telangana' in state_lower or 'ts' in state_lower:
        return 100.0
    else:
        return 150.0

async def get_user_from_session(session_token: str) -> Optional[User]:
    session = await db.sessions.find_one({"session_token": session_token})
    if not session or session['expires_at'] < datetime.utcnow():
        return None
    
    user = await db.users.find_one({"id": session['user_id']})
    return User(**user) if user else None

# Authentication endpoints
@api_router.post("/auth/login")
async def login(request: AuthRequest):
    try:
        # Call Emergent auth API
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": request.session_id}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_data = response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data["email"]})
        
        if not existing_user:
            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture")
            )
            await db.users.insert_one(user.dict())
        else:
            user = User(**existing_user)
        
        # Create session
        session_token = str(uuid.uuid4())
        session = Session(
            session_token=session_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        await db.sessions.insert_one(session.dict())
        
        return {
            "user": user.dict(),
            "session_token": session_token
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/profile")
async def get_profile(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user.dict()

# Menu endpoints
@api_router.get("/menu")
async def get_menu():
    menu_items = [
        {
            "id": "chicken",
            "name": "Chicken",
            "price": 800.0,
            "description": "Fresh chicken pickle per KG",
            "image_url": ""
        },
        {
            "id": "chicken_boneless",
            "name": "Chicken Boneless",
            "price": 1000.0,
            "description": "Boneless chicken pickle per KG",
            "image_url": ""
        },
        {
            "id": "prawns_small",
            "name": "Prawns Small Size",
            "price": 1200.0,
            "description": "Small size prawn pickle per KG",
            "image_url": ""
        },
        {
            "id": "prawns_big",
            "name": "Prawns Big Size",
            "price": 1400.0,
            "description": "Big size prawn pickle per KG",
            "image_url": ""
        },
        {
            "id": "mutton",
            "name": "Mutton",
            "price": 1500.0,
            "description": "Fresh mutton pickle per KG",
            "image_url": ""
        }
    ]
    return menu_items

# Cart endpoints
@api_router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest, authorization: str = Header(None)):
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get menu item
    menu_items = await get_menu()
    menu_item = next((item for item in menu_items if item["id"] == request.menu_item_id), None)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart:
        cart = Cart(user_id=user.id, items=[], total_amount=0.0)
        await db.carts.insert_one(cart.dict())
    else:
        cart = Cart(**cart)
    
    # Add or update item in cart
    existing_item = next((item for item in cart.items if item.menu_item_id == request.menu_item_id), None)
    if existing_item:
        existing_item.quantity += request.quantity
    else:
        cart_item = CartItem(
            menu_item_id=request.menu_item_id,
            quantity=request.quantity,
            price=menu_item["price"]
        )
        cart.items.append(cart_item)
    
    # Calculate total
    cart.total_amount = sum(item.quantity * item.price for item in cart.items)
    cart.updated_at = datetime.utcnow()
    
    await db.carts.replace_one({"user_id": user.id}, cart.dict())
    
    return cart.dict()

@api_router.get("/cart")
async def get_cart(authorization: str = Header(None)):
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart:
        return {"items": [], "total_amount": 0.0}
    
    return cart

@api_router.delete("/cart/item/{menu_item_id}")
async def remove_from_cart(menu_item_id: str, authorization: str = Header(None)):
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = Cart(**cart)
    cart.items = [item for item in cart.items if item.menu_item_id != menu_item_id]
    cart.total_amount = sum(item.quantity * item.price for item in cart.items)
    cart.updated_at = datetime.utcnow()
    
    await db.carts.replace_one({"user_id": user.id}, cart.dict())
    
    return cart.dict()

# Order endpoints
@api_router.post("/orders")
async def create_order(request: CheckoutRequest, authorization: str = Header(None)):
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get cart
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = Cart(**cart)
    
    # Calculate courier charges
    courier_charges = get_courier_charge(request.state)
    total_weight = sum(item.quantity for item in cart.items)
    total_courier_charges = courier_charges * total_weight
    
    # Create order
    order = Order(
        user_id=user.id,
        items=cart.items,
        subtotal=cart.total_amount,
        courier_charges=total_courier_charges,
        total_amount=cart.total_amount + total_courier_charges,
        delivery_address=request.delivery_address,
        pincode=request.pincode,
        phone=request.phone,
        state=request.state
    )
    
    await db.orders.insert_one(order.dict())
    
    # Clear cart
    await db.carts.delete_one({"user_id": user.id})
    
    return order.dict()

@api_router.get("/orders")
async def get_orders(authorization: str = Header(None)):
    user = await get_user_from_session(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    orders = await db.orders.find({"user_id": user.id}).to_list(100)
    return [Order(**order) for order in orders]

@api_router.get("/courier-charges/{state}")
async def get_courier_charges(state: str):
    charges = get_courier_charge(state)
    return {"state": state, "charges_per_kg": charges}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()