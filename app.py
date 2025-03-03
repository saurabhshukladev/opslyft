from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
jwt = JWTManager(app)


cache = {}  # {ip_addr,{time of first request,count}}


# rate limiter in before request
@app.before_request
def pre_request():
    ip_addr = request.remote_addr
    
    if ip_addr in cache.keys():
        json_data = json.loads((cache[ip_addr]))
        time_of_first_request = datetime.fromisoformat(
            json_data.get("time_of_first_request")
        )
        count = json_data.get("count")
        timediff = (
            (time_of_first_request + timedelta(seconds=10)) - datetime.now()
        ).total_seconds()
        if timediff > 0 and count < 3:
            count += 1
            cache[ip_addr] = json.dumps(
                {
                    "time_of_first_request": time_of_first_request.isoformat(),
                    "count": count,
                }
            )
        elif timediff <= 0:
            cache[ip_addr] = json.dumps(
                {"time_of_first_request": datetime.now().isoformat(), "count": 1}
            )
        else:
            return "Too Many Requests", 429

    else:
        cache[ip_addr] = json.dumps(
            {"time_of_first_request": datetime.now().isoformat(), "count": 1}
        )


@app.route("/get-auth-token", methods=["GET"])
def get_auth_token():
    ip_addr = request.remote_addr
    access_token = create_access_token(identity=ip_addr)
    return jsonify(access_token=access_token)


@app.route("/", methods=["GET"])
@jwt_required()
def index():
    ip_addr = get_jwt_identity()
    return jsonify(
        {
            "message": f"Your IP address is, {ip_addr}!",
            "rate_limiter_info": cache[ip_addr],
        }
    )