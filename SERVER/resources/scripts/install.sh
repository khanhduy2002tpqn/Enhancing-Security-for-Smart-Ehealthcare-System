current_dir=$(pwd)
token=$1
# Update and install necessary packages
echo "Updating and installing necessary packages"
sudo apt-get update -y
sudo apt-get install -y wget git curl python3-pip unzip
# Function to check if fl_env exists
check_fl_env_exists() {
conda env list | grep "fl_env"
}
check_fl_env_exists(){
conda env list | grep "fl_api"
}


# Function to prepare Conda
conda_install_fl_env() {
# Update Conda to the latest version
echo "Updating Conda to the latest version"
# Create a new Conda environment named fl_env with Python 3.10 and requirements
conda create --name fl_env python=3.10 anaconda -y
conda run -n fl_env pip install -r $current_dir/fl_client/flower-homomorphic_encryption/requirements.txt
}

conda_install_fl_api(){
conda create --name fl_api python=3.10 anaconda -y
conda run -n fl_api pip install -r $current_dir/fl_client/CLIENT/requirements.txt
}

# Assuming flower-homomorphic_encryption.zip is in the current directory
# check foler fl_client are exist
if [ -d fl_client ]; then
echo "fl_client already exists."
else
######################
curl -sSL -H "Authorization: ${token}" http://172.31.0.60:5000/zip_file -o fl_client.zip
echo "curl -sSL -H 'Authorization: ${token}' http://172.31.0.60:5000/zip_file -o fl_client.zip"
unzip fl_client.zip -d $current_dir 
fi
# check folder ~/miniconda3 are exist
if [ -d ~/miniconda3 ]; then
echo "Miniconda already exists."
# initialize conda
export PATH="$HOME/miniconda3/bin:$PATH"
source $HOME/miniconda3/bin/activate
~/miniconda3/bin/conda init
source ~/.bashrc
else
# check Miniconda3-latest-Linux-x86_64.sh exists
if [ -f Miniconda3-latest-Linux-x86_64.sh ]; then
echo "Miniconda3-latest-Linux-x86_64.sh already exists."
else
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
export PATH="$HOME/miniconda3/bin:$PATH"
source $HOME/miniconda3/bin/activate
~/miniconda3/bin/conda init
source ~/.bashrc
fi
fi
# Check if fl_env exists
conda update -n base -c defaults conda -y
if conda env list | grep "fl_env"; then
echo "Conda environment 'fl_env' already exists."
conda run -n fl_env pip install -r $current_dir/fl_client/flower-homomorphic_encryption/requirements.txt
else
# Prepare Conda environment
conda_install_fl_env
cd $current_dir
fi
# check if fl_api exists
if conda env list | grep "fl_api"; then
echo "Conda environment 'fl_api' already exists."
conda run -n fl_api pip install -r $current_dir/fl_client/CLIENT/requirements.txt
else
conda_install_fl_api
cd $current_dir
fi

conda run -n fl_env conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch -y

# # check torch, torchvision, torchaudio are exist
# if conda run -n fl_env pip list | grep "torch"; then
# echo "Torch already exists."
# else
# conda run -n fl_env pip install torch --index-url https://download.pytorch.org/whl/cu118
# fi
# # check torchvision are exist
# if conda run -n fl_env pip list | grep "torchvision"; then
# echo "Torchvision already exists."
# else
# conda run -n fl_env pip install torchvision --index-url https://download.pytorch.org/whl/cu118
# fi

# # check torchaudio are exist
# if conda run -n fl_env pip list | grep "torchaudio"; then
# echo "Torchaudio already exists."
# else
# conda run -n fl_env pip install torchaudio --index-url https://download.pytorch.org/whl/cu118
# fi


if conda run -n fl_env  pip list | grep "flwr"; then
echo "Flwr already exists."
else
conda run -n fl_env pip install flwr==1.5.0
fi


echo "Running the API Flower server"
# run the API Flower server background
conda run -n fl_api python $current_dir/fl_client/CLIENT/app.py & 
# curl -H "Authorization: ${token}" http://172.31.0.60:5000/client_online
# in ra pid của app.py
echo "PID of app.py: $!"
ip_address=$(hostname -I | awk '{print $1}')
echo "The IP address of the machine is: $ip_address"


# Post IP address to the server
response=$(curl -H "Authorization: ${token}" \
                -H "Content-Type: application/json" \
                -X POST \
                -d "{\"client_ip\": \"${ip_address}\"}" \
                http://172.31.0.60:5000/client_online)

echo "Server response: $response"


