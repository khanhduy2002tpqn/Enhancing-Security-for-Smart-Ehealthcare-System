from database.model import User
import jwt
from flask import request
import os
from web_base.colored_print import print_colored
from dotenv import load_dotenv
load_dotenv()


def add_user():
    print_colored("------[add_user]-------", "cyan")
    data = request.json
    username = data.get('username')
    password = data.get('password')
    return User().create(username, password)

def login():
    print_colored("[5] ------[login]-------", "cyan")
    data = request.json
    if not data:
        return {
            "message": "Please provide user details",
            "data": None,
            "error": "Bad request"
        }, 400
    username = data.get('username')
    password = data.get('password')
    user = User().login(username,password)
    if user:
        try:
            user["token"] = jwt.encode(
                {"user_id": user["_id"]},
                os.getenv('SECRET_KEY'),
                algorithm="HS256"
            )
            token = user["token"]
            print("[5.1] return script! ")
            return {
                "message": "Successfully fetched auth token",
                "data": user
                # "script": f"curl -sSL -H 'Authorization: {token}' http://172.31.0.60:5000/sh_file | bash -s -- {token}"
            }
        except Exception as e:
            print(f"Something went wrong: {e}")
            return {
                "error": "Something went wrong",
                "message": str(e)
            }, 500
    return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404