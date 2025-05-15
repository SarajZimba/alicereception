
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file11 = Blueprint('app_file11',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *

@app_file11.route("/getCustomer", methods=["POST"])
@cross_origin()
def customerGet():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = errormsg("No token provided.")
            mydb.close()
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = errormsg("Invalid token.")
            mydb.close()
            return data,400
        if not "customerID" in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        cId = json["customerID"]
        getCustomerSql =f"""SELECT Name, Email, Phone, Address,type, vatno FROM tblcustomer WHERE idtblcustomer=%s"""
        cursor.execute(getCustomerSql,(cId,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Temporarily unavailable.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description]
        billItemdata ={}
        for res in result:
            cName = dict(zip(row_headers,res))["Name"]
            cEmail = emailDecode(dict(zip(row_headers,res))["Email"])
            cPhone= phoneDecode(dict(zip(row_headers,res))["Phone"])
            cAddress = addressDecode(dict(zip(row_headers,res))["Address"])
            ctype= dict(zip(row_headers,res))["type"]
            cvatno=  dict(zip(row_headers,res))["vatno"]
            jsondata={"vatno":cvatno,"type":ctype,"Name":cName,"Email":cEmail,"Phone":cPhone,"Address":cAddress}
            billItemdata.setdefault("Details",[]).append(jsondata)
        mydb.close()
        return billItemdata,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400
 

