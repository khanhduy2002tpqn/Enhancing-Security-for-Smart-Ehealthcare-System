# import requests
# import json

# # Example JWT token
# jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjY2ZDk0Y2NhNjY2NTYxZThlZGY3MzAxIn0.KCzs2hl0MGow_qRo0TYnMnTIbwxvHPxcmbYymvNBfS8"

# # Define your Flask server URL
# url = "http://192.168.0.16:5000/is_online"

# # Set the Authorization header with the JWT token
# headers = {
#     'Authorization': jwt_token
# }

# # Send GET request to the protected endpoint
# response = requests.get(url, headers=headers)
# data = response.json()
# # Check the response
# if response.status_code == 200:
#     print("Response:", data['status'])
# elif response.status_code == 401:
#     print("Authentication failed:", response.json()['message'])
# else:
#     print("Failed to fetch data. Status code:", response.status_code)
#     print(response.text)


# watch dog
# from resources.file_watcher import FileWatcher

# Example usage
# if __name__ == "__main__":
#     path_to_watch = "/home/ubuntu/fl-project/log.txt"
#     file_watcher = FileWatcher(path_to_watch)
#     file_watcher.start()
# import time
# starttime = time.time()
# model =   Model().create("Lung x-ray", f"{starttime}")

# print(str(model))