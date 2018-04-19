from flask import Flask, request
import sqlite3
import os
import socket
import json


executable = 'C:\Program Files\Sublime Text 3\sublime_text.exe'

app=Flask(__name__)

@app.route('/receive_from_alexa',methods=['POST'])
def alexa():
  input_data = request.data
  input_data = json.loads()
  # input_data = {}
  # input_data['intent'] = 'SQL_QUERY'
  print(input_data['intent'])

  server_socket= socket.socket()
  server_socket.bind((host,port))
  server_socket.listen(1)

  if input_data['intent']=='SQL_QUERY':
    # print("inside")
    result=""
    host="127.0.0.1"
    port=12345
    command = '@"' + executable + '" --command "example"'
    os.system(command)

    conn, address = server_socket.accept()
    while True:

      data = conn.recv(1024).decode()
      
      if data:
        query=(data)
        conn = sqlite3.connect("chinook.db")
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchone()
       

        conn.close()
        return json.dumps({"result":str(result[0])})
    return result

    ###############################################################

  if input_data['intent']= 'CURRENT_DOCSTRING':

    command='@"' + executable + '" --command "auto_docstring"'
    os.system(command)

    return json.dumps({"result": "Generated the Documentation for this function"})

  if input_data['intent']= 'ALL_DOCSTRING':

    command='@"' + executable + '" --command "auto_docstring_all"'
    os.system(command)

    return json.dumps({"result": "Generated the Documentation for this file"})


if name == '__main__':
  app.run(host="0.0.0.0",debug=True)
