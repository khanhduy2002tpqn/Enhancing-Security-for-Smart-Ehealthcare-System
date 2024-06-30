from flask import request
import requests
import os
import threading
import time
from database.model import Client, Model
from dotenv import load_dotenv
from database.auth_middleware import token_required
from web_base.colored_print import print_colored
import concurrent.futures
import re
from resources.file_watcher import _FileWatcher
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
def read_log_file(filename):
    # read log file SERVER/resources/log/filename.log
    log_file_path = f"SERVER/resources/log/{filename}.log"
    
    fit_progress_pattern = re.compile(r'fit progress: \((\d+), ([\d\.]+), \{\'accuracy\': ([\d\.]+)\}, ([\d\.]+)\)')
    # regular expression to match the desired log entries metrics_centralized 
    metrics_centralized = re.compile(r'metrics_centralized')
    json = ""
    while True:
        if not os.path.exists(log_file_path):
            continue
        else:
            break
    with open(log_file_path, 'r') as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                continue
            metrics_centralized_match = metrics_centralized.search(line)
            if metrics_centralized_match:
                #stop the loop
                break
            fit_progress_match = fit_progress_pattern.search(line)
            if fit_progress_match:
                round_str = fit_progress_match.group(1)
                loss_str = fit_progress_match.group(2)
                accuracy_str = fit_progress_match.group(3)
                time_str = fit_progress_match.group(4)
                print(f"Round: {round_str}, Loss: {loss_str}, Accuracy: {accuracy_str}, Time: {time_str}")
                # update to the database
                json = {
                    "round": round_str,
                    "loss": loss_str,
                    "accuracy": accuracy_str,
                    "time": time_str
                }
                update = Model().update_fit_progress(filename, json)
    
    return {"message": "Monitor training process"}

@token_required
def start_train(_current_user):
    # start time training
    # start_time = time.time()
    
    data = request.json
    round_number = data.get('round_number')
    epoch_number = data.get('epoch_number')
    frac_fit = data.get('frac_fit')
    frac_eval = data.get('frac_eval')
    device = data.get('device')
    ip_array = data.get('ip_array')
    h_e = data.get('he')
    print_colored(str(data), "yellow")
    
    # create object to store the training process
    # DO SOMETHING HERE
    starttime = time.time()
    # return _id
    _id = Model().create("Lung x-ray", f"{starttime}")['_id']
    # Extract the _id
    filename = str(_id) 
    ##############################
    # filename = ""
    command = ""
    if(not data):
        return {
            "message": "No data received"
        }
    if h_e == "False":
        command = f"conda run -n fl_env python SERVER/resources/_flower/main_server.py  server --num_workers 0 --max_epochs {epoch_number} --number_clients {len(ip_array)} --min_fit_clients {len(ip_array)} --min_avail_clients {len(ip_array)} --min_eval_clients {len(ip_array)} --rounds {round_number} --frac_fit {frac_fit} --frac_eval {frac_eval} --device {device} --filename {filename}"
    else:
        command = f"conda run -n fl_env python SERVER/resources/_flower/main_server.py  server --num_workers 0 --max_epochs {epoch_number} --number_clients {len(ip_array)} --min_fit_clients {len(ip_array)} --min_avail_clients {len(ip_array)} --min_eval_clients {len(ip_array)} --rounds {round_number} --frac_fit {frac_fit} --frac_eval {frac_eval} --device {device} --filename {filename} --he"
    # os.command(command)
    print_colored(command, "yellow")
    command_thread = threading.Thread(target=run_command, args=(command,))
    command_thread.start()
    ##
    # watch_dog
    # log_path = ""
    # _FileWatcher(log_path).start()
    
    time.sleep(10)
    # create thread monitor training process
    monitor_thread = threading.Thread(target=read_log_file, args=(filename,))
    monitor_thread.start()
    
    response = process_ips(ip_array, epoch_number, device, h_e)
    print_colored(str(response), "yellow")
    #wait the training process to finish
    command_thread.join()
    monitor_thread.join()
    #update client status
    for ip in ip_array:
        update = Client().update_client_status(ip, "online")
    
    ## finish time training
    end_time = time.time()
    Model().update_endtime(_id, str(end_time))
    
    return {
        "message": "Train process successfully!",
        "data": response,
        "model_id": _id
    }

@token_required
def monitor_train(_current_user):
    # IP 
    # read log file log.txt
    return {"message": "Monitor training process"}

@token_required
def get_fit_prgress_by_id(_current_user):
    data = request.json
    model_id = data.get('model_id')
    return { "data": Model().get_fit_prgress_by_id(model_id)}