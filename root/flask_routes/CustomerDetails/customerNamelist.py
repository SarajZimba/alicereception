
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file22 = Blueprint('app_file22',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *

@app_file22.route("/customerNameList", methods=["POST"])
@cross_origin()
def getcustomerByname():
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
        getCustomerSql =f"""select distinct Name,idtblcustomer from tblcustomer"""
        cursor.execute(getCustomerSql,)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("No data available.")
            mydb.close()
            return data,400
        json_data = listtojson(result,cursor.description)
        response_json = []
        for i in json_data:
            outlet_json ={"name":i["Name"],"value":i["Name"]}
            response_json.append(outlet_json)
        mydb.close()
        return jsonify(response_json),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400
 

