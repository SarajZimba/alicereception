from flask import Flask, Blueprint,request,jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file24 = Blueprint('app_file24',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import errormsg,resultmsg,successmsg



@app_file24.route("/creditCustomerList", methods=["POST"])
@cross_origin()
def creditCustomerList():
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
            data =  errormsg("Invalid token.")
            mydb.close()
            return data,400
        if not "outlet" in json:
            data=  errormsg("Outlet Name not supplied.")
            mydb.close()
            return data,400
        get_customer_creditSql =f"""SELECT DISTINCT customerName from CreditHistory where Outlet_Name=%s"""
        cursor.execute(get_customer_creditSql,(json["outlet"],),)
        result = cursor.fetchall()
        if result == []:
            data = errormsg("No data available.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            json_data.append(dict(zip(row_headers,res)))
        response_json = []
        for i in json_data:
            customer_Credit_json ={"name":i["customerName"],"value":i["customerName"]}
            response_json.append(customer_Credit_json)
        mydb.close()
        return jsonify(response_json),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

