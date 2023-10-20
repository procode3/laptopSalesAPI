#!/bin/bash

if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Installing..."
    sudo apt update
    sudo apt install python3 -y
    echo "Python 3 has been installed."
    sudo apt install python3-pip -y
    
    else
    echo "Installing dependencies..."
        
fi

if command -v pip3 &>/dev/null; then
    echo "pip is already installed."
    else
        # Install pip for Python 3
    sudo apt update
    sudo apt install python3-pip -y
    echo "pip has been installed."
        
fi

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "psycopg2 is not installed. Attempting to install..."

    # Try installing psycopg2-binary
    pip3 install psycopg2-binary

    # Check if the installation was successful
    if ! python3 -c "import psycopg2" 2>/dev/null; then
        echo "Failed to install psycopg2. Please install it manually."
        exit 1
    fi
    echo "psycopg2 has been installed successfully."
else
    echo "psycopg2 is already installed."
fi


if [ ! -f .env.example ] || [ ! -f .env ]; then
  repo_url="https://github.com/procode3/laptopSalesAPI.git"
  clone_dir="./server"

  shopt -s dotglob

  if [ -d "$clone_dir" ]; then
    echo "Repository directory already exists."
  else
    git clone "$repo_url" "$clone_dir"
    echo "Repository cloned."
  fi

  if [ -d "$clone_dir" ]; then
    if [ -f "$clone_dir/.env.example" ]; then
      cp -r "$clone_dir"/* .
      cp .env.example .env
      echo "Repository files copied to the current directory, and .env.example renamed to .env."
    fi
  fi

  shopt -u dotglob
else
  echo ".env.example and/or .env files already exist in the current directory. Not running the script."
fi



if [ -f .env ]; then
    echo "Reading database configuration from .env file..."
    source .env
else
    echo "Error: .env file not found."
    exit 1
fi

#set env variables with values from .env file
export DB_HOST=${DB_HOST}
export DB_PORT=${DB_PORT}
export DB_NAME=${DB_NAME}
export DB_USER=${DB_USER}
export DB_PASSWORD=${DB_PASSWORD}

# Define database configuration variables
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

echo "$DB_HOST:$DB_PORT:$DB_NAME:$DB_USER:$DB_PASSWORD" > "$HOME/.pgpass"
chmod 600 "$HOME/.pgpass"

#Function to connect to a PostgreSQL database
connect_postgresql() {
  
    PSQL_COMMAND="psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER"

     if timeout 5 $PSQL_COMMAND -c "\q"; then
        echo "Successfully connected to the database."
    else
        echo "Error: Failed to connect to the database within the timeout period or host is incorrect."
        exit 1
    fi
}

# Function to connect to a MySQL database
start_server() {

    api_response='{"message": "Hello from the REST API"}'

    # Create a custom request handler for the REST API endpoint


    python3 api_server.py &

    # Sleep briefly to allow ncat to start listening
    sleep 1

    # Echo "Server running" in the same terminal
    echo "Server started on port 8080"
}




# Function to delete a specific laptop by ID


stop_and_exit() {
    PID=$(pgrep -f 'python3')
    if [ -z "$PID" ]; then
        echo "Bye..."
    else
        kill $PID
        echo "Server stopped."
    fi
    exit 0
}


# Main menu
while true; do
    echo "Laptop Sales CRUD"
    echo "1. Connect to PostgreSQL DB"
    echo "2. Start laptop sales Server"
    # Add options for other CRUD operations here
    echo "3. Close Server and Exit"
    read -p "Choose an option (1/2/3): " choice

    case $choice in
        1) selected_db="postgresql"; connect_postgresql ;;
        2) selected_db="mysql"; start_server ;;
         # Add cases for other CRUD operations
        3) stop_and_exit ;;
    esac
done