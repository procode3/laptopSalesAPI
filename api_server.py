import os
import json
import psycopg2
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


db_settings = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
}
    
def setup_database():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    # Create the 'laptops' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laptops_sales (
        id serial PRIMARY KEY,
        brand VARCHAR (255) NOT NULL,
        model VARCHAR (255) NOT NULL,
        price DECIMAL (10, 2) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laptop_brands (
        id serial PRIMARY KEY,
        name VARCHAR (255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

setup_database()

class LaptopAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/laptops':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Get all laptops from the database
            conn = psycopg2.connect(**db_settings)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM laptops_sales;')
            laptops = cursor.fetchall()
            laptops = [
                {
                    'id': row[0],
                    'brand_id': row[1],
                    'model': row[2],
                    'price': float(row[3])
                }
                for row in laptops
            ]
            cursor.close()
            conn.close()
            # Return the laptops as JSON
            
            self.wfile.write(json.dumps(laptops).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/laptops':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
               
                new_laptop = json.loads(post_data)
                print(new_laptop)

            
                brand = new_laptop['brand']
                model = new_laptop['model']
                price = new_laptop['price']

                conn = psycopg2.connect(**db_settings)
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO laptops_sales (brand, model, price) VALUES (%s, %s, %s)
                """, (brand, model, price))
                cursor.execute('SELECT * FROM laptops_sales WHERE brand = %s AND model = %s AND price = %s ORDER by id DESC limit 1;', (brand, model, price) )
                inserted_id, brand, model, price = cursor.fetchone()
                cursor.close()
                conn.commit()
                cursor.close()
                conn.close()
            


                response_data = {
                    "message": "New Laptop added successfully.",
                    "data": {
                        "id": inserted_id,
                        "brand": brand,
                        "model": model,
                        "price": str(price),
                        "timestamp": str(datetime.datetime.now())
                    }
                }
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            except json.JSONDecodeError:
                
                self.send_response(400)  # Bad Request
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/laptops/'):
            laptop_id = int(self.path.split('/')[2])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            updated_laptop = json.loads(put_data)
            for laptop in laptops:
                if laptop['id'] == laptop_id:
                    laptop.update(updated_laptop)
                    self.send_response(200)
                    self.end_headers()
                    return
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/laptops/'):
            laptop_id = int(self.path.split('/')[2])
            for laptop in laptops:
                if laptop['id'] == laptop_id:
                    laptops.remove(laptop)
                    self.send_response(204)
                    self.end_headers()
                    return
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, LaptopAPIHandler)
    print('Starting server on port 8080...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()