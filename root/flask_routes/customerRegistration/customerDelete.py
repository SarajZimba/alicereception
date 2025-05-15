from flask import Blueprint,request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from root.auth.check import token_auth
from root.utils.returnJson import successmsg,errormsg

app_file31= Blueprint('app_file31',__name__)
@app_file31.route("/customerDelete", methods=["POST"])
@cross_origin()
def customerDelete():
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
        if  "customerID" not in json or json["customerID"]=="":
            data = errormsg("CustomerID missing")
            mydb.close()
            return data,400
        customerID=json["customerID"]
        cexistsSql = f"""SELECT * FROM `tblbanquetReservation` WHERE customerID=%s"""
        cursor.execute(cexistsSql,(customerID,),)
        result = cursor.fetchall()
        if result !=[]:
            data = errormsg("Cannot delete customer. Reason: Customer has previous reservation records.")
            mydb.close()
            return data,400
        deletecustomerSql=f"""DELETE FROM `tblcustomer` WHERE idtblcustomer=%s"""
        cursor.execute(deletecustomerSql,(customerID,),)
        mydb.commit()
        mydb.close()
        data=successmsg("Successfully updated.")
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400