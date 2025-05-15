
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file13 = Blueprint('app_file13',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file13.route("/cancel", methods=["POST"])
@cross_origin()
def cancelled():
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
        if not "banquetreservationID" in json or json["banquetreservationID"]=="":
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        banquetreservationID = json["banquetreservationID"]
        getPaymentDetailsSql =f"""update tblbanquetReservation set reservationState='Cancelled' where idtblbanquetReservation=%s"""
        cursor.execute(getPaymentDetailsSql,(banquetreservationID,),)
        mydb.commit()
        removeAdvancePaymentSQL =f"""delete from tblbanquetPayment_details  where paymentType='Advance' and banquetReservationID=%s"""
        cursor.execute(removeAdvancePaymentSQL,(banquetreservationID,),)
        mydb.commit()
        mydb.close()
        return successmsg("Cancelled."),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


