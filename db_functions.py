import sqlite3,json

def db_functions(tablename,databasename,intent):
    conn = sqlite3.connect("chinook.db")
    if intent=='GET_ROWS':
        getRows(tablename,conn)
    elif intent == 'RISE_ROWS':
        getRiseinRows(tablename,conn)
    elif intent == 'LAST_ACCESS'
        getLastAccessDate(tablename,conn)

def getLastAccessDate(tablename, conn):
    query = "Select MAX(InvoiceDate) AS LASTACCESSDATE from "+tablename+";"
    cursor=conn.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    conn.close()
    return(json.dumps({"result":str(result[0])}))

def getRiseinRows(tablename, conn):
    cursor=conn.cursor()
    q1 = "select count(*) from "+tablename+" where InvoiceDate <= datetime('now','-1 day');"
    cursor.execute(q1)
    total=int(cursor.fetchone())
    q2 = "select count(*) from "+tablename+" a where a.InvoiceDate <= datetime('now') and a.InvoiceDate >= datetime('now','-1 day');"
    cursor.execute(q2)
    diff=int(cursor.fetchone())
    result = (diff/total)*100
    conn.close()
    return(json.dumps({"result":str(result)}))

def getRows(tablename, conn):
    query = "Select count(*) from "+tablename+";"
    cursor=conn.cursor()
    cursor.execute(query)
    result=cursor.fetchone()
    conn.close()
    return(json.dumps({"result":str(result[0])}))
