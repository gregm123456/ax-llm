from transformers import AutoTokenizer
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import argparse

class TokenizerGLM3_Http():

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm3-6b",
                                                       trust_remote_code=True)

    def encode(self, prompt):
        token_ids = self.tokenizer.build_chat_input(
            prompt)["input_ids"][0].tolist()
        return token_ids
    
    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids)
    
    def bos_id(self):
        return self.tokenizer.bos_token_id
    
    def eos_id(self):
        return self.tokenizer.eos_token_id

tikenizer = TokenizerGLM3_Http()


class Request(BaseHTTPRequestHandler):
    # Define a new request handler class by inheriting from BaseHTTPRequestHandler
    timeout = 5
    server_version = 'Apache'

    def do_GET(self):
        print(self.path)
        # Define the GET handler (runs when a client sends a GET request)
        self.send_response(200)
        self.send_header("type","get") # Set response header; optional
        self.end_headers() 

        if self.path == '/bos_id':
            bos_id = tikenizer.bos_id()
            # print(bos_id)
            # to json
            if bos_id is None:
                msg = json.dumps({'bos_id': -1})
            else:
                msg = json.dumps({'bos_id': bos_id})
        elif self.path == '/eos_id':
            eos_id = tikenizer.eos_id()
            if eos_id is None:
                msg = json.dumps({'eos_id': -1})
            else:
                msg = json.dumps({'eos_id': eos_id})
        else:
            msg = 'error'

        print(msg)
        msg = str(msg).encode() # Convert to string then to bytes

        self.wfile.write(msg) # Return byte-formatted message to client

    def do_POST(self):
        # Define the POST handler (runs when a client sends a POST request)
        data = self.rfile.read(int(self.headers['content-length'])) # Read request body (bytes)
        data =  data.decode() # Decode bytes to string

        self.send_response(200)
        self.send_header("type","post") # Set response header; optional
        self.end_headers()

        if self.path == '/encode':
            req = json.loads(data)
            prompt = req['text']
            token_ids = tikenizer.encode(prompt)
            if token_ids is None:
                msg = json.dumps({'token_ids': -1})
            else:
                msg = json.dumps({'token_ids': token_ids})
            
        elif self.path == '/decode':
            req = json.loads(data)
            token_ids = req['token_ids']
            text = tikenizer.decode(token_ids)
            if text is None:
                msg = json.dumps({'text': ""})
            else:
                msg = json.dumps({'text': text})
        else:
            msg = 'error'
        print(msg)
        msg = str(msg).encode() # Convert to string then to bytes

        self.wfile.write(msg) # Return byte-formatted message to client

if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument('--host', type=str, default='localhost')
    args.add_argument('--port', type=int, default=8080)
    args = args.parse_args()

    host = (args.host, args.port) # Set host address and port; 'localhost' == '127.0.0.1'
    print('http://%s:%s' % host)
    server = HTTPServer(host, Request) # Create server instance using host and defined handler
    server.serve_forever() # Start server