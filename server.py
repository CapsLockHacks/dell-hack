from flask import Flask, request
import sqlite3
import os
import socket
import json


executable = 'C:\Program Files\Sublime Text 3\sublime_text.exe'
host="127.0.0.1"
port=12345

app=Flask(__name__)

@app.route('/receive_from_alexa',methods=['POST'])
def alexa():
  input_data = request.data

  input_data = json.loads(input_data)
  # return(input_data)

  # input_data = {}
  # input_data['intent'] = 'SQL_QUERY'
  print(input_data['intent'])

  server_socket= socket.socket()
  server_socket.bind((host,port))
  server_socket.listen(1)

  if input_data['intent']=='SQL_QUERY':
    # print("inside")
    result=""
    command = '@"' + executable + '" --command "line"'

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

  if input_data['intent']=='RISE_ROWS':
    tablename = "invoices"
    db_con = sqlite3.connect("chinook.db")
    cursor=db_con.cursor()
    q1 = "select count(*) from "+tablename+" where InvoiceDate <= datetime('now','-1 day');"
    cursor.execute(q1)
    total=int(cursor.fetchone()[0])
    q2 = "select count(*) from "+tablename+" a where a.InvoiceDate <= datetime('now') and a.InvoiceDate >= datetime('now','-1 day');"
    cursor.execute(q2)
    diff=int(cursor.fetchone()[0])
    result = (diff/total)*100
    db_con.close()
    return(json.dumps({"result":str(result)}))

  if input_data['intent']=='LAST_ACCESS':
    tablename = "invoices"
    query = "Select MAX(InvoiceDate) AS LASTACCESSDATE from "+tablename+";"
    cursor=conn.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    conn.close()
    return(json.dumps({"result":str(result[0])}))
  
  if input_data['intent']=='GET_ROWS':
    tablename = "invoices"
    query = "Select count(*) from "+tablename+";"
    cursor=conn.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    conn.close()
    return(json.dumps({"result":str(result[0])}))


  if input_data['intent'] == 'CURRENT_DOCSTRING':

    command='@"' + executable + '" --command "auto_docstring"'
    os.system(command)

    return json.dumps({"result": "Generated the Doc Strings for this function"})

  if input_data['intent'] == 'ALL_DOCSTRING':

    command='@"' + executable + '" --command "auto_docstring_all"'
    os.system(command)

    return json.dumps({"result": "Generated the Doc Strings for this file"})

  if input_data['intent'] == 'GEN_DOC':
    result=""
    command = '@"' + executable + '" --command "path"'

    os.system(command)

    conn, address = server_socket.accept()
    while True:

      path = conn.recv(1024).decode()
      
      if path:
        conn.close()
        path=path[:path.rfind('\\')]

        command_md = "python py2md.py -s "+path+"  -o README.md"
        os.system(command_md) 

        
        return json.dumps({"result": "Generated the README for this Folder"}) 




if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)
