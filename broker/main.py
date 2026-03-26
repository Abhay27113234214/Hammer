from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename

jwt = JWTManager()

app = Flask(__name__)
jwt.init_app(app)
api = Api(app)
DATASETS_FOLDER = os.path.join(app.root_path, 'static', 'datasets')
PYFILES_FOLDER = os.path.join(app.root_path, 'static', 'pyfiles')
os.makedirs(DATASETS_FOLDER, exist_ok=True)
os.makedirs(PYFILES_FOLDER, exist_ok=True)

class SubmitResource(Resource):
    def post(self):
        dataset = request.files['dataset']
        pyfile = request.files['pyfile']
        dataset_path = os.path.join(DATASETS_FOLDER, dataset.filename)
        pyfile_path = os.path.join(PYFILES_FOLDER, pyfile.filename)
        dataset.save(dataset_path)
        pyfile.save(pyfile_path)


api.add_resource(SubmitResource, "/submit")

if __name__ == "__main__":
    app.run(debug=True)