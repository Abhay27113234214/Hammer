from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import LoginManager, UserMixin, login_user,login_required, logout_user, current_user
import secrets
import re
from datetime import timedelta


app = Flask(__name__)
jwt = JWTManager(app)
jwt.init_app(app)
api = Api(app)


DATASETS_FOLDER = os.path.join(app.root_path, 'static', 'datasets')
PYFILES_FOLDER = os.path.join(app.root_path, 'static', 'pyfiles')
os.makedirs(DATASETS_FOLDER, exist_ok=True)
os.makedirs(PYFILES_FOLDER, exist_ok=True)



app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)


# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()#Initializes the login system.
login_manager.init_app(app)
login_manager.login_view = 'login' 



# User model with authentication and authorization features
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
    api_key = db.Column(db.String(6), unique=True) 

    def __init__(self, email,api_key):
        self.api_key=api_key
        self.email = email


# Method hash and store password securely
    def save_hash_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_hash_password(self, password):
        return check_password_hash(self.password_hash, password)
    




class SubmitResource(Resource):
    def post(self):
        dataset = request.files['dataset']
        pyfile = request.files['pyfile']
        dataset_path = os.path.join(DATASETS_FOLDER, dataset.filename)
        pyfile_path = os.path.join(PYFILES_FOLDER, pyfile.filename)
        dataset.save(dataset_path)
        pyfile.save(pyfile_path)


class RegisterResources(Resource):
    def post(self):
        email = request.form['email']
        password = request.form['password']
        api_key = secrets.token_hex(3)     

        # Create new user and save hashed password
        user_data = User(email,api_key)
        user_data.save_hash_password(password)
        db.session.add(user_data)
        db.session.commit()
        return {"message": "Registered successfully", "api_key": api_key}, 201
    

class loginResource(Resource):
        
    def post(self):
        self.email = request.form['email']
        self.password = request.form['password']
        user_data = User.query.filter_by(email=self.email).first()
        name = user_data.email.split('@')[0]
        access_token = create_access_token(identity=user_data.email)

        if user_data and user_data.check_hash_password(self.password):
            return f"user exist login sucessfull : {name}and{access_token}",200
        elif user_data.email!=self.email:
            return "user not exist",321
        elif user_data.password!=self.password:
            return "password is wrong",404



class login_with_key(Resource):
    def post(self):
        self.api_key=request.form['api_key']
        user_key = User.query.filter_by(api_key=self.api_key).first()

        
        name = user_key.email.split('@')[0]
        access_token = create_access_token(identity=user_key.email) 
        if user_key:
            return f"login sucessfull: {name}and{access_token}",200
        else:
            return "wrong key",400
        
        
        
        

api.add_resource(SubmitResource, "/submit")
api.add_resource(RegisterResources,"/register")
api.add_resource(loginResource,"/login")
api.add_resource(login_with_key,"/loginkey")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


