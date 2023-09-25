# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 10:21:47 2023

@author: Himanshu Mayank
"""
import http.server
import socketserver
import urllib.parse
import json
import openai
from datetime import datetime
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

storage_account_key = "ec5SbL6Px5VyaPhZmXKhPlURTGK+lyyda+OJT66IDUFNJ25VnZNpOdUIdVfYnH+PglzT2j3z4jiI+AStkE2hCA=="
storage_account_name = "empathychatbotstorage"
connection_string = "DefaultEndpointsProtocol=https;AccountName=empathychatbotstorage;AccountKey=ec5SbL6Px5VyaPhZmXKhPlURTGK+lyyda+OJT66IDUFNJ25VnZNpOdUIdVfYnH+PglzT2j3z4jiI+AStkE2hCA==;EndpointSuffix=core.windows.net"
container_name = "chathistory"
# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Set the API key as an environment variable
os.environ['OPENAI_API_KEY'] = "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"
class ChatbotRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the HTML file for the home page
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

    def do_POST(self):
        # Handle user input and return chatbot response
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        user_input = urllib.parse.parse_qs(post_data)['user_input'][0]
    
        # Make a request to the ChatGPT API
        response = openai.Completion.create(
            engine='text-davinci-003',  # Use the appropriate ChatGPT engine
            prompt=user_input,
            max_tokens=500,  # Define the maximum number of tokens in the response
            n=1,  # Generate a single response
            stop=None,  # Customize a stop condition if needed
            api_key=os.environ['OPENAI_API_KEY']  # Access the API key from the environment variable
        )
        # Getting the current date and time to create a unique file name for chat history
        dt = datetime.now()
        filename = "chat_results_" + str(dt)[0:16].replace(" ", "_").replace(":", "_") + ".txt"

     
        
        print(response)
        # Extract the generated response from the API
        chatbot_response = response.choices[0].text.strip()
        chatbot_response = chatbot_response.replace('\n', '<br>')
        # Send the chatbot response as JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'response': chatbot_response}).encode('utf-8'))

        data = {
            "User": str(user_input),
            "ChatGPT": str(chatbot_response)
        }
        
        # Define the filename for the JSON file
        filename = "conversation.json"
        json_data = json.dumps(data, indent=4)
        blob_client = container_client.get_blob_client("conversation.json")
        blob_client.upload_blob(json_data, overwrite=True)
        # Write the data to the JSON file
        #with open(filename, 'w') as json_file:
        #    json.dump(data, json_file, indent=4)

server_address = ('', 8000)  # Use an available port, If the port is already in use, use 8001
httpd = socketserver.TCPServer(server_address, ChatbotRequestHandler)

print('Chatbot web page is running at http://localhost:8000/')
httpd.serve_forever()


