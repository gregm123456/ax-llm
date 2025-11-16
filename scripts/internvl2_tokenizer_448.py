from transformers import AutoTokenizer, PreTrainedTokenizerFast
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import argparse


class Tokenizer_Http():

    def __init__(self):

        path = 'internvl2_tokenizer'
        self.tokenizer = AutoTokenizer.from_pretrained(path,
                                                       trust_remote_code=True,
                                                       use_fast=False)

    def encode(self, content):
        # System prompt: Describe the model identity/role in English, keep semantics the same
        prompt = f"<|im_start|>system\nYou are a multi-modal assistant model developed jointly by Shanghai AI Laboratory and SenseTime, named InternVL. You are a helpful, harmless AI assistant.<|im_end|><|im_start|>user\n{content}<|im_end|><|im_start|>assistant\n"
        input_ids = self.tokenizer.encode(prompt)
        return input_ids

    def encode_vpm(self, content="Please describe the image shortly."):
        # System prompt: Model description (English), then image prompt
        prompt = f"<|im_start|>system\nYou are a multi-modal assistant model developed jointly by Shanghai AI Laboratory and SenseTime, named InternVL. You are a helpful, harmless AI assistant.<|im_end|><|im_start|>user\n<img>" + "<IMG_CONTEXT>" * 256 + f"</img>\n{content}<|im_end|><|im_start|>assistant\n"
        input_ids = self.tokenizer.encode(prompt)
        return input_ids

    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids,
                                     clean_up_tokenization_spaces=False)

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


tokenizer = Tokenizer_Http()

print(tokenizer.bos_id, tokenizer.bos_token, tokenizer.eos_id,
      tokenizer.eos_token)
token_ids = tokenizer.encode_vpm()
# [151644, 8948, 198, 56568, 104625, 100633, 104455, 104800, 101101, 32022, 102022, 99602, 100013, 9370, 90286, 21287, 42140, 53772, 35243, 26288, 104949, 3837, 105205, 109641, 67916, 30698, 11, 54851, 46944, 115404, 42192, 99441, 100623, 48692, 100168, 110498, 1773, 151645, 151644, 872, 198,
# 151646,
# 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648, 151648,
# 151647,
# 198, 5501, 7512, 279, 2168, 19620, 13, 151645, 151644, 77091, 198]
# 118
print(token_ids)
print(len(token_ids))
token_ids = tokenizer.encode("hello world")
# [151644, 8948, 198, 56568, 104625, 100633, 104455, 104800, 101101, 32022, 102022, 99602, 100013, 9370, 90286, 21287, 42140, 53772, 35243, 26288, 104949, 3837, 105205, 109641, 67916, 30698, 11, 54851, 46944, 115404, 42192, 99441, 100623, 48692, 100168, 110498, 1773, 151645, 151644, 872, 198, 14990, 1879, 151645, 151644, 77091, 198]
# 47
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
        self.send_header("type", "get")  # Set response header; optional
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
        msg = str(msg).encode()  # Convert to string then to bytes

        self.wfile.write(msg)  # Return byte-formatted message to client

    def do_POST(self):
        # Define the POST handler (runs when a client sends a POST request)
        data = self.rfile.read(int(
            self.headers['content-length']))  # Read request body (bytes)
        data = data.decode()  # Decode bytes to string

        self.send_response(200)
        self.send_header("type", "post")  # Set response header; optional
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
        msg = str(msg).encode()  # Convert to string then to bytes

        self.wfile.write(msg)  # Return byte-formatted message to client


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument('--host', type=str, default='localhost')
    args.add_argument('--port', type=int, default=8080)
    args = args.parse_args()

    host = (args.host, args.port)  # Set host address and port; 'localhost' == '127.0.0.1'
    print('http://%s:%s' % host)
    server = HTTPServer(host, Request)  # Create server instance using host and defined handler
    server.serve_forever()  # Start server
