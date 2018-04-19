from flask import Flask, request
import sqlite3
import os
import socket
import json
import base64
import re

executable = 'C:\Program Files\Sublime Text 3\sublime_text.exe'
host="127.0.0.1"
port=12345

app=Flask(__name__)

def escape_for_cmd_exe(arg):
    # Escape an argument string to be suitable to be passed to
    # cmd.exe on Windows
    #
    # This method takes an argument that is expected to already be properly
    # escaped for the receiving program to be properly parsed. This argument
    # will be further escaped to pass the interpolation performed by cmd.exe
    # unchanged.
    #
    # Any meta-characters will be escaped, removing the ability to e.g. use
    # redirects or variables.
    #
    # @param arg [String] a single command line argument to escape for cmd.exe
    # @return [String] an escaped string suitable to be passed as a program
    #   argument to cmd.exe

    meta_chars = '()%!^"<>&|'
    meta_re = re.compile('(' + '|'.join(re.escape(char) for char in list(meta_chars)) + ')')
    meta_map = { char: "^%s" % char for char in meta_chars }

    def escape_meta_chars(m):
        char = m.group(1)
        return meta_map[char]

    return meta_re.sub(escape_meta_chars, arg)

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

  if input_data['intent'] == 'OPEN_DOCS':
    # command = '@"' + executable + '" --command "path"'

    # os.system(command)

    # conn, address = server_socket.accept()
    # while True:

    #   path = conn.recv(1024).decode()
      
    #   if path:
    #     conn.close()
        # path=path[:path.rfind('\\')] 
        # path = os.path.join(path, "README.md")

        # command='@"' + executable + '" --command '+ "\""+ "displaydocs {\\\"path\\\":\\\""+json.dumps(path)+"\\\"}\""
    # command='@"' + executable + ' --command displaydocs'# {\\\"path\\\":\\\""+json.dumps(path)+"\\\"}\""
    # print(command)
    # os.system(command)

    command = '@"' + executable + '" --command "displaydocs"'

    os.system(command)
        
    return json.dumps({"result": "Opening the README for this Folder in your browser"}) 

  if input_data['intent'] == 'SNIPPET':
    r = {
      'JSON_TO_XML': "jsontoxml",
      'XML_TO_JSON': "xmltojson",
      'ORACLE_CONNECTION': "oracleconnection",
      'MONGO_CONNECTION': "mongoconnection",
      'POSTGRES_CONNECTION': "postgresconnection",
      'MYSQL_CONNECTION': "mysqlconnection"
    }

    
    command = '@"' + executable + '" --command "'+r[input_data['which']]+'"'
    print(command)
    os.system(command)
    return json.dumps({"result": "Inserted it"}) 

if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)
