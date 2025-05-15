
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file18 = Blueprint('app_file18',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *



@app_file18.route("/banquetreport", methods=["POST"])
@cross_origin()
def getcustomerhistorybyname():
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
        if "customerName" not in json  or "state" not in json or "reservationDateEnd" not in json or "reservationDatestart" not in json or "reservationForDatestart" not in json or "reservationForDateEnd" not in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400

        if json["reservationDatestart"] !="" and json["reservationDateEnd"] !="" and json["reservationForDatestart"] !="" and json["reservationForDateEnd"] !="":
            data=errormsg("All dates cannot be supplied together. Only two at a time")
            mydb.close()
            return data,400

        elif json["reservationDatestart"] =="" and json["reservationDateEnd"] =="" and json["reservationForDatestart"] =="" and json["reservationForDateEnd"] =="" and json["state"]=="" and json["customerName"]=="":
            data=errormsg("Empty values supplied. All values cannot be empty.")
            mydb.close()
            return data,400
        elif json["customerName"] !="" and json["reservationDatestart"] !="" and json["reservationDateEnd"] !="" and json["state"] !="":
            customerName=json["customerName"]
            reservationDatestart=json["reservationDatestart"]
            reservationDateEnd=json["reservationDateEnd"]
            state =  json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')  and a.reservationDate between %s and %s and a.reservationState=%s and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,reservationDatestart,reservationDateEnd,state,),)
            result = cursor.fetchall()

        elif json["customerName"] !="" and json["reservationForDatestart"] !="" and json["reservationForDateEnd"] !="" and json["state"] !="":
            customerName=json["customerName"]
            reservationForDatestart=json["reservationForDatestart"]
            reservationForDateEnd=json["reservationForDateEnd"]
            state =  json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')  and a.reservationForDate between %s and %s and a.reservationState=%s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,reservationForDatestart,reservationForDateEnd,state,),)
            result = cursor.fetchall()

        elif json["customerName"] !="" and json["reservationDatestart"] !="" and json["reservationDateEnd"] !="" and json["state"] =="":
            customerName=json["customerName"]
            reservationDatestart=json["reservationDatestart"]
            reservationDateEnd=json["reservationDateEnd"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')  and a.reservationDate between %s and %s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,reservationDatestart,reservationDateEnd,),)
            result = cursor.fetchall()

        elif json["customerName"] !="" and json["reservationForDatestart"] !="" and json["reservationForDateEnd"] !="" and json["state"] =="":
            customerName=json["customerName"]
            reservationForDatestart=json["reservationForDatestart"]
            reservationForDateEnd=json["reservationForDateEnd"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')  and a.reservationForDate between %s and %s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,reservationForDatestart,reservationForDateEnd,),)
            result = cursor.fetchall()

        elif json["reservationDatestart"] !="" and json["reservationDateEnd"] !="" and json["state"] !="":
            reservationDatestart=json["reservationDatestart"]
            reservationDateEnd=json["reservationDateEnd"]
            state =  json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer  and a.reservationDate between %s and %s and a.reservationState=%s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(reservationDatestart,reservationDateEnd,state,),)
            result = cursor.fetchall()

        elif json["reservationForDatestart"] !="" and json["reservationForDateEnd"] !="" and json["state"] !="":
            reservationForDatestart=json["reservationForDatestart"]
            reservationForDateEnd=json["reservationForDateEnd"]
            state =  json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.reservationForDate between %s and %s and a.reservationState=%s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(reservationForDatestart,reservationForDateEnd,state,),)
            result = cursor.fetchall()

        elif json["reservationDatestart"] !="" and json["reservationDateEnd"] !="" and json["state"] =="":
            reservationDatestart=json["reservationDatestart"]
            reservationDateEnd=json["reservationDateEnd"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer  and a.reservationDate between %s and %s   and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(reservationDatestart,reservationDateEnd,),)
            result = cursor.fetchall()
        elif json["reservationForDatestart"] !="" and json["reservationForDateEnd"] !="" and json["state"] =="":
            reservationForDatestart=json["reservationForDatestart"]
            reservationForDateEnd=json["reservationForDateEnd"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.reservationForDate between %s and %s   and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(reservationForDatestart,reservationForDateEnd,),)
            result = cursor.fetchall()

        elif json["customerName"] !="" and json["reservationForDatestart"] =="" and json["reservationForDateEnd"] =="" and json["reservationDatestart"] =="" and json["reservationDateEnd"] =="" and json["state"] !="":
            customerName=json["customerName"]
            state =  json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')  and a.reservationState=%s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,state,),)
            result = cursor.fetchall()

        elif json["customerName"] !="" and json["reservationForDatestart"] =="" and json["reservationForDateEnd"] =="" and json["reservationDatestart"] =="" and json["reservationDateEnd"] =="" and json["state"] =="":
            customerName=json["customerName"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  b.Name like CONCAT(%s, '%')   and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerName,),)
            result = cursor.fetchall()

        elif json["customerName"] =="" and json["reservationForDatestart"] =="" and json["reservationForDateEnd"] =="" and json["reservationDatestart"] =="" and json["reservationDateEnd"] =="" and json["state"] !="":
            state=json["state"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.reservationState=%s  and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(state,),)
            result = cursor.fetchall()


        elif json["customerName"] !="" and json["reservationForDatestart"] =="" and json["reservationForDateEnd"] =="" and json["reservationDatestart"] =="" and json["reservationDateEnd"] =="" and json["state"] !="":
            state=json["state"]
            customerName=json["customerName"]
            get_started_sql =f"""SELECT a.TimeSlot,a.reservationState,a.idtblbanquetReservation , b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.reservationState=%s and  b.Name like CONCAT(%s, '%')   and a.reservationState!='Completed' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(state,customerName,),)
            result = cursor.fetchall()

        if result == []:
            data = errormsg("No results found.")
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
                # advancePaymentMethod= advpaymentmethod[0]["PaymentMode"]
            #getRateSql=f"""SELECT GROUP_CONCAT(HallName SEPARATOR ' / ' ) as HallName, RateName from tblbanquetRate_details  WHERE banquetReservationID=%s"""



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
                Startedjsondata={"TimeSlot":TimeSlot,"billingAddressJSON":billingaddressJSON,"reservationState":reservationState,"idtblbanquetReservation":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancePaymentMethod":advancePaymentMethod,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
            else:
                hall_names = listtojson(rateresult,cursor.description)
                hall_names = hall_names[0]["HallName"]
                Startedjsondata={"TimeSlot":TimeSlot,"billingAddressDetails":billingaddressJSON,"reservationState":reservationState,"idtblbanquetReservation":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancePaymentMethod":advancePaymentMethod,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
        mydb.close()
        return billItemdata["Details"],200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

