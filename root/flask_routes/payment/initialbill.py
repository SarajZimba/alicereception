
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file20 = Blueprint('app_file20',__name__)
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from datetime import datetime
import pytz
from root.utils.hashDetails import emailHash,phoneHash,addressHash
import re

@app_file20.route("/billing", methods=["POST"])
@cross_origin()
def billing():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if not "billno" in json or json["billno"]=="" or  not "Tax" in json or json["Tax"]=="" or not "subTotal" in json or json["subTotal"]=="" or not "banquetReservationID" in json or json["banquetReservationID"]=="" or not "Total" in json or json["Total"]=="":
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        Tax = json["Tax"]
        subTotal = json["subTotal"]
        billno=json["billno"]
        Total = json["Total"]
        Total=re.sub(',(?!\s+\d$)', '', Total)
        subTotal=re.sub(',(?!\s+\d$)', '', subTotal)
        Tax=re.sub(',(?!\s+\d$)', '', Tax)
        
        try:
            float(Total)
        except ValueError:
            data= errormsg("Invalid Total amount supplied.")
            mydb.close()
            return data,400

        Total = round(float(Total),2)





        banquetReservationID = json["banquetReservationID"]

        getbanquetDetailsSql =f"""SELECT customerID,Outlet_Name FROM `tblbanquetReservation` WHERE idtblbanquetReservation=%s and reservationState='Finalized' """
        cursor.execute(getbanquetDetailsSql,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Error occured. Please check the banquet reservation ID.")
            mydb.close()
            return data,400





        getbanquetDetails = listtojson(result,cursor.description)
        customerID=getbanquetDetails[0]["customerID"]
        Outlet_Name=getbanquetDetails[0]["Outlet_Name"]
        datetimeToday= datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d %H:%M:%S')
        creditTime= datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%I:%M %p')
        creditDate= datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d')
        getTotalAdvancePaidSql=f"""SELECT  ifnull(sum(advancePaid),0) as advancePaid,banquetReservationID FROM `tblbanquetPayment_details` WHERE paymentType='Advance' and banquetReservationID=%s"""
        cursor.execute(getTotalAdvancePaidSql,(banquetReservationID,),)
        TotalAdvancePaidresult = cursor.fetchall()
        TotalAdvancePaidDetails = listtojson(TotalAdvancePaidresult,cursor.description)
        totalAdvancePaid=TotalAdvancePaidDetails[0]["advancePaid"]

        totalAdvancePaid=round(totalAdvancePaid,2)
        if totalAdvancePaid>Total and totalAdvancePaid-Total>5:
            msg = "Advance amount {} is greater than total amount {}.".format(totalAdvancePaid,totalAdvancePaid)
            data=errormsg(msg)
            mydb.close()
            return data,400












        insertBillPaymententrySql=f"""INSERT INTO `tblbanquetPayment_details`(`paymentDate`, `banquetReservationID`, `paymentType`, `customerID`, `Total`, `subTotal`, `Tax`, `Outlet_Name`,`billno`,`advancePaid`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(insertBillPaymententrySql,(datetimeToday,banquetReservationID,'billEntry',customerID,Total,subTotal,Tax,Outlet_Name,billno,totalAdvancePaid,),)
        mydb.commit()

        # getpaymentIDsql=f"""SELECT idtblbanquetPayment_details as paymentID,banquetReservationID FROM `tblbanquetPayment_details` WHERE paymentDate=%s and banquetReservationID=%s and paymentType=%s and customerID=%s and Total=%s and subTotal=%s and Tax=%s and Outlet_Name=%s limit 1"""
        # cursor.execute(getpaymentIDsql,(datetimeToday,banquetReservationID,'billEntry',customerID,Total,subTotal,Tax,Outlet_Name,),)
        # result = cursor.fetchall()
        
        # getpaymentID = listtojson(result,cursor.description)
        # paymentID = getpaymentID[0]["paymentID"]
        
        
        getpaymentID = cursor.lastrowid
        paymentID = getpaymentID


        getCustomerDetailsSql=f"""SELECT name as customerName,Address,Email,Phone,type,vatno FROM `tblcustomer` WHERE idtblcustomer=%s limit 1"""
        cursor.execute(getCustomerDetailsSql,(customerID,),)
        result = cursor.fetchall()
        getcustomerDetails = listtojson(result,cursor.description)
        customerName=getcustomerDetails[0]["customerName"] or ""
        customerType=getcustomerDetails[0]["type"] or ""
        customerVat=getcustomerDetails[0]["vatno"] or ""
        customerAddress=getcustomerDetails[0]["Address"] or ""
        customerEmail=getcustomerDetails[0]["Email"] or ""
        customerPhone=getcustomerDetails[0]["Phone"] or ""

        insertCreditSql=f"""INSERT INTO `CreditHistory`(`Date`, `Amount`, `billprintTime`, `customerID`, `creditState`, `banquetReservationID`, `paymentID`, `Outlet_Name`,`customerName`,`type`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(insertCreditSql,(creditDate,Total,creditTime,customerID,'billEntry',banquetReservationID,paymentID,Outlet_Name,customerName,customerType,),)
        mydb.commit()



        if totalAdvancePaid==Total or (((Total-totalAdvancePaid)<=1) and ((Total-totalAdvancePaid)>=0)) or ((totalAdvancePaid-Total)<=5 and (totalAdvancePaid-Total)>=0):
            totalAdvancePaid=Total
            print(totalAdvancePaid,Total)
            stateCompletedSql = f"""update tblbanquetReservation set paymentStauts='Completed' where idtblbanquetReservation=%s"""
            cursor.execute(stateCompletedSql,(banquetReservationID,),)
            mydb.commit()

            PaymentstateCompletedSql = f"""update tblbanquetPayment_details set paymentStatus='Paid' ,advancePaid=%s where banquetReservationID=%s and 	paymentType='billEntry'; """
            cursor.execute(PaymentstateCompletedSql,(totalAdvancePaid,banquetReservationID,),)
            mydb.commit()

            stateCompletedSql = f"""update tblbanquetPayment_details set paymentStatus='Billed',advancePaid=%s,PaymentAmount=%s where	paymentType='Advance' and  banquetReservationID=%s"""
            cursor.execute(stateCompletedSql,(totalAdvancePaid,totalAdvancePaid,banquetReservationID,),)
            mydb.commit()

            stateCompletedSql = f"""update tblbanquetReservation set reservationState='Completed',advancePayment=%s where idtblbanquetReservation=%s"""
            cursor.execute(stateCompletedSql,(totalAdvancePaid,banquetReservationID,),)
            mydb.commit()


            checkexistsSQL =f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
            cursor.execute(checkexistsSQL,(banquetReservationID,),)
            result = cursor.fetchall()
            if result == []:
                insertBillingPartySQL=f"""INSERT INTO `tblbillingparty`(`banquetReservationID`, `Name`, `PanNo`, `Address`, `Phone`, `Email`) VALUES (%s,%s,%s,%s,%s,%s);"""
                cursor.execute(insertBillingPartySQL,(banquetReservationID,customerName,customerVat,customerAddress,customerPhone,customerEmail,),)
                mydb.commit()

            mydb.close()
            return successmsg("Bill inserted and payment is completed."),200




        stateCompletedSql = f"""update tblbanquetReservation set reservationState='Completed' where idtblbanquetReservation=%s"""
        cursor.execute(stateCompletedSql,(banquetReservationID,),)
        mydb.commit()
        stateCompletedSql = f"""update tblbanquetPayment_details set paymentStatus='Billed' where	paymentType='Advance' and  banquetReservationID=%s"""
        cursor.execute(stateCompletedSql,(banquetReservationID,),)
        mydb.commit()


        checkexistsSQL =f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
        cursor.execute(checkexistsSQL,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            insertBillingPartySQL=f"""INSERT INTO `tblbillingparty`(`banquetReservationID`, `Name`, `PanNo`, `Address`, `Phone`, `Email`) VALUES (%s,%s,%s,%s,%s,%s);"""
            cursor.execute(insertBillingPartySQL,(banquetReservationID,customerName,customerVat,customerAddress,customerPhone,customerEmail,),)
            mydb.commit()



        mydb.close()
        return successmsg("Bill inserted."),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


