
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file10 = Blueprint('app_file10',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from decimal import Decimal

@app_file10.route("/rateEdit", methods=["POST"])
@cross_origin()
def rateEdit():
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
        if "hall" not in json or not "idtblbanquetRate_details" in json or not "RateName" in json or not "RateAmount" in json or not "NoOfPax" in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        ratedetailsID = json["idtblbanquetRate_details"]
        RateName= json["RateName"]
        RateAmount= json["RateAmount"]
        NoOfPax= json["NoOfPax"]
        hall=json["hall"]


        try:
            float(RateAmount)
        except ValueError:
            data= errormsg("Invalid Rate amount supplied.")
            mydb.close()
            return data,400

        try:
            int(NoOfPax)
        except ValueError:
            data= errormsg("Invalid NoOfPax supplied.")
            mydb.close()
            return data,400


        totalaftertax = (float(RateAmount) * int(NoOfPax)) * 1.13
        totalaftertax = round(totalaftertax,2)

        #Get the current data in the ratedetails table.
        if ratedetailsID=="" or RateName=="" or RateAmount=="" or NoOfPax=="" or hall=="":
            data = errormsg("Empty fields supplied.")
            mydb.close()
            return data,400
        verifyrateEditSql =f"""select	NoOfPax,RateName,RateAmount, RateName,	banquetReservationID,HallName from tblbanquetRate_details where idtblbanquetRate_details=%s"""
        cursor.execute(verifyrateEditSql,(ratedetailsID,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Supplied Id is incorrect.")
            mydb.close()
            return data,400





        ratedataDetailsJSON = listtojson(result,cursor.description)
        banquetReservationID=ratedataDetailsJSON[0]["banquetReservationID"]



        getTotalAdvancePaidSql=f"""SELECT  ifnull(sum(advancePaid),0) as advancePaid,banquetReservationID FROM `tblbanquetPayment_details` WHERE paymentType='Advance' and banquetReservationID=%s"""
        cursor.execute(getTotalAdvancePaidSql,(banquetReservationID,),)
        TotalAdvancePaidresult = cursor.fetchall()
        TotalAdvancePaidDetails = listtojson(TotalAdvancePaidresult,cursor.description)

        totalAdvancePaid=TotalAdvancePaidDetails[0]["advancePaid"]
        totalAdvancePaid=round(totalAdvancePaid,2)
        print(totalAdvancePaid,totalaftertax)
        if totalAdvancePaid>totalaftertax:
            msg = "Total value after tax {} is less than advance amount {}. Cannot save this rate.".format(totalaftertax, totalAdvancePaid)
            data=errormsg(msg)
            return data,400




        previoushallname= ratedataDetailsJSON[0]["HallName"]
        previouosRateName= ratedataDetailsJSON[0]["RateName"]
        previousRateAmount= ratedataDetailsJSON[0]["RateAmount"]
        previousNoOfPax= ratedataDetailsJSON[0]["NoOfPax"]

        # Check is nothing new is there to be updated.
        if previoushallname==hall and previouosRateName==RateName and str(float(previousRateAmount))==str(float(Decimal(RateAmount))) and str(float(previousNoOfPax))==str(float(Decimal(NoOfPax))):
            data = errormsg("Nothing new to change.")
            mydb.close()
            return data,400


        #Check if booking is available for this new hall.
        if previoushallname !=hall:
            getbanquetdetailsSQL=f"""SELECT reservationForDate,Outlet_Name,TimeSlot FROM `tblbanquetReservation` WHERE idtblbanquetReservation=%s"""
            cursor.execute(getbanquetdetailsSQL,(banquetReservationID,),)
            banquetresult = cursor.fetchall()
            banquetdata= listtojson(banquetresult,cursor.description)
            reservationForDate=banquetdata[0]["reservationForDate"]
            Outlet_Name=banquetdata[0]["Outlet_Name"]
            TimeSlot=banquetdata[0]["TimeSlot"]
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
        # Update the new information.
        getRateDetailsSql =f"""insert into tblbanquetRate_details (idtblbanquetRate_details) values (%s) on duplicate key update RateName=%s, RateAmount=%s, NoOfPax=%s,HallName=%s"""
        cursor.execute(getRateDetailsSql,(ratedetailsID,RateName,RateAmount,NoOfPax,hall,),)
        mydb.commit()
        updatebanquetreservationTableSQL=f"""UPDATE `tblbanquetReservation` SET `NoOfPax`=%s WHERE idtblbanquetReservation=%s"""
        cursor.execute(updatebanquetreservationTableSQL,(NoOfPax,banquetReservationID,),)
        mydb.commit()
        updateReservation_detailshallnameSql=f"""UPDATE `tblbanquetReservation_details` SET `HallName`=%s  WHERE banquetReservationID=%s"""
        cursor.execute(updateReservation_detailshallnameSql,(hall,banquetReservationID,),)
        mydb.commit()
        mydb.close()
        return successmsg("Rate edited."),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

