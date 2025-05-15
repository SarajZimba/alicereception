from flask import Blueprint,request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from root.auth.check import token_auth
from root.utils.phoneRegex import phonecheck
from root.utils.emailRegex import emailcheck
from root.utils.hashDetails import emailHash,phoneHash,ccHash,nameHash,addressHash
from root.utils.returnJson import successmsg,errormsg
from root.utils.converttoJson import listtojson

app_file1= Blueprint('app_file1',__name__)
@app_file1.route("/customerpost", methods=["POST"])
@cross_origin()
def customerPost():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data =errormsg("No token provided.")
            mydb.close()
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            mydb.close()
            return data,400
        if "Name" not in json or "Email" not in json or "Phone" not in json or "Address" not in json or "Country" not in json or "type" not in json  or "vatno" not in json:
            data = errormsg("Some fields are missing")
            mydb.close()
            return data,400
        cName = json["Name"]
        cEmail = json["Email"]
        cPhone = json["Phone"]
        caltPhone = json["altPhone"]
        cAddress = json["Address"]
        cCountry = json["Country"]
        ctype = json["type"]
        ccardno = json["cardno"]
        cvatno = json["vatno"]
        if cName=="" or cPhone=="" or cAddress=="" or cCountry=="" or ctype=="":
            data = errormsg("Some fields are missing")
            mydb.close()
            return data,400
        if not ctype=="Company" and not ctype=="Individual":
            data = errormsg("Type must be either Company or Individual.")
            mydb.close()
            return data,400
        if not any((cName, cEmail, cPhone,cAddress,cCountry,ctype,ccardno)):
            data= errormsg("Empty strings are not accepted.")
            mydb.close()
            return data,400
        if cEmail!="" and not emailcheck(cEmail):
            data = {"error":"Invalid email address provided. Please ensure that the correct format is used."}
            mydb.close()
            return data,400
        if cEmail!="":
            cEmail= emailHash(cEmail)
        cPhone= phoneHash(cPhone)
        cexistsSql = f"""SELECT Name FROM tblcustomer WHERE Name=%s and (Phone=%s OR Email=%s)"""
        cursor.execute(cexistsSql,(cName,cPhone,cEmail,),)
        mydb.commit()
        result = cursor.fetchall()
        if result != []:
            data = errormsg("Customer has already been registered before.")
            mydb.close()
            return data,400
        cAddress= addressHash(cAddress)
        if ccardno and not ccardno=="" :
            ccardno= ccHash(ccardno)
        insertCustomerSql=f"""INSERT INTO `tblcustomer`(`Name`, `Email`, `Phone`, `Address`, `Country`, `type`, `cardno`, `vatno`,`altPhone`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(insertCustomerSql,(cName,cEmail,cPhone,cAddress,cCountry,ctype,ccardno,cvatno,caltPhone,),)
        mydb.commit()
        customerKeySql= f"""SELECT idtblcustomer,Name FROM tblcustomer WHERE Name=%s AND Email=%s AND Phone=%s;"""
        cursor.execute(customerKeySql,(cName,cEmail,cPhone,),)
        result = cursor.fetchall()
        key = listtojson(result,cursor.description)
        key = "{}".format(key[0]["idtblcustomer"])
        data = successmsg(key)
        mydb.close()
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400