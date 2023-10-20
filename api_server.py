import os
import json
import psycopg2
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


db_settings = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
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
            response_data = {
                'status': '✔success',
                "message": "Successfully retrieved laptops.",
                'data': laptops
            }
            self.wfile.write(json.dumps(response_data).encode())

        elif self.path.startswith('/api/laptops/'):
            laptop_id = int(self.path.split('/')[3])
            conn = psycopg2.connect(**db_settings)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM laptops_sales WHERE id = %s;', (laptop_id,))
            laptop = cursor.fetchone()
            cursor.close()
            conn.close()
            if laptop:
                response_data = {
                    'status': '✔success',
                    "message": "Successfully retrieved laptop.",
                    'data': {
                        'id': laptop[0],
                        'brand': laptop[1],
                        'model': laptop[2],
                        'price': float(laptop[3])
                    }
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            else:
                response_data = {
                    'status': '❌Error',
                    "message": "Laptop not found.",
                    'data': {}
                }
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
        else:
            response_data = {
                'status': '❌Error',
                "message": "Failed to retreive check request",
                'data': []
            }
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

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
            response_data = {
                'status': '❌Error',
                "message": "Failed to post",
                'data': []
            }
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

    def do_PUT(self):
        if self.path.startswith('/api/laptops/'):
            try:
                laptop_id = int(self.path.split('/')[3])
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                updated_laptop = json.loads(put_data)
                if laptop_id:
                    conn = psycopg2.connect(**db_settings)
                    cursor = conn.cursor()
                
                    brand, model, price = updated_laptop['brand'], updated_laptop['model'], updated_laptop['price'] 

                    cursor.execute("""
                    UPDATE laptops_sales SET brand = %s, model = %s, price = %s WHERE id = %s
                    """, (brand, model, price, laptop_id))

                    cursor.execute('SELECT * FROM laptops_sales WHERE id = %s;', (laptop_id,))
                    updated_id, brand, model, price = cursor.fetchone()
                    cursor.close()
                    conn.commit()
                    cursor.close()
                    conn.close()

                    response_data = {
                        "message": "Laptop updated successfully.",
                        "status": "✔success",
                        "data": {
                            "id": updated_id,
                            "brand": brand,
                            "model": model,
                            "price": str(price),
                            "timestamp": str(datetime.datetime.now())
                        }
                    }
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
                    return
                else:
                    response_data = {
                        "message": "Laptop not found check id",
                        "status": "❌Error",
                        "data": {}
                    }
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
            except Exception as e:
                print(e)
                response_data = {
                    "message": "Mising or invalid data.",
                    "status": "❌Error",
                    "data": {}
                }
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

        else:
            response_data = {
                'status': '❌Error',
                "message": "Failed to put",
                'data': []
            }
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

    def do_DELETE(self):
        if self.path.startswith('/api/laptops/'):
            try:
                laptop_id = int(self.path.split('/')[3])
                conn = psycopg2.connect(**db_settings)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM laptops_sales WHERE id = %s;', (laptop_id,))
                laptop = cursor.fetchone()
                if not laptop:
                    response_data = {
                        'status': '❌Error!',
                        "message": "Laptop not found.",
                        'data': {}
                    }
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
                    return
                cursor.execute('DELETE FROM laptops_sales WHERE id = %s;', (laptop_id,))
                cursor.close()
                conn.commit()
                cursor.close()
                conn.close()
                response_data = {
                    'status': '✔success',
                    "message": "Successfully deleted laptop with id: " + str(laptop_id) + ".",  
                    'data': {
                        'id': laptop[0],
                        "brand": laptop[1],
                        "model": laptop[2],
                        "price": str(laptop[3]),
                        "timestamp": str(datetime.datetime.now())
                    }
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
                return
                if laptop:
                    response_data = {
                        'status': '❌Error',
                        "message": "Failed to delete",
                        'data': []
                    }
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
            except Exception as e:
                print(e)
                response_data = {
                    'status': '❌Error',
                    "message": "Failed to delete",
                    'data': []
                }
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

    

def run():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, LaptopAPIHandler)
    print('Starting server on port 8080...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()