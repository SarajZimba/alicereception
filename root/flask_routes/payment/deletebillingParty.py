
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file37 = Blueprint('app_file37',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import successmsg,errormsg
from root.utils.hashDetails import emailHash,phoneHash,addressHash


@app_file37.route("/deletebillingParty", methods=["POST"])
@cross_origin()
def deletebillingParty():
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

        if "banquetReservationID" not in json or json["banquetReservationID"]=="":
            data= errormsg("banquetReservationID not supplied.")
            mydb.close()
            return data,400


        banquetReservationID=json["banquetReservationID"]

        checkBanquetIDSQL=f"""SELECT * FROM `tblbanquetReservation` WHERE idtblbanquetReservation=%s;"""
        cursor.execute(checkBanquetIDSQL,(banquetReservationID,),)
        result=cursor.fetchall()
        if result ==[]:
            data= errormsg("Incorrect banquetReservationID supplied.")
            mydb.close()
            return data,400



        checkexistsSQL =f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
        cursor.execute(checkexistsSQL,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            data=successmsg("Billing party doesn't exist.")
            mydb.close()
            return data,400
        elif result!=[]:
            updateBillingPartySQL=f"""delete from tblbillingparty where banquetReservationID=%s"""
            cursor.execute(updateBillingPartySQL,(banquetReservationID,),)
            mydb.commit()
            data=successmsg("Billing party deleted.")
            mydb.close()
            return data,200

        data=successmsg("Error occured.")
        mydb.close()
        return jsonify(data),400
    except Exception as error:
        data ={'error':str(error)}
        return data,400

