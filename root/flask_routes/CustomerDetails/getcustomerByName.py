
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file17 = Blueprint('app_file17',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *

@app_file17.route("/getcustomerByName", methods=["POST"])
@cross_origin()
def getcustomerByName():
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
        if not "customerName" in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        cId = json["customerName"]
        getCustomerSql =f"""SELECT customerNote,altPhone,Name, Email, Phone, Address,type, vatno as vat,	Country as country, idtblcustomer as customerID FROM tblcustomer WHERE Name=%s"""
        cursor.execute(getCustomerSql,(cId,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("No results found.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        billItemdata ={}
        for res in result:
            altPhone= dict(zip(row_headers,res))["altPhone"]
            cName = dict(zip(row_headers,res))["Name"]
            cCountry = dict(zip(row_headers,res))["country"]
            cvat = dict(zip(row_headers,res))["vat"]
            ctype=dict(zip(row_headers,res))["type"]
            cEmail=""
            cPhone=""
            cAddress=""
            if dict(zip(row_headers,res))["Email"]!="":
                cEmail = emailDecode(dict(zip(row_headers,res))["Email"])
            if dict(zip(row_headers,res))["Phone"] !="":
                cPhone= phoneDecode(dict(zip(row_headers,res))["Phone"])
            if dict(zip(row_headers,res))["Address"] !="":
                cAddress = addressDecode(dict(zip(row_headers,res))["Address"])
            customerID= dict(zip(row_headers,res))["customerID"]
            customerNote= dict(zip(row_headers,res))["customerNote"]
            jsondata={"customerNote":customerNote,"type":ctype,"vat":cvat,"country":cCountry,"altPhone":altPhone,"Name":cName,"Email":cEmail,"Phone":cPhone,"Address":cAddress,"customerID":customerID}
            billItemdata.setdefault("Details",[]).append(jsondata)
        mydb.close()
        return billItemdata,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400
 

