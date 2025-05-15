from flask import Blueprint,request
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()


from root.auth.check import token_auth
from root.utils.phoneRegex import phonecheck
from root.utils.emailRegex import emailcheck
from root.utils.hashDetails import emailHash,phoneHash
from root.utils.decodeDetails import addressDecode
from root.utils.returnJson import errormsg,resultmsg,successmsg
from root.utils.converttoJson import listtojson

app_file2= Blueprint('app_file2',__name__)
@app_file2.route("/customercheck", methods=["POST"])
@cross_origin()
def customerExists():
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
        if "Name" not in json or "Email" not in json or "Phone" not in json:
            data = errormsg("Some fields are missing")
            mydb.close()
            return data,400
        cName = json["Name"]
        cEmail = json["Email"]
        cPhone = json["Phone"]
        if not any((cName, cPhone)):
            data= errormsg("Empty strings are not accepted.")
            mydb.close()
            return data,400
        #cName= nameHash(cName)
        if cEmail!="":
            cEmail= emailHash(cEmail)
        cPhone= phoneHash(cPhone)
        cexistsSql = f"""SELECT idtblcustomer,Address,Country,type,vatno FROM tblcustomer WHERE Name=%s and (Phone=%s OR Email=%s)"""
        cursor.execute(cexistsSql,(cName,cPhone,cEmail,),)
        mydb.commit()
        result = cursor.fetchall()
        customerVerificationresult = {}
        if result != []:
            key = listtojson(result,cursor.description)
            Address=addressDecode(key[0]["Address"])
            jsondata={"customerId":key[0]["idtblcustomer"],"vatno":key[0]["vatno"],"type":key[0]["type"],"country":key[0]["Country"],"address":Address}
            customerVerificationresult.setdefault("success",[]).append(jsondata)
            mydb.close()
            return customerVerificationresult,200
        mydb.close()
        data= errormsg("Registration required.")
        return data,400
    except Exception as error:
        data ={'error':str(error)}
        return data,400