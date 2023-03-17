import os
from dotenv import load_dotenv, find_dotenv

from pymongo import MongoClient 
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
import datetime



class DbConnection:
    def __init__(self):
        '''Connects to database'''
        load_dotenv(find_dotenv())
        password = os.environ.get("MONGODB_PWD")
        my_conection = f"mongodb+srv://ezzop6:{password}@cluster0.qr7l0pg.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(my_conection)

    
        
class DbUsersMain(DbConnection):
    def __init__(self):
        super().__init__()
        self.user_db = self.client.main.users
        self.user_key = self.client.main.keys
        
    def create_user(self, user_login, user_password):
        '''Creates user in database if user does not exist'''
        if self.check_if_user_exists(user_login):
            key = self.generate_key()
            password = self.encript_data(user_password,key)
            register_time = self.current_time()
            
            self.user_db.insert_one({"login":user_login, "password":password, "role":"user",
                                    "register_time":register_time, "last_login":register_time})
            
            user_id = self.get_user_id(user_login)
            self.user_key.insert_one({"_id":user_id, "key":key})
            return True
        else:
            return False
            
    def login_user(self, user_login, user_password):
        '''Checks if user exists and if password is correct'''
        if not self.check_if_user_exists(user_login):
            user_id = self.get_user_id(user_login)
            user_key = self.get_user_key(user_id)
            encripted_password = self.get_user_password(user_id)
            decripted_password = self.decript_data(encripted_password, user_key)
            if user_password == decripted_password:
                self.update_user_last_login(user_id)  
                return True
            else:
                return False
        else:
            return False
    
    def check_if_user_exists(self, user_login):
        '''Checks if user exists in database'''
        if self.user_db.count_documents({"login":user_login}) == 0:
            return True
    
    


    def current_time(self):
        '''Returns current time'''
        current_time = datetime.datetime.now()
        current_time = current_time.strftime("%d.%m.%Y %H:%M:%S")
        return current_time

    # key functions for encription and decription
    def generate_key(self):
        '''Creates key for user'''
        key = Fernet.generate_key()
        return key
        
    def encript_data(self, data_to_encript, key):
        '''Creates key for user'''
        fernet = Fernet(key)
        encripted_data = fernet.encrypt(data_to_encript.encode())
        return encripted_data
    
    def decript_data(self, data_to_decript, key):
        fernet = Fernet(key)
        decripted_data = fernet.decrypt(data_to_decript).decode()
        return decripted_data
    
    
    # functions for getting data from database
    def get_user_id(self, user_login):
        '''Returns user id from database'''
        return self.user_db.find_one({"login":user_login})["_id"]
    
    def get_user_key(self, user_id):
        '''Returns user key from database'''
        return self.user_key.find_one({"_id":ObjectId(user_id)})["key"]
    
    def get_user_login(self, user_id):
        '''Returns user login from database'''
        return self.user_db.find_one({"_id":ObjectId(user_id)})["login"]
    
    def get_user_password(self, user_id):
        '''Returns user password from database'''
        return self.user_db.find_one({"_id":ObjectId(user_id)})["password"]
    
    def get_user_role(self, user_id):
        '''Returns user role from database'''
        return self.user_db.find_one({"_id":ObjectId(user_id)})["role"]
    
    # functions for updating data in database
    def update_user_last_login(self, user_id):
        '''Updates user last login time'''
        last_login = self.current_time()
        self.user_db.update_one({"_id":ObjectId(user_id)}, {"$set":{"last_login":last_login}})
    


