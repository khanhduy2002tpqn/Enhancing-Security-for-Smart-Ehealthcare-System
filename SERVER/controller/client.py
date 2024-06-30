from database.model import Client
import jwt
from flask import request
import os
import requests
from dotenv import load_dotenv
from database.auth_middleware import token_required
from database.auth_ip import ip_token_validate
from web_base.colored_print import print_colored
load_dotenv()

@token_required
def add_client(_current_user):
    """
        Add client to db
    """
    data = request.json
    if(not data):
        return {
            "message": "No data received"
            }
    client_id = data.get('client_id')
    client_ip = data.get('client_ip')
    
    # request to client to check is online
    # print(f"http://{client_ip}:5000/is_online")
    # status = requests.get(f"http://{client_ip}:5000/is_online")
    # print(status.json())
    client_status = "Added!"
    model = data.get('model')
    _id = str(_current_user["_id"])
    token = request.headers.get('Authorization')
    return {
        "user": Client().create(
            client_id=client_id,
            client_ip=client_ip,
            client_status=client_status,
            model=model,
            _id = _id
            ),
        "script": f"curl -sSL -H 'Authorization: {token}' http://172.31.0.60:5000/sh_file | bash -s -- {token}"
        }

@token_required
def delete_client(_current_user):
    print_colored("------[delete_client]-------", "cyan")
    data = request.json
    client_id = data.get('client_id')
    token = data.get('token')
    ip = Client().get_ip_by_client_id(client_id)
    if(not ip_token_validate(token, ip)):
        return {
            "message": "no ip match"
        }
    return Client().delete_by_client_id(client_id)

@token_required
def get_total_client(_current_user):
    print_colored("------[get_total_client]-------", "cyan")
    return  {"count": Client().count_client(str(_current_user["_id"]))}

@token_required
def get_active_client(_current_user):
    print_colored("------[get_active_client]-------", "cyan")
    return  {"count": Client().count_client_status(str(_current_user["_id"]), "online")}   

@token_required                  
def get_waiting_client(_current_user):
    print_colored("------[get_waiting_client]-------", "cyan")
    return  {"count": Client().count_client_status(str(_current_user["_id"]), "Added!")}

@token_required
def get_training_client(_current_user):
    print_colored("------[get_training_client]-------", "cyan")
    return  {"count": Client().count_client_status(str(_current_user["_id"]), "training")}
@token_required
def get_error_client(_current_user):
    print_colored("------[get_error_client]-------", "cyan")
    return  {"count": Client().count_client_status(str(_current_user["_id"]), "offline")}

@token_required
def client_online(_current_user):
    data = request.json
    client_ip = data.get('client_ip')
    if (Client().if_exist(client_ip)["status"] =="No exist client"):
        return {"status": "Unauthoried client tried to login!"}
    
    res = requests.get(f"http://{client_ip}:5000/is_online")
    print(res.json()["status"])
    if (str(res.json()["status"])!="True"):
        return {"message": "Authorized message but server cant find!"}
    update = Client().update_client_status(client_ip)
    return  {"status": "online"}

@token_required
def is_exist(_current_user):
    print_colored("------[is_exist]-------", "cyan")
    data = request.json
    client_ip = data.get('client_ip')
    return  Client().if_exist(client_ip)

# @token_required
# def is_exist(_current_user):
#     print_colored("------[is_exist]-------", "cyan")
#     data = request.json
#     client_ip = data.get('client_ip')
#     if Client().if_exist(client_ip):
#         response= Client().get_status_by_ip(client_ip)
#         return {"exist": response}
#     return {"exist": "No exist"}

@token_required
def client_login(_current_user):
    print_colored("[1]------[client_login]-------", "cyan")
    data = request.json
    client_ip = data.get('client_ip')
    cred = {
        "username": data.get('username'),
        "password": data.get('password')
    }
    print_colored(str(cred), "green")
    print_colored(str(client_ip), "green")
    print(f"[2] Direct ---> {client_ip}")
    res = requests.post(f"http://{client_ip}:5000/login_client", json=cred)
    # res = res.json()
    print("[7] --- Token have been sent !")
    print(str(res.json()))
    update = Client().update_client_status(_current_user["_id"])
    print(str(update))
    print("[8] --- Return to app")
    return res.json()