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
    else
        
    fi
else


fi

#Function to connect to a PostgreSQL database
connect_postgresql() {
    read -p "Enter PostgreSQL username: " pg_user
    read -s -p "Enter PostgreSQL password: " pg_password
    echo
    read -p "Enter PostgreSQL database name: " pg_db

    # You may need to adjust the host and port if your database is not on localhost:5432
    PSQL_COMMAND="psql -h localhost -U $pg_user -d $pg_db"

    # Function to create the laptop table
    $PSQL_COMMAND -c "CREATE TABLE IF NOT EXISTS laptops (id serial primary key, brand text, model text, price numeric);"
}

# Function to connect to a MySQL database
connect_mysql() {
    read -p "Enter MySQL username: " mysql_user
    read -s -p "Enter MySQL password: " mysql_password
    echo
    read -p "Enter MySQL database name: " mysql_db

    # You may need to adjust the host and port if your database is not on localhost:3306
    MYSQL_COMMAND="mysql -h localhost -u $mysql_user -p$mysql_password $mysql_db"

    # Function to create the laptop table
    $MYSQL_COMMAND -e "CREATE TABLE IF NOT EXISTS laptops (id INT AUTO_INCREMENT PRIMARY KEY, brand VARCHAR(255), model VARCHAR(255), price DECIMAL(10, 2));"
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

# Add other CRUD operations (read, update, delete) similarly

# Main menu
while true; do
    echo "Laptop Sales CRUD"
    echo "1. Connect to PostgreSQL"
    echo "2. Connect to MySQL"
    echo "3. Create Laptop"
    # Add options for other CRUD operations here
    echo "4. Exit"
    read -p "Choose an option (1/2/3/4): " choice

    case $choice in
        1) selected_db="postgresql"; connect_postgresql ;;
        2) selected_db="mysql"; connect_mysql ;;
        3) create_laptop ;;
        # Add cases for other CRUD operations
        4) exit ;;
        *) echo "Invalid choice. Please select a valid option." ;;
    esac
done

#BD environment variables from a .env file

#Install nmap using apt

#Start the HTTP server

ncat -lk -p 3000 --sh-exec 'echo -ne "HTTP/1.1 200 OK\r\n\r\nContent-Type: application/json\r\n\r\n{\"message\": \"Hello from LaptopSales Bash low level REST API\"}"'

