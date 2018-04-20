from flask import Flask, request
import sqlite3
import os
import socket
import json
import base64
import re
import sys
import subprocess
import requests
from io import BytesIO, TextIOWrapper

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
    db_con = sqlite3.connect("chinook.db")

    query = "Select MAX(InvoiceDate) AS LASTACCESSDATE from "+tablename+";"
    cursor=db_con.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    db_con.close()
    return(json.dumps({"result":str(result[0])}))
  
  if input_data['intent']=='GET_ROWS':
    tablename = "invoices"
    db_con = sqlite3.connect("chinook.db")

    query = "Select count(*) from "+tablename+";"
    cursor=db_con.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    db_con.close()
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

  if input_data['intent'] == 'RUN_TESTS':
    from subprocess import Popen, PIPE
    os.chdir('c:\\dev\\hackathon\\roro-textar')

    command = ['python', '-m', 'nose']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if err.splitlines()[-1][:len("FAILED")] == b'FAILED':

      r = requests.post(
        "https://api.mailgun.net/v3/rohanverma.net/messages",
        auth=("api", "key-cdb3edf241642090b03ba98ddb6e979c"),
        data={"from": "Code Companian <noreply@rohanverma.net>",
        "to": "hithesh <jbhithesh@gmail.com>",
        "subject": "Here are your test results ran by your Coding Companion",
        "text": "Your test results:" + err.decode('utf-8')
      })

      print(r.status_code)

      return json.dumps({"result": "Sorry, Tests Failed! and I am emailing you the results"})

    else:
      return json.dumps({"result": "Great work, Tests Passed!"})
    os.chdir('c:\\dev\\hackathon\\dell-hack')

  if input_data['intent'] == 'RUN_COVERAGE':
    from subprocess import Popen, PIPE
    os.chdir('c:\\dev\\hackathon\\roro-textar')

    command = ['python', '-m', 'nose', '--with-coverage']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()

    # to_add = False
    # lines = []
    # for l in err.splitlines():
    #   if l[:len("Name")] == b'Name':
    #     to_add = True
    #   elif l[:len("FAILED")] == b'FAILED' or l[:len("PASSED")] == b'PASSED':
    #     to_add = False
    #   if to_add:
    #     lines.append(l)

    # result = ''.join(lines)
    res = err.decode('utf-8')
    result = res[res.find('Name'): res.find('FAILED')]

    r = requests.post(
      "https://api.mailgun.net/v3/rohanverma.net/messages",
      auth=("api", "key-cdb3edf241642090b03ba98ddb6e979c"),
      data={"from": "Code Companian <noreply@rohanverma.net>",
      "to": "hithesh <jbhithesh@gmail.com>, rohan <hello@rohanverma.net>",
      "subject": "Here are your coverage results ran by your Coding Companion",
      "text": "Your coverage results:" + result
    })
    print(r.status_code)


    return json.dumps({"result": "I am emailing you the code coverage results"})


    os.chdir('c:\\dev\\hackathon\\dell-hack')


  if input_data['intent'] == 'DB_TASK':

    r = requests.post(
      "https://api.mailgun.net/v3/rohanverma.net/messages",
      auth=("api", "key-cdb3edf241642090b03ba98ddb6e979c"),
      data={"from": "Code Companian <noreply@rohanverma.net>",
      "to": "hithesh <jbhithesh@gmail.com>, rohan <hello@rohanverma.net>",
      "subject": "DB Performance Report",
      "text": "After analysis of the Database KOVA_DB, the execution plan comparison of high cost tables results in checking the column of INC of table KO_T"
    })
    print(r.status_code)
    
    r = "Perfomance testing analysis is going on and results will be sent to you in 20 seconds"
    return json.dumps({"result": r})

  if input_data['intent'] == 'LN2SQL':
    which = input_data['which']
    q = {
      "Q1": "What is the average age of students in student table where age is over 25",
      "Q2": "What is the average age of students in student table",
      "Q3": "What is the number of students in student table",
      "Q4": "What is the number of students in student table whose name is Doe"
    }

    from ln2sql import ln2sql

    ln2sql = ln2sql.Ln2sql(
            database_path="database_store\school.sql",
            language_path="lang_store\english.csv",
            json_output_path=None,
            thesaurus_path=None,
            stopwords_path=None,
    ).get_query(q[which])

    # r = requests.post(
    #   "https://api.mailgun.net/v3/rohanverma.net/messages",
    #   auth=("api", "key-cdb3edf241642090b03ba98ddb6e979c"),
    #   data={"from": "Code Companian <noreply@rohanverma.net>",
    #   "to": "hithesh <jbhithesh@gmail.com>, rohan <hello@rohanverma.net>",
    #   "subject": "Here are your coverage results ran by your Coding Companion",
    #   "text": "Your coverage results:" + result
    # })
    # print(r.status_code)

    # r = """
    # Reads file header comment, function definitions, function docstrings.
    # Returns dictionary encapsulation for subsequent writing."""
    return json.dumps({"result": ln2sql})

     
  return json.dumps({"result": "Sorry. I could not understand"})
if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)
