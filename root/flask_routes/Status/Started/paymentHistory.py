
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file8 = Blueprint('app_file8',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from datetime import datetime, timezone



@app_file8.route("/paymentHistory", methods=["POST"])
@cross_origin()
def paymentHistory():
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
        if not "banquetReservationID" in json or json["banquetReservationID"]=="":
            data = errormsg("A field is missing.")
            mydb.close()
            return data,400
        banquetReservationID= json["banquetReservationID"]
        getPaymentDetailsSql =f"""SELECT a.idtblbanquetPayment_details,a.paymentDate,a.PaymentAmount from tblbanquetPayment_details a, tblbanquetReservation b WHERE  a.banquetReservationID=%s AND b.idtblbanquetReservation=a.banquetReservationID and a.paymentType!='billEntry' GROUP BY a.idtblbanquetPayment_details"""
        cursor.execute(getPaymentDetailsSql,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %Z') or "Fri, 19 May 2023 14:54:02 GMT" 
            returndata = [{"PaymentAmount": "0.00","advancePaymentMethod": "", "idtblbanquetPayment_details": "", "paymentDate": date }
]
            mydb.close()
            return jsonify(returndata),200
    
        json_data = listtojson(result,cursor.description)
        
        advancePaymentMethod= ""
        getPaymentMethodAndAmount=f"""SELECT IFNULL(PaymentMode,"") as PaymentMode FROM `tblbanquetPayment_details` WHERE paymentType='Advance' and banquetReservationID=%s"""
        cursor.execute(getPaymentMethodAndAmount,(banquetReservationID,),)
        result=cursor.fetchall()

        if result !=[]:
            advancePaymentMethod=result[0][0] or ""
        print(json_data,advancePaymentMethod)
        json_data[0]["advancePaymentMethod"]=advancePaymentMethod
        print(json_data)
        mydb.close()
        return jsonify(json_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

