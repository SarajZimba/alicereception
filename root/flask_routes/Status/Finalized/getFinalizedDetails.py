from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file15 = Blueprint('app_file15',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *


@app_file15.route("/getFinalizedDetails", methods=["POST"])
@cross_origin()
def getFinalizedDetials():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "ResID" not in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        ResID=json["ResID"]
        getFinalizedSql =f"""SELECT b.Name,b.Phone,b.Address,b.type,b.vatno, a.TimeSlot, DATE(a.reservationDate) as reservationDate, DATE(a.reservationForDate) as ReservationFor,a.advancePayment,a.SpecialRequest,b.idtblcustomer as customerID FROM tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.idtblbanquetReservation=%s"""
        cursor.execute(getFinalizedSql,(ResID,),)
        mydb.commit()
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Temporarily unavailable.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description]
        billItemdata ={}
        for res in result:
            cName = dict(zip(row_headers,res))["Name"]
            cPhone= phoneDecode(dict(zip(row_headers,res))["Phone"])
            cAddress = addressDecode(dict(zip(row_headers,res))["Address"])
            cType= dict(zip(row_headers,res))["type"]
            vatno=dict(zip(row_headers,res))["vatno"]
            if not vatno:
                vatno=""
            TimeSlot=dict(zip(row_headers,res))["TimeSlot"]
            reservationDate=dict(zip(row_headers,res))["reservationDate"]
            reservationForDate=dict(zip(row_headers,res))["ReservationFor"]
            advancePayment=dict(zip(row_headers,res))["advancePayment"]
            SpecialRequest=dict(zip(row_headers,res))["SpecialRequest"]
            customerID=dict(zip(row_headers,res))["customerID"]
            if not SpecialRequest:
                SpecialRequest="None"
            getRateSql=f"""SELECT idtblbanquetRate_details as id,RateName,RateAmount,NoOfPax, HallName from tblbanquetRate_details  WHERE banquetReservationID=%s GROUP BY idtblbanquetRate_details"""
            cursor.execute(getRateSql,(ResID,),)
            result = cursor.fetchall()
            if result == []:
                data =errormsg("Temporarily unavailable.")
                mydb.close()
                return data,400
            json_data = listtojson(result,cursor.description)
            jsondata={"CustomerName":cName,"Phone":cPhone,"Address":cAddress,"type":cType,"PanNo":vatno,"TimeSlot":TimeSlot,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"advancePayment":advancePayment,"SpecialRequest":SpecialRequest,"customerID":customerID,"RateDetails":json_data}
            billItemdata.setdefault("Details",[]).append(jsondata)

        getBillingAddressSQL=f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
        cursor.execute(getBillingAddressSQL,(ResID,),)
        billingpartyReesult=cursor.fetchall()
        if billingpartyReesult ==[]:
            billingaddressJSON={}
            billItemdata["Details"][0]
            billItemdata["Details"][0]["billingName"]=""
            billItemdata["Details"][0]["billingPanNo"]=""
            billItemdata["Details"][0]["billingPhone"]=""
            billItemdata["Details"][0]["billingEmail"]=""
            billItemdata["Details"][0]["billingAddress"]=""
        else:
            billingaddressJSON=listtojson(billingpartyReesult,cursor.description)
            billingaddress=""
            billingEmail=""
            billingPhone=""
            if billingaddressJSON[0]["Address"] !="":
                billingaddress=addressDecode(billingaddressJSON[0]["Address"])
            if billingaddressJSON[0]["Email"] !="":
                billingEmail=emailDecode(billingaddressJSON[0]["Email"])
            if billingaddressJSON[0]["Phone"] !="":
                billingPhone=phoneDecode(billingaddressJSON[0]["Phone"])
            billItemdata["Details"][0]
            billItemdata["Details"][0]["billingName"]=billingaddressJSON[0]["Name"]
            billItemdata["Details"][0]["billingPanNo"]=billingaddressJSON[0]["PanNo"]
            billItemdata["Details"][0]["billingPhone"]=billingPhone
            billItemdata["Details"][0]["billingEmail"]=billingEmail
            billItemdata["Details"][0]["billingAddress"]=billingaddress
        mydb.close()
        response_data=[]
        response_data.append(billItemdata["Details"][0])
        return response_data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


