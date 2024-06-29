from flask import request
import requests
import os
import threading
import time
from database.model import Client
from dotenv import load_dotenv
from database.auth_middleware import token_required
from web_base.colored_print import print_colored
import concurrent.futures
load_dotenv()

def run_command(command):
    try:
        os.system(command)
        return {"message": "Success"}
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e)
        }, 500

def send_request(ip, epoch_number, device, h_e):
    try:
        body = {
            "id_client": Client().get_by_ip(ip),
            "max_epochs": epoch_number,
            "device": device,
            "he": h_e
        }
        print_colored(f"Start on {ip}", "green")
        
        # update client status
        update = Client().update_client_status(ip, "training")
        res = requests.post(f"http://{ip}:5000/client_train", json=body)
        
        if res.json()["status"] != "Successfully":
            print(f"Train process failed on {ip}")
            print_colored(str(res.json()), "red")
            return {"ip": ip, "status": "failed", "response": res.json()}
        print_colored(f"Start training process successfully on {ip}", "green")
        return {"ip": ip, "status": "success", "response": res.json()}
    except Exception as e:
        return {"ip": ip, "status": "error", "error": str(e)}

def process_ips(ip_array, epoch_number, device, h_e):
    results = []
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(send_request, ip, epoch_number, device, h_e) for ip in ip_array]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        return {"message": "Train process successfully!", "results": results}
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e)
        }, 500

@token_required
def start_train(_current_user):
    data = request.json
    
    round_number = data.get('round_number')
    epoch_number = data.get('epoch_number')
    frac_fit = data.get('frac_fit')
    frac_eval = data.get('frac_eval')
    device = data.get('device')
    ip_array = data.get('ip_array')
    h_e = data.get('he')
    print_colored(str(data), "yellow")
    
    command = ""
    if(not data):
        return {
            "message": "No data received"
        }
    if h_e == "False":
        command = f"""conda run -n fl_env python SERVER/resources/_flower/main_server.py  server --num_workers 0 
                        --max_epochs {epoch_number} 
                        --number_clients {len(ip_array)} 
                        --min_fit_clients 2 
                        --min_avail_clients 2 
                        --min_eval_clients 2 
                        --rounds {round_number} 
                        --frac_fit {frac_fit} 
                        --frac_eval {frac_eval}
                        --device {device}"""
    else:
        command = f"""conda run -n fl_env python SERVER/resources/_flower/main_server.py  server 
                        --num_workers 0 
                        --max_epochs {epoch_number} 
                        --number_clients {ip_array} 
                        --min_fit_clients 2 
                        --min_avail_clients 2 
                        --min_eval_clients 2 
                        --rounds {round_number} 
                        --frac_fit {frac_fit} 
                        --frac_eval {frac_eval}
                        --device {device}"""
    # os.command(command)
    print_colored(command, "yellow")
    command_thread = threading.Thread(target=run_command, args=(command,))
    command_thread.start()
    
    time.sleep(10)
    response = process_ips(ip_array, epoch_number, device, h_e)
    print_colored(str(response), "yellow")
    #wait the training process to finish
    command_thread.join()
    #update client status
    for ip in ip_array:
        update = Client().update_client_status(ip, "online")
    return response

@token_required
def monitor_train(_current_user):
    # read log file log.txt
    return {"message": "Monitor training process"}

    