from flask import Flask, request
import sqlite3
import os
import socket
import json



app=Flask(__name__)

@app.route('/receive_from_alexa',methods=['GET'])
def alexa():
  input_data = request.args
  # input_data = {}
  # input_data['intent'] = 'SQL_QUERY'
  print(input_data['intent'])
  if input_data['intent']=='SQL_QUERY':
    print("inside")
    result=""
    host="0.0.0.0"
    port=12345
    command = "subl --command 'example'"
    # subprocess.Popen(cmdList, stdout=subprocess.PIPE)
    os.system(command)
    server_socket= socket.socket()
    server_socket.bind((host,port))
    server_socket.listen(1)
    conn, address = server_socket.accept()
    while True:
      print("waitingfordata")
      data = conn.recv(1024).decode()
      
      if data:
        query=(data)
        conn = sqlite3.connect("chinook.db")
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchone()
       
        # return json.dumps({"result":"HELLO MOTHER FOCK HERS"})
        return json.dumps({"result":str(result[0])})
    conn.close()
    return result


@app.route('/receive_from_sublime',methods=['GET'])
def sublime():
	database=""
	data=request.args
	query=(data['q'])
	conn = sqlite3.connect(database)
	cursor=conn.cursor()
	cursor.execute(query)
	result=cursor.fetchall()
	print(result)
	#returning
	return result
	

if __name__ == '__main__':
	app.run(host="0.0.0.0",debug=True)