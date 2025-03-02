from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime



app = Flask(__name__)
jwt = JWTManager(app)

@app.before_request 
def pre_request():
    print("Pre Request")

 
@app.route('/',methods=['GET'])
def index():
    return "Hello World"


if __name__ == '__main__':
    app.run(host='::', port=5000, debug=True)