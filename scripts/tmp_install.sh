CURRENT_DIR=$(pwd)

# Update and install necessary packages
echo "Updating and installing necessary packages"
sudo apt-get update -y
sudo apt-get install -y wget git curl python3-pip unzip

# Function to check if fl_env exists
check_env_exists() {
    conda env list | grep "fl_env"
}
# Function to prepare Conda
conda_preparation() {
    if command -v conda >/dev/null 2>&1; then
        echo "Conda is installed."

        # Update Conda to the latest version

        echo "Updating Conda to the latest version"
        conda update -n base -c defaults conda -y
        # Create a new Conda environment named fl_env with Python 3.10 and requirements
        conda create --name fl_env python=3.10 anaconda -y
        conda run -n fl_env pip install -r $CURRENT_DIR/_flower/requirements.txt

    else

        echo "Conda is not installed. Installing Miniconda..."
        # Install Miniconda
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest-Linux-x86_64.sh
        bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

        # Initialize Conda
        export PATH="$HOME/miniconda3/bin:$PATH"
        source $HOME/miniconda3/bin/activate

        # Update Conda to the latest version
        echo "Updating Conda to the latest version"
        conda update -n base -c defaults conda -y

        # Initialize Conda
        ~/miniconda3/bin/conda init
        source ~/.bashrc
        # Create a new Conda environment named fl_env with Python 3.10 and requirements
        echo "Creating a new Conda environment named fl_env with Python 3.10 and requirements"
        conda create --name fl_env python=3.10 anaconda -y
        conda create --name fl_api python=3.10 anaconda -y
        conda run -n fl_env pip install -r $CURRENT_DIR/fl_client/flower-homomorphic_encryption/requirements.txt
        conda run -n fl_api pip install -r $CURRENT_DIR/fl_client/CLIENT/requirements.txt
    fi
}

# Assuming flower-homomorphic_encryption.zip is in the current directory
unzip fl_client.zip -d $CURRENT_DIR 

# Check if fl_env exists

if check_env_exists; then
    echo "Conda environment 'fl_env' already exists."
else
    # Prepare Conda environment
    conda_preparation
    cd $CURRENT_DIR
fi

conda run -n fl_api python $CURRENT_DIR/fl_client/CLIENT/app.py