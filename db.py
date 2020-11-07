from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from user import User

client = MongoClient('mongodb+srv://teste:teste@chatapp.8fyq4.mongodb.net/<dbname>?retryWrites=true&w=majority')

chat_db = clien1t.get_database("chatappdb")
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")

def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username,
                                'email': email,
                                'password': password_hash})

# save_user('jhon','a@a.com', 'teste')

def get_user(username):
    # retornar a collection inteira pelo username
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None


def save_room(room_name, create_by, usernames):
    room_id = rooms_collection.insert_one(
        {'room_name': room_name, 'created_by': create_by, 'created_at': datetime.now()}).inserted_id
    
    add_room_member(room_id, room_name, created_by, created_by, is_admin=True)
    return room_id

def update_room(room_id, room_name):
    rooms_collection.update_room({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})

def get_room(room_id):
    rooms_collection.find_one({'_id': ObjectId(room_id)})

def add_room_member(room_id, room_name, username, added_by, is_admin=False):
    room_members_collection.insert_one(
        {'_id':{'room_id': ObjectId(room_id), 'username': username},'room_name': room_name,'added_by': added_by,
         'added_at': datetime.now(),'is_room_admin': is_room_admin})

def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.inser_one(
                {'_id':{'room_id': ObjectId(room_id), 'username': username},'room_name': room_name,'added_by': added_by,
         'added_at': datetime.now(),'is_room_admin': False} for username in usernames)

def remove_room_members(room_id, usernames):
    room_members_collection.delete_many({'_id': {'$in': [{'room_id': room_id, 'username': username} for username in usernames]}})

def get_room_members(room_id):
    room_members_collection.find({'_id.room_id': ObjectId(room_id)})

def get_room_for_user(username):
    room_members_collection.find({'_id.username': username})


def is_room_member(room_id, username):
    room_members_collections.count_documents({'_id': {'room': ObjectId(room_id), username: username}})

def is_room_admin(room_id, username):
    room_members_collections.count_documents({'_id': {'room': ObjectId(room_id), username: username}, 'is_room_admin': True})