
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file9 = Blueprint('app_file9',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file9.route("/rateDetails", methods=["POST"])
@cross_origin()
def rateDetails():
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
        if not "banquetReservationID" in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        cId = json["banquetReservationID"]
        getRateDetailsSql =f"""SELECT a.idtblbanquetRate_details,a.RateName,a.RateAmount,a.NoOfPax,a.HallName,a.banquetReservationID from tblbanquetRate_details a, tblbanquetReservation b WHERE b.idtblbanquetReservation=a.banquetReservationID and a.banquetReservationID=%s GROUP BY a.idtblbanquetRate_details"""
        cursor.execute(getRateDetailsSql,(cId,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Temporarily unavailable.")
            mydb.close()
            return data,400
        json_data = listtojson(result,cursor.description)
        mydb.close()
        return jsonify(json_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

