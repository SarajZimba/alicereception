from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file4 = Blueprint('app_file4',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import successmsg,errormsg



@app_file4.route("/outlets", methods=["POST"])
@cross_origin()
def outlets():
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
        get_outlet_sql =f"""select Outlet_Name from Outlets"""
        cursor.execute(get_outlet_sql)
        result = cursor.fetchall()
        if result == []:
            data = errormsg("Temporarily unavailable.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            json_data.append(dict(zip(row_headers,res)))
        response_json = []
        for i in json_data:
            outlet_json ={"name":i["Outlet_Name"],"value":i["Outlet_Name"]}
            response_json.append(outlet_json)
        mydb.close()
        return  jsonify(response_json),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

