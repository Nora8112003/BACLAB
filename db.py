from pymongo import MongoClient
from bson.objectid import ObjectId


MONGO_URI = "mongodb+srv://admin:2qhAarVQ23UzLHhq@cluster0.cxmy1yt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

db = client['nhandienvikhuan']
users_collection = db['users']
categories_collection = db['categories']
orders_collection = db['orders']
feedback_collection = db["feedbacks"]

#User

def get_users():
    users = list(users_collection.find())
    return users

def create_user(data):
    # Kiem tra username hoac email da ton tai chua 
    existing_user = users_collection.find_one({"username": data.get("username")})
    if existing_user:
        return {"error": "Tên người dùng đã được sử dụng"}

    user = {
        "username": data.get("username"),
        "password": data.get("password"),  #Luu mat khau ma hoa 
        "email": data.get("email"),
        "role": data.get("role", "user"),
        "is_premium": False,
        "premium_until": None,
        "free_uses": 5  #Mac dinh so lan su dung mien phi 
    }
    users_collection.insert_one(user)
    return {"message": "Tạo người dùng thành công"}

def get_user_by_id(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {'_id': 0})
    if user:
        return user
    return {"error": "Không tìm thấy người dùng"}
def update_user_role(user_id, new_role):
    try:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role}}
        )
        return True
    except Exception as e:
        print("Error:", e)
        return False
def update_user(user_id, data):
    update_data = {
        "username": data.get("username"),
        "password": data.get("password"),
        "email": data.get("email"),
        "role": data.get("role"),
        "free_uses": 5
    }
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    if result.modified_count:
        return {"message": "User updated successfully"}
    return {"error": "User not found or no changes made"}

def delete_user(user_id):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    return {"error": "User not found"}

#Categories 

def get_categories():
    categories = list(categories_collection.find({}, {'_id': 0}))
    return categories

#Orders

def get_orders():
    orders = list(orders_collection.find())
    return orders

def update_order(order_id, data):
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": data}
    )
    return result.modified_count

def delete_order(order_id):
    result = orders_collection.delete_one({"_id": ObjectId(order_id)})
    return result.deleted_count

#Password

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(user_id, password):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user.get("password") == hash_password(password)
    return False

def update_password(user_id, new_password):
    hashed = hash_password(new_password)
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed}}
    )

