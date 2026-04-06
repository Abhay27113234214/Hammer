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
from flask_bcrypt import Bcrypt
from chunker import chunk_csv_manual

app = Flask(__name__)
jwt = JWTManager()
jwt.init_app(app)
api = Api(app)
bcrypt = Bcrypt(app)

DATASETS_FOLDER = os.path.join(app.root_path, 'static', 'datasets')
PYFILES_FOLDER = os.path.join(app.root_path, 'static', 'pyfiles')
os.makedirs(DATASETS_FOLDER, exist_ok=True)
os.makedirs(PYFILES_FOLDER, exist_ok=True)

basedir=os.path.abspath(os.path.dirname(__file__))

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir,"instance/app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret-hammer-key-2026"
app.config['SECRET_KEY'] = "super-secret-hammer-key-2026"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))

    def __init__(self, email):
        self.email = email
    def save_hash_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_hash_password(self, password):
        return check_password_hash(self.password_hash, password)
    


class SubmitResource(Resource):
    @jwt_required()
    def post(self):

        identity = get_jwt_identity()

        user = User.query.filter_by(email=identity).first()

        if not user:
            return {"message": "user not found or session expired"}, 404

        dataset = request.files['dataset']
        pyfile = request.files['pyfile']
        chunks = request.form.get("chunks")  
        chunks = int(chunks)      
        dataset_path = os.path.join(DATASETS_FOLDER, dataset.filename)
        pyfile_path = os.path.join(PYFILES_FOLDER, pyfile.filename)
        dataset.save(dataset_path)
        pyfile.save(pyfile_path)
        chunk_csv_manual(identity, dataset_path, chunks)
        return {'message':'successfully submitted'}


class RegisterResources(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user_data = User(email)
        user_data.save_hash_password(password)
        db.session.add(user_data)
        db.session.commit()
        return {"message": "Registered successfully"}, 201
    

class loginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_hash_password(password):
            access_token = create_access_token(identity=user.email)
            return {"message":"login successfull!!", "access_token":access_token}, 200
        elif user.email!=email:
            return "user not exist",321
        elif not user.check_hash_password(password):
            return "password is wrong",404        


api.add_resource(SubmitResource, "/submit")
api.add_resource(RegisterResources,"/register")
api.add_resource(loginResource,"/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


