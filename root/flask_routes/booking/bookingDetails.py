
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file23 = Blueprint('app_file23',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *

@app_file23.route("/bookingDetails", methods=["POST"])
@cross_origin()
def bookingDetails():
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
        if not "customerID" in json or json["customerID"]=="":
            data= errormsg("Invalid parameters.")
            mydb.close()
            return data,400
        customerID=json["customerID"]
        getbookingDetailsSql =f"""SELECT CONVERT(c.Tax,CHAR) as vatAmount,CONVERT(c.subTotal,CHAR) as subTotal,CONVERT(c.Total,CHAR) as Total,c.billno,a.idtblbanquetReservation as BanquetReservationId,b.Name as customerName,a.reservationForDate,a.reservationDate,a.NoOfPax,a.advancePayment,a.TimeSlot,b.type, b.vatno FROM `tblbanquetReservation` a , `tblcustomer` b, `tblbanquetPayment_details` c where c.paymentType='billEntry' and c.banquetReservationID=a.idtblbanquetReservation and c.customerID=b.idtblcustomer and a.customerID=b.idtblcustomer  and a.reservationState='Completed' and b.idtblcustomer=%s group by a.idtblbanquetReservation"""
        cursor.execute(getbookingDetailsSql,(customerID,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("No data available.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            vatAmount=dict(zip(row_headers,res))["vatAmount"]
            subTotal=dict(zip(row_headers,res))["subTotal"]
            Total=dict(zip(row_headers,res))["Total"]
            billno=dict(zip(row_headers,res))["billno"]
            BanquetReservationId=dict(zip(row_headers,res))["BanquetReservationId"]
            customerName=dict(zip(row_headers,res))["customerName"]
            reservationForDate=dict(zip(row_headers,res))["reservationForDate"]
            reservationDate=dict(zip(row_headers,res))["reservationDate"]
            NoOfPax=dict(zip(row_headers,res))["NoOfPax"]
            advancePayment=dict(zip(row_headers,res))["advancePayment"]
            TimeSlot=dict(zip(row_headers,res))["TimeSlot"]
            ctype=dict(zip(row_headers,res))["type"]
            vatno =dict(zip(row_headers,res))["vatno"]
            
            getBillingAddressSQL=f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
            cursor.execute(getBillingAddressSQL,(BanquetReservationId,),)
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
            bookingdetailsJson={"billingAddressDetails":billingaddressJSON,"BanquetReservationId": BanquetReservationId, "NoOfPax": NoOfPax, "TimeSlot": TimeSlot, "Total": Total, "advancePayment": advancePayment, "billno": billno, "customerName": customerName, "reservationDate": reservationDate, "reservationForDate": reservationForDate, "subTotal": subTotal, "type": ctype, "vatAmount": vatAmount, "vatno": vatno }
            json_data.append(bookingdetailsJson)
        mydb.close()
        return jsonify(json_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

