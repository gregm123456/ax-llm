from transformers import AutoTokenizer, PreTrainedTokenizerFast
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import argparse


class TokenizerGLM3_Http():

    def __init__(self):

        path = 'minicpm_tokenizer_v_2'
        # path = "openbmb/MiniCPM-V-2"
        # path = 'openbmb/MiniCPM-V-2'
        self.tokenizer_v2 = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        
        
        path = 'minicpm_tokenizer'
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        # self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm3-6b",
        #                                                trust_remote_code=True)

    def encode(self, prompt):
        # tokenizer.apply_chat_template(
        #             prompt,
        #             add_generation_prompt=True,
        #             return_tensors="pt")
        # token_ids = self.tokenizer.apply_chat_template(prompt)
        history = []
        history.append({"role": "user", "content": prompt})
        history_str = self.tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=False)
        print(history_str)
        token_ids = self.tokenizer.encode(history_str)
        return token_ids
    
    def encode_vpm(self, content = "What is in the image?"):
        image_placeholder = self.tokenizer_v2.im_start + self.tokenizer_v2.unk_token * 64 + self.tokenizer_v2.im_end
        prompt = "<用户>"
        prompt += image_placeholder + "\n" + content + "<AI>"

        input_ids = self.tokenizer_v2.encode(prompt)
        return input_ids

    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids, clean_up_tokenization_spaces=False)

    @property
    def bos_id(self):
        return self.tokenizer.bos_token_id

    @property
    def eos_id(self):
        return self.tokenizer.eos_token_id
    
    @property
    def bos_token(self):
        return self.tokenizer.bos_token

    @property
    def eos_token(self):
        return self.tokenizer.eos_token


tokenizer = TokenizerGLM3_Http()

print(tokenizer.bos_id, tokenizer.bos_token, tokenizer.eos_id, tokenizer.eos_token)
token_ids = tokenizer.encode_vpm()
print(token_ids)
print(len(token_ids))
token_ids = tokenizer.encode("hello world")
print(token_ids)
print(len(token_ids))


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
            bos_id = tokenizer.bos_id
            # print(bos_id)
            # to json
            if bos_id is None:
                msg = json.dumps({'bos_id': -1})
            else:
                msg = json.dumps({'bos_id': bos_id})
        elif self.path == '/eos_id':
            eos_id = tokenizer.eos_id
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
            print(req)
            prompt = req['text']
            b_img_prompt = False
            if 'img_prompt' in req:
                b_img_prompt = req['img_prompt']
            if b_img_prompt:
                token_ids = tokenizer.encode_vpm(prompt)
            else:
                token_ids = tokenizer.encode(prompt)
            if token_ids is None:
                msg = json.dumps({'token_ids': -1})
            else:
                msg = json.dumps({'token_ids': token_ids})
            
        elif self.path == '/decode':
            req = json.loads(data)
            token_ids = req['token_ids']
            text = tokenizer.decode(token_ids)
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
