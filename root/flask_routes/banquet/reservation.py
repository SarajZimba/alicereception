from flask import Blueprint,request
import mysql.connector
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import pytz
from root.utils.returnJson import errormsg,resultmsg
from root.utils.converttoJson import listtojson
from root.utils.convertDate import convertBStoAD,convertADtoBS
import json



def validate_json(data):
    # Check tblbanquetReservation key
    if "tblbanquetReservation" in data:
        reservation = data["tblbanquetReservation"]
        if isinstance(reservation, dict) and all(key in reservation for key in ["reservationMiti", "reservationMitiFor", "Outlet_Name", "reservationState", "TimeSlot", "customerID", "advancePayment", "NoOfPax"]):
            if reservation["reservationMiti"] and reservation["reservationMitiFor"] and reservation["Outlet_Name"] and reservation["reservationState"] and reservation["TimeSlot"] and reservation["customerID"] and (reservation["advancePayment"] == "" or isinstance(reservation["advancePayment"], str)) and reservation["NoOfPax"]:
                pass
            else:
                return False
        else:
            return False
    else:
        return False

    # Check tblbanquetReservation_details key
    if "tblbanquetReservation_details" in data:
        details = data["tblbanquetReservation_details"]
        if isinstance(details, list) and all(isinstance(detail, dict) and all(key in detail for key in ["HallName", "TimeSlot"]) for detail in details):
            pass
        else:
            return False

    # Check tblbanquetRate_details key
    if "tblbanquetRate_details" in data:
        rate_details = data["tblbanquetRate_details"]
        if isinstance(rate_details, list) and all(isinstance(rate_detail, dict) and all(key in rate_detail for key in ["RateName", "RateAmount", "NoOfPax", "HallName"]) for rate_detail in rate_details):
            pass
        else:
            return False

    # Check tblbanquetPayment_details key if advancePayment is not empty
    if "advancePayment" in reservation and reservation["advancePayment"] != "":
        if "tblbanquetPayment_details" in data:
            payment_details = data["tblbanquetPayment_details"]
            if isinstance(payment_details, list) and all(isinstance(payment_detail, dict) and all(key in payment_detail for key in ["paymentDate", "PaymentAmount","PaymentMode"]) and all(value != "" for value in payment_detail.values()) for payment_detail in payment_details):
                pass
            else:
                return False
    return True

