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

app_file30= Blueprint('app_file30',__name__)
@app_file30.route("/customerDetailsUpdate", methods=["POST"])
@cross_origin()
def customerDetailsUPdate():
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
        if  "customerNote" not in json or "customerID" not in json or "Email" not in json or "Phone" not in json or "Address" not in json or "Country" not in json or "type" not in json  or "vatno" not in json:
            data = errormsg("Some fields are missing")
            mydb.close()
            return data,400
        customerNote=json["customerNote"]
        customerID=json["customerID"]
        cEmail = json["Email"]
        cPhone = json["Phone"]
        cAddress = json["Address"]
        cCountry = json["Country"]
        ctype = json["type"]
        ccardno = json["cardno"]
        cvatno = json["vatno"]
        caltPhone=json["altPhone"]
        if customerID=="" or cPhone=="" or cAddress=="" or cCountry=="" or ctype=="":
            data = errormsg("Some fields are missing")
            mydb.close()
            return data,400
        if not ctype=="Company" and not ctype=="Individual":
            data = errormsg("Type must be either Company or Individual.")
            mydb.close()
            return data,400
        if ctype=="Company" and not any((cvatno)):
            data= errormsg("Pan number must be provided for type 'Company'.")
            mydb.close()
            return data,400
        if not any((cPhone,cAddress,cCountry,ctype,ccardno)):
            data= errormsg("Empty strings are not accepted.")
            mydb.close()
            return data,400
        if not phonecheck(cPhone) :
            data = {"error":"Invalid phone number provided. Please ensure that the correct format is used."}
            mydb.close()
            return data,400
        cAddress= addressHash(cAddress)
        if ccardno and not ccardno=="" :
            ccardno= ccHash(ccardno)
        if cEmail!="":
            cEmail= emailHash(cEmail)
        cPhone= phoneHash(cPhone)
        cexistsSql = f"""UPDATE `tblcustomer` SET `altPhone`=%s,`customerNote`=%s,`Email`=%s,`Phone`=%s,`Address`=%s,`Country`=%s,`type`=%s,`cardno`=%s,`vatno`=%s WHERE idtblcustomer=%s"""
        cursor.execute(cexistsSql,(caltPhone,customerNote,cEmail,cPhone,cAddress,cCountry,ctype,ccardno,cvatno,customerID,),)
        mydb.commit()
        mydb.close()
        data=successmsg("Successfully updated.")
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400