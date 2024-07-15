#!/bin/bash
current_dir=$(pwd)
# Install necessary packages (assuming it's a setup script)
sudo apt-get update -y
sudo apt-get install -y jq curl

# Prompt user for username and password
read -p "Username: " username
read -sp "Password: " password
echo

# URL of the login API
login_url="http://172.31.0.60:5000/login"

# Call login API with curl and fetch response
response=$(curl -s -X POST $login_url -H "Content-Type: application/json" -d "{\"username\": \"$username\", \"password\": \"$password\"}")

# Extract token from response using jq
token=$(echo $response | jq -r '.data.token')

# Check if token is empty
if [ -z "$token" ]; then
  echo "Failed to fetch auth token. Please check your credentials."
  exit 1
fi

# Gather hostname and IP address
ip_address=$(hostname -I | awk '{print $1}')
host_name=$(hostname)

# URL of the add_client API
add_client_url="http://172.31.0.60:5000/add_client"

# Gather system performance metrics
memory=$(free -m | awk 'NR==2{print $2}')
core_cpu=$(nproc)
if nvidia-smi &> /dev/null; then
    echo "GPU is available"
    device_name=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader)
else
    echo "GPU is not available"
    device_name="CPU"
fi

# Prepare JSON data to send
client_data=$(cat <<EOF
{
    "client_id": "$host_name",
    "client_ip": "$ip_address",
    "model": "ResNet",
    "performance": {
        "memory": $memory,
        "core_cpu": $core_cpu,
        "device_name": "$device_name"
    }
}
EOF
)

echo "Sending client data:"
echo $client_data

# Call add_client API with curl
add_client_response=$(curl -s -X POST $add_client_url -H "Content-Type: application/json" -H "Authorization: $token" -d "$client_data")

echo "Response from add_client API:"
echo $add_client_response

# Extract script from response using jq
script=$(echo $add_client_response | jq -r '.script')

# Check if script is empty
if [ -z "$script" ]; then
  echo "No script found in the response. Please check the response."
  exit 1
fi

# Execute the script returned by the server
echo "Executing script from server:"
echo "$script"
eval "$script"
