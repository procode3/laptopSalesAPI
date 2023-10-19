#!/bin/bash

# Check if nmap is installed
if ! dpkg -l | grep -q "nmap"; then
    echo "nmap is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install nmap -y
    echo "nmap has been installed."
    if ! dpkg -l | grep -q "ncat"; then
    echo "ncat is not installed. Installing..."
    sudo apt-get install ncat -y
    echo "ncat has been installed."    
    fi
fi

if [ -f .env ]; then
    echo "Reading database configuration from .env file..."
    source .env
else
    echo "Error: .env file not found."
    exit 1
fi

# Define database configuration variables
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

if(! nc -z $DB_HOST $DB_PORT); then
    echo "Error: Cannot connect to $DB_HOST:$DB_PORT"
    exit 1
fi

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
    ncat -lk -p 3000 --sh-exec 'echo -ne "HTTP/1.1 200 OK\r\n\r\nContent-Type: application/json\r\n\r\n{\"message\": \"Hello from LaptopSales Bash low-level REST API\"}"' &

    # Sleep briefly to allow ncat to start listening
    sleep 1

    # Echo "Server running" in the same terminal
    echo "Server started on port 3000"
   
}

# Function to create a laptop
create_laptop() {
    read -p "Enter laptop brand: " brand
    read -p "Enter laptop model: " model
    read -p "Enter laptop price: " price

    if [ "$selected_db" == "postgresql" ]; then
        $PSQL_COMMAND -c "INSERT INTO laptops (brand, model, price) VALUES ('$brand', '$model', $price);"
    else
        $MYSQL_COMMAND -e "INSERT INTO laptops (brand, model, price) VALUES ('$brand', '$model', $price);"
    fi

    echo "Laptop created."
}

stop_and_exit() {
    ncat_pid=$(pgrep -f "ncat -lk -p 3000")
    if [ -n "$ncat_pid" ]; then
        echo "Stopping the ncat server..."
        kill "$ncat_pid"
    else
        echo "The ncat server is not running."
    fi
    exit 0
}

# Add other CRUD operations (read, update, delete) similarly

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


