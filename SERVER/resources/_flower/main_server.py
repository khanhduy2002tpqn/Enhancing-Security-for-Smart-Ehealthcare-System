from server import *
"""
Script to start the server side of the federated learning pipeline with Flower.
"""

if __name__ == '__main__':
    print("start server")
    start_time = time.time()
    # Write log file to the current directory
    filename=args.filename
    print(f"filename = {filename}")
    fl.common.logger.configure(identifier="FL",filename= f"SERVER/resources/log/{filename}.log")    
    fl.server.start_server(server_address="0.0.0.0:8090",
                           config=fl.server.ServerConfig(num_rounds=args.rounds),
                           strategy=strategy)
    print(f"Server Time = {time.time() - start_time} seconds")
    #mv log file to the log folder
