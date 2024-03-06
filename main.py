import psycopg2
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="characters",
    user="postgres",
    password="password",
    host="127.0.0.1",
    port="5432" 
)

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path) + "\\"

def format_html(character1_id, character1_name, character1_url,
                character2_id, character2_name, character2_url, rows):
    # Read the HTML content from the file
    with open((script_directory + 'index.html'), 'r') as file:
        html_content = file.read()

    # Find the position where the <body> tag starts
    body_start_index = html_content.find('<body>') + len('<body>')

    # Split the HTML content into header and body sections
    header = html_content[:body_start_index]
    body = html_content[body_start_index:]

    # Format the body section with the character data
    formatted_images = ''
    formatted_images = ''.join([f'<img src="{image}" alt="{name}">' for name, votes, image in rows])
    #formatted_images = ''.join([f'<img src="{image}" alt="Image"> Votes: {votes}' for name, votes, image in rows])

    formatted_body = body.format(
        character1_id=character1_id,
        character1_name=character1_name,
        character1_url=character1_url,
        character2_id=character2_id,
        character2_name=character2_name,
        character2_url=character2_url,
        images=formatted_images
    )

    # Recombine the header and formatted body sections
    formatted_html = header + formatted_body

    return formatted_html


# Create a cursor object to perform database operations
cur = conn.cursor()

class RequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        if self.path.endswith('.js'):
            self.send_header('Content-type', 'application/javascript')
        super().end_headers()

        
    def do_GET(self):
        if self.path == '/style.css':  # Check for the correct path
            # Serve CSS file
            self.send_response(200)
            self.send_header('Content-type', 'text/css')  # Set the correct MIME type
            self.end_headers()

            with open((script_directory + 'style.css'), 'rb') as file:
                css_content = file.read()

            self.wfile.write(css_content)
        else:
            # Serve HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        # Select two random characters from characters_list
        cur.execute("SELECT id, name, image_url FROM characters_list ORDER BY RANDOM() LIMIT 2")
        characters = cur.fetchall()

        character1_id, character1_name, character1_url = characters[0]
        character2_id, character2_name, character2_url = characters[1]

        cur.execute("SELECT cv.character_name, cv.votes, cl.image_url FROM Character_votes cv JOIN characters_list cl ON cv.character_name = cl.name ORDER BY cv.votes DESC;")
        rows = cur.fetchall()
    
        # Read HTML content from the HTML file
        with open((script_directory + 'index.html'), 'r') as file:
            response_content = file.read()

        # Replace placeholders in HTML content with actual values
        response_content = format_html(character1_id, character1_name, character1_url, character2_id, character2_name, character2_url,rows)
        
        self.wfile.write(response_content.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)

        # Assuming the POST request contains a parameter named 'chosenCharacter'
        chosen_char_id = int(parsed_data.get('chosenCharacter', [''])[0])
        other_char_id = int(parsed_data.get('otherCharacter', [''])[0])

        print(chosen_char_id)
        cur.execute("UPDATE character_votes SET votes = votes + 1 WHERE id = %s", (chosen_char_id,))
        cur.execute("UPDATE character_votes SET votes = votes - 1 WHERE id = %s", (other_char_id,))
        conn.commit()

        print("Vote recorded successfully!")

        # Send response back to the client
        self.send_response(303)  # Redirect status code
        self.send_header('Location', '/')  # Redirect to do_GET
        self.end_headers()
if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting server...')
    httpd.serve_forever()