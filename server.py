from flask import Flask, request
import sqlite3
import os
import socket
import json



app=Flask(__name__)

@app.route('/receive_from_alexa',methods=['POST'])
def alexa():
  input_data = request.data
  input_data = json.loads(input_data)
  # return(input_data)
  # input_data = {}
  # input_data['intent'] = 'SQL_QUERY'
  print(input_data['intent'])
  if input_data['intent']=='SQL_QUERY':
    # print("inside")
    result=""
    host="127.0.0.1"
    port=12345
    executable = 'C:\Program Files\Sublime Text 3\sublime_text.exe'
    command = '@"' + executable + '" --command "example"'
    # print(command)
    # subprocess.Popen(cmdList, stdout=subprocess.PIPE)
    os.system(command)
    # print("socket starting")
    server_socket= socket.socket()
    # print("socket created")
    server_socket.bind((host,port))
    # print("socket bound")
    server_socket.listen(1)
    # print("socket listening")
    conn, address = server_socket.accept()
    # print("socket started")
    while True:
      # print("waitingfordata")
      data = conn.recv(1024).decode()
      
      if data:
        query=(data)
        conn = sqlite3.connect("chinook.db")
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchone()
       
        # return json.dumps({"result":"HELLO MOTHER FOCK HERS"})
        conn.close()
        return json.dumps({"result":str(result[0])})
    return result

if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)