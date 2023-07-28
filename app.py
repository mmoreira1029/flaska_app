import pymongo, json, os
from urllib.parse import quote_plus
from flask import Flask, request, jsonify
from waitress import serve
from bson import ObjectId

app = Flask(__name__)
db_user = 'mmoreira'
db_pass = os.getenv('mongopass')
 
uri = 'mongodb+srv://' + db_user + ':' + db_pass + '@cluster1.re8hp.mongodb.net/'

client = pymongo.MongoClient(uri)
group_coll = client["users_and_groups"]["groups"]
user_coll = client["users_and_groups"]["users"]

class user:
    def __init__(self, name="", region="", email="", age="", group=""):
        self.name = name
        self.region = region
        self.email = email
        self.age = age
        self.group = group
    
    def to_json(self):
        return {
            "name": self.name,
            "region": self.region,
            "email": self.email,
            "age": self.age,
            "group": self.group
        }

class group:
    def __init__(self, name="", region="", users=[]):
        self.name = name
        self.region = region
        self.users = users

    def to_json(self):
        return {
            "name": self.name,
            "region": self.region,
            "users": self.users
        }

def post_user(data):
    try:
        #user
        new_user = user(name=data['name'], region=data['region'], email=data['email'], age=data['age'], group=data['group'])
        user_coll.insert_one(new_user.to_json())

        #group
        user_group = group(name=data['group'], region=data['region'], users=[new_user.to_json()])          
        
        existing_groups = group_coll.find()

        for item in existing_groups:
            if item['name'] == data['group']:
                group_coll.update_one({"name": data['group']}, {'$push': {'users': new_user.to_json()}})
            else:
                group_coll.insert_one(user_group.to_json())

    except Exception as ex:
        return ({'ERROR': 'An error occurred while trying to insert a new user: '+str(ex)}), 500

@app.route('/')
def home():
    return "Hello, welcome!"

@app.route('/users', methods=['GET'])
def get_users():
    try:

        users_from_db = user_coll.find()
        user_list = []
        
        for usr in users_from_db:
            user_list.append(
                {
                    "name": usr['name'],
                    "region": usr['region'],
                    "email": usr['email'],
                    "age": usr['age'],
                    "group": usr['group']
                }
            )
            #print(usr)
    
        return user_list

    except Exception as ex:
        return ({'ERROR': 'An error occurred while trying to get users from DB: '+str(ex)}), 500

@app.route('/users/<name>', methods=['GET'])
def get_user_by_name(name):
    try:
        if name:
            user_from_db = user_coll.find_one({"name": str(name)})

            found_user = {
                    "name": user_from_db['name'],
                    "region": user_from_db['region'],
                    "email": user_from_db['email'],
                    "age": user_from_db['age'],
                    "group": user_from_db['group']
                }
            
            return found_user
        else:
            return ({'ERROR': 'An NAME must be provided.'}), 400

    except Exception as ex:
        return ({'ERROR': 'An error occurred while trying to get users from DB: '+str(ex)}), 500

@app.route('/groups', methods=['GET'])
def get_groups():
    try:

        groups_from_db = group_coll.find()
        group_list = []
        
        for grp in groups_from_db:
            group_list.append(
                {
                    "name": grp['name'],
                    "region": grp['region'],
                    "users": grp['users']
                }
            )
    
        return group_list

    except Exception as ex:
        return ({'ERROR': 'An error occurred while trying to get groups from DB: '+str(ex)}), 500

@app.route('/groups/<name>', methods=['GET'])
def get_group_by_name(name):
    try:
        if name:
            groups_from_db = group_coll.find_one({"name": str(name)})

            found_group = {
                    "name": groups_from_db['name'],
                    "region": groups_from_db['region'],
                    "users": groups_from_db['users']
                }
            
            return found_group
        else:
            return ({'ERROR': 'An NAME must be provided.'}), 400

    except Exception as ex:
        return ({'ERROR': 'An error occurred while trying to get groups from DB: '+str(ex)}), 500

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json() 
        
        if data is None:
            return jsonify({'ERROR': 'No JSON document was provided'}), 400

        else:
            post_user(data)
            return "New user subscribed!"

    except Exception as ex:
        return ({'ERROR': 'An error occurred during the process: '+str(ex)}), 500

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8080)
