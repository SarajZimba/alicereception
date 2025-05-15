
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file35 = Blueprint('app_file35',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import successmsg,errormsg
from root.utils.hashDetails import emailHash,phoneHash,addressHash


@app_file35.route("/billingParty", methods=["POST"])
@cross_origin()
def billingParty():
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

        if "banquetReservationID" not in json or json["banquetReservationID"]=="" or "email" not in json or "phone" not in json or "address" not in json or "vatno" not in json or json["vatno"]=="" or "name" not in json or json["name"]=="":
            data= errormsg("Important fields not supplied.")
            mydb.close()
            return data,400




        email=json["email"]
        phone= json["phone"]
        address=json["address"]
        vatno=json["vatno"]
        name=json["name"]
        banquetReservationID=json["banquetReservationID"]

        checkBanquetIDSQL=f"""SELECT * FROM `tblbanquetReservation` WHERE idtblbanquetReservation=%s;"""
        cursor.execute(checkBanquetIDSQL,(banquetReservationID,),)
        result=cursor.fetchall()
        if result ==[]:
            data= errormsg("Incorrect banquetReservationID supplied.")
            mydb.close()
            return data,400

        if email!="":
            email= emailHash(email)
        if phone!="":
            phone= phoneHash(phone)
        if address!="":
            address= addressHash(address)

        checkexistsSQL =f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
        cursor.execute(checkexistsSQL,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            insertBillingPartySQL=f"""INSERT INTO `tblbillingparty`(`banquetReservationID`, `Name`, `PanNo`, `Address`, `Phone`, `Email`) VALUES (%s,%s,%s,%s,%s,%s);"""
            cursor.execute(insertBillingPartySQL,(banquetReservationID,name,vatno,address,phone,email,),)
            mydb.commit()
            data=successmsg("Billing party changed.")
            mydb.close()
            return data,200
        elif result!=[]:
            updateBillingPartySQL=f"""INSERT INTO `tblbillingparty`(`banquetReservationID`) VALUES (%s) ON DUPLICATE KEY UPDATE Name=%s,PanNo=%s,Address=%s,Phone=%s,Email=%s;"""
            cursor.execute(updateBillingPartySQL,(banquetReservationID,name,vatno,address,phone,email,),)
            mydb.commit()
            data=successmsg("Billing party changed.")
            mydb.close()
            return data,200

        data=successmsg("Error occured.")
        mydb.close()
        return jsonify(data),400
    except Exception as error:
        data ={'error':str(error)}
        return data,400

