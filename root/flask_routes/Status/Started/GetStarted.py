
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file7 = Blueprint('app_file7',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *

@app_file7.route("/getStarted", methods=["POST"])
@cross_origin()
def GetStarted():
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
        get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation as idtblbanquetReservation, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID= b.idtblcustomer and a.reservationState='Started' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
        cursor.execute(get_started_sql)
        result = cursor.fetchall()
        if result == []:
            data = errormsg("Temporarily unavailable.")
            mydb.close()
            return data,400

        row_headers=[x[0] for x in cursor.description] 
        billItemdata ={}
        for res in result:
            idtblbanquetReservation = dict(zip(row_headers,res))["idtblbanquetReservation"]
            Name = dict(zip(row_headers,res))["Name"]
            customerID = dict(zip(row_headers,res))["customerID"]
            Outlet_Name = dict(zip(row_headers,res))["Outlet_Name"]
            advancePayment = dict(zip(row_headers,res))["advancePayment"]
            NoOfPax = dict(zip(row_headers,res))["NoOfPax"]
            reservationDate = dict(zip(row_headers,res))["reservationDate"]
            reservationForDate = dict(zip(row_headers,res))["reservationForDate"]
            reservationState=dict(zip(row_headers,res))["reservationState"]
            TimeSlot=dict(zip(row_headers,res))["TimeSlot"]
            
            advancePaymentMethod= ""
            getPaymentMethodAndAmount=f"""SELECT IFNULL(PaymentMode,"") as PaymentMode FROM `tblbanquetPayment_details` WHERE paymentType='Advance' and banquetReservationID=%s"""
            cursor.execute(getPaymentMethodAndAmount,(idtblbanquetReservation,),)
            result=cursor.fetchall()
            if result !=[]:
                advancePaymentMethod=result[0][0] or ""
            
            getBillingAddressSQL=f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
            cursor.execute(getBillingAddressSQL,(idtblbanquetReservation,),)
            billingpartyReesult=cursor.fetchall()
            if billingpartyReesult ==[]:
                billingaddressJSON={}
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
                billingaddressJSON={"Name":billingaddressJSON[0]["Name"],"PanNo":billingaddressJSON[0]["PanNo"],"banquetReservationID":billingaddressJSON[0]["banquetReservationID"],"Phone":billingPhone,"Email":billingEmail,"Address":billingaddress,"idtblbilling":billingaddressJSON[0]["idtblbilling"]}


            getRateSql=f"""SELECT HallName, RateName from tblbanquetRate_details  WHERE banquetReservationID=%s"""
            cursor.execute(getRateSql,(idtblbanquetReservation,),)
            rateresult = cursor.fetchall()
            if rateresult == []:
                hall_names = ""
                Startedjsondata={"billingAddressDetails":billingaddressJSON,"TimeSlot":TimeSlot,"reservationState":reservationState,"idtblbanquetReservation":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancePaymentMethod":advancePaymentMethod,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
            else:
                hall_names = listtojson(rateresult,cursor.description)
                hall_names = hall_names[0]["HallName"]
                Startedjsondata={"billingAddressDetails":billingaddressJSON,"TimeSlot":TimeSlot,"reservationState":reservationState,"idtblbanquetReservation":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancePaymentMethod":advancePaymentMethod,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
        mydb.close()
        return jsonify(billItemdata["Details"]),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