app_file3= Blueprint('app_file3',__name__)
@app_file3.route("/banquetregistration", methods=["POST"])
@cross_origin()
def banquetregistration():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()

        if not validate_json(json):
            data = {"error":"Couldn't save reservation. Please refresh the page and try again. Reason: Required data missing.","errorjson":json}
            mydb.close()
            return data,400

        banquetresJson = json["tblbanquetReservation"]
        reservationMiti=banquetresJson["reservationMiti"]
        reservationMitiFor=banquetresJson["reservationMitiFor"]
        reservationDate = convertBStoAD(reservationMiti)
        reservationForDate=convertBStoAD(reservationMitiFor)
        # reservationDate="{}".format(convert_BS_to_AD(reservationMitidt.year, reservationMitidt.month, reservationMitidt.day))
        # reservationDate='-'.join(str(v) for v in reservationDate)
        # reservationDate=datetime.strptime(reservationDate, '%Y-%M-%d').date()
        # reservationForDate="{}".format(convert_BS_to_AD(reservationMitiFordt.year, reservationMitiFordt.month, reservationMitiFordt.day))
        # reservationForDate='-'.join(str(v) for v in reservationForDate)
        # reservationForDate=datetime.strptime(reservationForDate, '%Y-%M-%d').date()

        Outlet_Name=banquetresJson["Outlet_Name"]
        reservationState=banquetresJson["reservationState"]
        TimeSlot=banquetresJson["TimeSlot"]
        customerID=banquetresJson["customerID"]
        advancePayment=banquetresJson["advancePayment"]
        NoOfPax=banquetresJson["NoOfPax"]
        SpecialRequest=banquetresJson["SpecialRequest"]

        if  "NoOfPax" not in banquetresJson or banquetresJson["NoOfPax"]==""  or  "customerID" not in banquetresJson or banquetresJson["customerID"]==""  or "TimeSlot" not in banquetresJson or banquetresJson["TimeSlot"]==""  or "reservationState" not in banquetresJson or banquetresJson["reservationState"]==""  or  "Outlet_Name" not in banquetresJson or banquetresJson["Outlet_Name"]==""  or "reservationMitiFor" not in banquetresJson or banquetresJson["reservationMitiFor"]==""  or "reservationMiti" not in banquetresJson or banquetresJson["reservationMiti"]=="": 
            data = errormsg("Missing parameters.")
            mydb.close()
            return data,400

        if not advancePayment=="":
            if "tblbanquetPayment_details" not in json:
                data = errormsg("tblbanquetPayment_details not provided.")
                mydb.close()
                return data,400
            payment_detailsJson= json["tblbanquetPayment_details"]
            for z in payment_detailsJson:
                if not "PaymentMode" in z or z["PaymentMode"]=="" or  not "PaymentAmount" in z or z["PaymentAmount"]=="":
                    data=errormsg("Some fields in advanced payment details missing.")
                    mydb.close()
                    return data,400
        cexistsSql = f"""SELECT idtblcustomer FROM tblcustomer WHERE idtblcustomer=%s"""
        cursor.execute(cexistsSql,(customerID,),)
        mydb.commit()
        result = cursor.fetchall()
        if result == []:
            data = errormsg("Customer record does not exist. Registration required.")
            mydb.close()
            return data,400
        try:
            tempbanquetres_detailsJson=json["tblbanquetReservation_details"][0]
            if not "HallName" in tempbanquetres_detailsJson or tempbanquetres_detailsJson["HallName"]=="":
                data= errormsg("Hall Name not provided.")
                mydb.close()
                return data,400
        except:
            data = errormsg("Error occured.")
            mydb.close()
            return data,400
        tempbanquetres_detailsJson=json["tblbanquetReservation_details"]
        banquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE IFNULL(a.reservationState,"")!="Cancelled" and IFNULL(a.reservationState,"")!="Completed" and   a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND a.TimeSlot=%s GROUP BY a.idtblbanquetReservation"""
        cursor.execute(banquetReservationCheckSql,(reservationForDate,Outlet_Name,tempbanquetres_detailsJson[0]["HallName"],TimeSlot,),)
        result = cursor.fetchall()
        if TimeSlot=='Both':
            bothbanquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE IFNULL(a.reservationState,"")!="Cancelled" and IFNULL(a.reservationState,"")!="Completed" and   a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND (a.TimeSlot='Lunch' OR a.TimeSlot='Dinner') GROUP BY a.idtblbanquetReservation"""
            cursor.execute(bothbanquetReservationCheckSql,(reservationForDate,Outlet_Name,tempbanquetres_detailsJson[0]["HallName"],),)
            lunchordinnercheck = cursor.fetchall()
        else:
            lunchordinnercheck=[]
        if TimeSlot=='Lunch' or TimeSlot=='Dinner':
            bothbanquetReservationCheckSql=f"""SELECT a.idtblbanquetReservation, a.reservationDate FROM tblbanquetReservation a,tblbanquetReservation_details b WHERE IFNULL(a.reservationState,"")!="Cancelled" and IFNULL(a.reservationState,"")!="Completed" and   a.idtblbanquetReservation=b.banquetReservationID and a.reservationForDate=%s AND a.Outlet_Name=%s AND b.HallName=%s AND a.TimeSlot='Both' GROUP BY a.idtblbanquetReservation"""
            cursor.execute(bothbanquetReservationCheckSql,(reservationForDate,Outlet_Name,tempbanquetres_detailsJson[0]["HallName"],),)
            bothresult = cursor.fetchall()
        else:
            bothresult=[]
        if result !=[] or bothresult!=[] or lunchordinnercheck!=[]:
            data = errormsg("Booking not available for this time.")
            mydb.close()
            return data,400




        registrationTime=datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d %H:%M:%S')
        tblbanquetReservationSql = f"""INSERT INTO `tblbanquetReservation` (`reservationTime`,`reservationDate`, `reservationForDate`,`Outlet_Name`,`reservationState`,`TimeSlot`,`customerID`,`advancePayment`,`NoOfPax`,`SpecialRequest`,`reservationMiti`,`reservationMitiFor`) VALUES ( %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s);"""
        cursor.execute(tblbanquetReservationSql,(registrationTime,reservationDate,reservationForDate,Outlet_Name,reservationState,TimeSlot,customerID,advancePayment,NoOfPax,SpecialRequest,reservationMiti,reservationMitiFor,),)
        mydb.commit()
        tblbanquetReservationSql=f"""SELECT idtblbanquetReservation, reservationDate FROM tblbanquetReservation WHERE reservationTime=%s and TimeSlot=%s and customerID=%s AND reservationDate=%s AND Outlet_Name=%s AND reservationForDate=%s"""
        cursor.execute(tblbanquetReservationSql,(registrationTime,TimeSlot,customerID,reservationDate,Outlet_Name,reservationForDate,),)
        result = cursor.fetchall()
        idtblbanquetReservation = listtojson(result,cursor.description)
        idtblbanquetReservation = "{}".format(idtblbanquetReservation[0]["idtblbanquetReservation"])
        banquetres_detailsJson=json["tblbanquetReservation_details"]
        for x in banquetres_detailsJson:
            if not ("TimeSlot" not in x or x["TimeSlot"]=="" or "HallName" not in x or x["HallName"]==""):
                detailTimeSlot=x["TimeSlot"]
                detailHallName=x["HallName"]
                tblbanquetReservation_detailsSql=f"""INSERT INTO `tblbanquetReservation_details` (`HallName`, `TimeSlot`, `banquetReservationID`) VALUES ( %s, %s, %s);"""
                cursor.execute(tblbanquetReservation_detailsSql,(detailHallName,detailTimeSlot,idtblbanquetReservation,),)
                mydb.commit()
        banquetrate_detailsJson=json["tblbanquetRate_details"]
        for y in banquetrate_detailsJson:
            RateName=y["RateName"] or ""
            RateAmount=y["RateAmount"] or ""
            rateNoOfPax=y["NoOfPax"] or ""
            rateHallName=y["HallName"] or ""
            if rateHallName[-1]==" ":
                rateHallName=rateHallName[:-1]
            if not( not "HallName" in y or y["HallName"]=="" or not "NoOfPax" in y or y["NoOfPax"]=="" or not "RateAmount" in y or y["RateAmount"]=="" or not "RateName" in y or y["RateName"]==""):
                tblbanquetRate_detailsSql=f"""INSERT INTO `tblbanquetRate_details` ( `RateName`, `RateAmount`, `NoOfPax`, `banquetReservationID`, `HallName`) VALUES ( %s, %s, %s, %s, %s);"""
                cursor.execute(tblbanquetRate_detailsSql,(RateName,RateAmount,rateNoOfPax,idtblbanquetReservation,rateHallName,),)
                mydb.commit()
        if not advancePayment=="":
            payment_detailsJson= json["tblbanquetPayment_details"]
            for z in payment_detailsJson:
                if not "PaymentMode" in z or z["PaymentMode"]=="" or  not "PaymentAmount" in z or z["PaymentAmount"]=="":
                    data=errormsg("Booking made but advance payment not registered. Reason: Missing either paymentDate or PaymentAmount  or PaymentMode or all. ")
                    mydb.close()
                    return data,400
                paymentDate=datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d %H:%M:%S')
                PaymentAmount=z["PaymentAmount"]
                PaymentMode=z["PaymentMode"]
                tblbanquetPayment_detailsSql=f"""INSERT INTO `tblbanquetPayment_details` (`paymentDate`, `PaymentAmount`, `banquetReservationID`,`paymentType`,`customerID`,`PaymentMode`,`Outlet_Name`,`advancePaid`) VALUES (%s, %s, %s,"Advance",%s,%s,%s,%s);"""
                cursor.execute(tblbanquetPayment_detailsSql,(paymentDate,PaymentAmount,idtblbanquetReservation,customerID,PaymentMode,Outlet_Name,PaymentAmount),)
                mydb.commit()
        mydb.close()
        data= resultmsg("Posted successfully")
        return data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400