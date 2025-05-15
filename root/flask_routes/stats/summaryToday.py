
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file28 = Blueprint('app_file28',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from datetime import datetime
import pytz

@app_file28.route("/stats", methods=["POST"])
@cross_origin()
def summaryToday():
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
        datetimeToday= datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d')
        getSummary =f"""SELECT reservationForDate,IFNULL(sum(NoOfPax),0) as totalPax,count(idtblbanquetReservation) as reservationCount FROM `tblbanquetReservation` WHERE IFNULL(paymentStauts,'')!='Completed' and reservationState='Finalized' and reservationForDate=%s"""
        cursor.execute(getSummary,(datetimeToday,),)
        reportTodayResult=cursor.fetchall()
        if reportTodayResult==[]:
            data=errormsg("No data available.")
            mydb.close()
            return data,400
        reportToday = listtojson(reportTodayResult,cursor.description)
        totalPax=reportToday[0]["totalPax"]
        reservationCount=reportToday[0]["reservationCount"]
        reservationForDate=reportToday[0]["reservationForDate"]
        getLunchDetailsSql=f"""SELECT c.Name, b.HallName,a.NoOfPax as PaxCount,a.advancePayment,a.SpecialRequest,a.reservationDate as ReservationCreatedOn  FROM `tblbanquetReservation` a,`tblbanquetReservation_details` b, `tblcustomer` c WHERE IFNULL(a.paymentStauts,'')!='Completed' and a.idtblbanquetReservation=b.banquetReservationID and a.customerID= c.idtblcustomer and a.reservationForDate=%s and a.TimeSlot='Lunch' and a.reservationState='Finalized' GROUP BY a.idtblbanquetReservation"""
        cursor.execute(getLunchDetailsSql,(datetimeToday,),)
        LunchDetailsResult=cursor.fetchall()
        if LunchDetailsResult==[]:
            LunchDetailsjson=[]
        else:
            LunchDetailsjson = listtojson(LunchDetailsResult,cursor.description)
        getDinnerDetailsSql=f"""SELECT c.Name, b.HallName,a.NoOfPax as PaxCount,a.advancePayment,a.SpecialRequest,a.reservationDate as ReservationCreatedOn  FROM `tblbanquetReservation` a,`tblbanquetReservation_details` b, `tblcustomer` c WHERE IFNULL(a.paymentStauts,'')!='Completed' and a.idtblbanquetReservation=b.banquetReservationID and a.customerID= c.idtblcustomer and a.reservationForDate=%s and a.TimeSlot='Dinner' and a.reservationState='Finalized' GROUP BY a.idtblbanquetReservation"""
        cursor.execute(getDinnerDetailsSql,(datetimeToday,),)
        DinnerDetailsResult=cursor.fetchall()
        if DinnerDetailsResult==[]:
            DinnerDetailsjson=[]
        else:
            DinnerDetailsjson = listtojson(DinnerDetailsResult,cursor.description)
        getBothDetailsSql=f"""SELECT c.Name, b.HallName,a.NoOfPax as PaxCount,a.advancePayment,a.SpecialRequest,a.reservationDate as ReservationCreatedOn  FROM `tblbanquetReservation` a,`tblbanquetReservation_details` b, `tblcustomer` c WHERE IFNULL(a.paymentStauts,'')!='Completed' and a.idtblbanquetReservation=b.banquetReservationID and a.customerID= c.idtblcustomer and a.reservationForDate=%s and a.TimeSlot='Both' and a.reservationState='Finalized' GROUP BY a.idtblbanquetReservation"""
        cursor.execute(getBothDetailsSql,(datetimeToday,),)
        BothDetailsResult=cursor.fetchall()
        if BothDetailsResult==[]:
            BothDetailsjson=[]
        else:
            BothDetailsjson = listtojson(BothDetailsResult,cursor.description)
        response_data = {"reservationForDate":reservationForDate,"BothDetailsjson":BothDetailsjson,"DinnerDetailsjson":DinnerDetailsjson,"LunchDetailsjson":LunchDetailsjson,"totalPax":totalPax,"reservationCount":reservationCount}


        mydb.close()
        return jsonify(response_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


