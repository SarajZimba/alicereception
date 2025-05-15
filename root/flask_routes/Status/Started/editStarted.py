
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file33 = Blueprint('app_file33',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg

@app_file33.route("/editStarted", methods=["POST"])
@cross_origin()
def editStarted():
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
        if "TimeSlot" not in json or not "reservationForDate" in json or not "banquetReservationID" in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400

        banquetReservationID = json["banquetReservationID"]
        reservationForDate= json["reservationForDate"]
        TimeSlot=json["TimeSlot"]

        # Json validation.
        if TimeSlot=="" or reservationForDate=="" or banquetReservationID=="":
            data = errormsg("Empty fields supplied.")
            mydb.close()
            return data,400
        verifyrateEditSql =f"""select RateName,	HallName from tblbanquetRate_details where banquetReservationID=%s"""
        cursor.execute(verifyrateEditSql,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Supplied ID is incorrect.")
            mydb.close()
            return data,400
        hallnamejson = listtojson(result,cursor.description)
        hall=hallnamejson[0]["HallName"]



        # Check if any there's anything new to udpate.
        getbanquetdetailsSQL=f"""SELECT TimeSlot,reservationForDate,Outlet_Name,idtblbanquetReservation FROM `tblbanquetReservation` WHERE idtblbanquetReservation=%s"""
        cursor.execute(getbanquetdetailsSQL,(banquetReservationID,),)
        banquetresult = cursor.fetchall()
        banquetdata= listtojson(banquetresult,cursor.description)
        Outlet_Name=banquetdata[0]["Outlet_Name"]
        previousreservationForDate=str(banquetdata[0]["reservationForDate"])
        
        previousTimeSlot=banquetdata[0]["TimeSlot"]
        if previousTimeSlot==TimeSlot and previousreservationForDate==reservationForDate:
            data = errormsg("Nothing new to change.")
            mydb.close()
            return data,400


        # Verify if booking for the new date and timeslot if available.
        banquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND a.TimeSlot=%s GROUP BY a.idtblbanquetReservation"""
        cursor.execute(banquetReservationCheckSql,(reservationForDate,Outlet_Name,hall,TimeSlot,),)
        result = cursor.fetchall()
        if TimeSlot=='Both':
            bothbanquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND (a.TimeSlot='Lunch' OR a.TimeSlot='Dinner') GROUP BY a.idtblbanquetReservation"""
            cursor.execute(bothbanquetReservationCheckSql,(reservationForDate,Outlet_Name,hall,),)
            lunchordinnercheck = cursor.fetchall()
        else:
            lunchordinnercheck=[]
        if TimeSlot=='Lunch' or TimeSlot=='Dinner':
            bothbanquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND a.TimeSlot='Both' GROUP BY a.idtblbanquetReservation"""
            cursor.execute(bothbanquetReservationCheckSql,(reservationForDate,Outlet_Name,hall,),)
            bothresult = cursor.fetchall()
        else:
            bothresult=[]

        if result !=[] or bothresult!=[] or lunchordinnercheck!=[]:
            data = errormsg("Booking not available for this time.")
            mydb.close()
            return data,400
        # Update the information.
        getRateDetailsSql =f"""UPDATE `tblbanquetReservation` SET `reservationForDate`=%s,`TimeSlot`=%s WHERE idtblbanquetReservation=%s"""
        cursor.execute(getRateDetailsSql,(reservationForDate,TimeSlot,banquetReservationID,),)
        mydb.commit()
        updatebanquetreservationTableSQL=f"""UPDATE `tblbanquetReservation_details` SET `TimeSlot`=%s WHERE banquetReservationID=%s"""
        cursor.execute(updatebanquetreservationTableSQL,(TimeSlot,banquetReservationID,),)
        mydb.commit()
        mydb.close()
        return successmsg("Timeslot and reservationfordate updated successfully."),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

