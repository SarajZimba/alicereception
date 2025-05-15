
from flask import Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file21 = Blueprint('app_file21',__name__)
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.auth.check import token_auth
from datetime import datetime
import pytz

@app_file21.route("/makePayment", methods=["POST"])
@cross_origin()
def makePayment():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()

        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = errormsg("No token provided.")
            mydb.close()
            mydb.close()
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = errormsg("Invalid token.")
            mydb.close()
            return data,400
        if not "outlet" in json or json["outlet"]=="" or not "PaymentAmount" in json or json["PaymentAmount"]=="" or not "customerID" in json or json["customerID"]=="" or not "PaymentMode" in json or json["PaymentMode"]=="":
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        PaymentAmount = json["PaymentAmount"]
        totalPaymentAmount=0.00
        try:
            totalPaymentAmount=float(PaymentAmount)
        except:
            data = errormsg("Payment amount is invalid.")
            mydb.close()
            return data,400

        customerID = json["customerID"]
        PaymentMode = json["PaymentMode"]
        Outlet_Name=json["outlet"]

        CreditDetails_Paid_Sql =f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s) as TotalCredit,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Advance' and IFNULL(paymentStatus,'')='Billed' and customerID=%s and Outlet_Name=%s)as AdvanceAmount,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
        cursor.execute(CreditDetails_Paid_Sql,(json["customerID"],json["outlet"],json["customerID"],json["outlet"],json["customerID"],json["outlet"],),)
        creditDetailsSummary = cursor.fetchall()
        getcreditDetails = listtojson(creditDetailsSummary,cursor.description)
        RemainingAmount=float(getcreditDetails[0]["RemainingAmount"]) or 0.00
        if totalPaymentAmount > RemainingAmount:
            data = errormsg("Payment is greater than due amount.")
            mydb.close()
            return data,400

        getbanquetDetailsSql =f"""SELECT banquetReservationID,(ifnull(sum(Total),0)-ifnull(sum(advancePaid),0)) as dueLeft,billno from tblbanquetPayment_details where customerID=%s and 	ifnull(paymentStatus,'')!='Paid' and 	paymentType='billEntry'  group by idtblbanquetPayment_details ORDER BY idtblbanquetPayment_details ASC"""
        cursor.execute(getbanquetDetailsSql,(customerID,),)
        result = cursor.fetchall()
        if result == []:
            data =errormsg("Error occured. Please check the banquet reservation ID.")
            mydb.close()
            return data,400
        getbanquetDetails = listtojson(result,cursor.description)

        y=True
        k=0
        banquetDetailslength = len(getbanquetDetails)
        while(y and k<banquetDetailslength):
            if not y:
                return
            else:
                mainjson=getbanquetDetails[k]
                banquetreservationID=mainjson["banquetReservationID"]
                due=float(mainjson["dueLeft"])
                paidSql=f"""SELECT ifnull(sum(PaymentAmount),0) as TotalPayment,banquetReservationID FROM tblbanquetPayment_details where  ifnull(paymentStatus,'')!='Paid'  and 	paymentType='Payment' and banquetReservationID=%s"""
                cursor.execute(paidSql,(banquetreservationID,),)
                result = cursor.fetchall()
                paidJsondata = listtojson(result,cursor.description)
                TotalAmountPaid= paidJsondata[0]["TotalPayment"]
                due = due - float(TotalAmountPaid)
                datetimeToday= datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d %H:%M:%S')
                billno=mainjson["billno"]

                if due ==totalPaymentAmount:
                    insertPaymentSql=f"""INSERT INTO `tblbanquetPayment_details`(`paymentDate`, `PaymentAmount`, `banquetReservationID`, `paymentType`, `PaymentMode`, `customerID`, `Outlet_Name`, `billno`,`paymentStatus`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
                    cursor.execute(insertPaymentSql,(datetimeToday,totalPaymentAmount,banquetreservationID,'Payment',PaymentMode,customerID,Outlet_Name,billno,'Completed',),)
                    mydb.commit()
                    y=False
                    stateCompletedSql = f"""update tblbanquetReservation set paymentStauts='Completed' where idtblbanquetReservation=%s"""
                    cursor.execute(stateCompletedSql,(banquetreservationID,),)
                    mydb.commit()

                    PaymentstateCompletedSql = f"""update tblbanquetPayment_details set paymentStatus='Paid' where banquetReservationID=%s and 	paymentType='billEntry'; """
                    cursor.execute(PaymentstateCompletedSql,(banquetreservationID,),)
                    mydb.commit()

                    k=k+1
                elif due < totalPaymentAmount:
                    diff= totalPaymentAmount-due
                    insertPaymentSql=f"""INSERT INTO `tblbanquetPayment_details`(`paymentDate`, `PaymentAmount`, `banquetReservationID`, `paymentType`, `PaymentMode`, `customerID`, `Outlet_Name`, `billno`,`paymentStatus`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
                    cursor.execute(insertPaymentSql,(datetimeToday,due,banquetreservationID,'Payment',PaymentMode,customerID,Outlet_Name,billno,'Completed',),)
                    mydb.commit()
                    totalPaymentAmount=diff
                    stateCompletedSql = f"""update tblbanquetReservation set paymentStauts='Completed' where idtblbanquetReservation=%s"""
                    cursor.execute(stateCompletedSql,(banquetreservationID,),)
                    mydb.commit()
                    PaymentstateCompletedSql = f"""update tblbanquetPayment_details set paymentStatus='Paid' where banquetReservationID=%s and 	paymentType='billEntry'; """
                    cursor.execute(PaymentstateCompletedSql,(banquetreservationID,),)
                    mydb.commit()
                    k=k+1
                elif due > totalPaymentAmount:
                    insertPaymentSql=f"""INSERT INTO `tblbanquetPayment_details`(`paymentDate`, `PaymentAmount`, `banquetReservationID`, `paymentType`, `PaymentMode`, `customerID`, `Outlet_Name`, `billno`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""
                    cursor.execute(insertPaymentSql,(datetimeToday,totalPaymentAmount,banquetreservationID,'Payment',PaymentMode,customerID,Outlet_Name,billno,),)
                    mydb.commit()
                    y=False

        mydb.close()
        return successmsg("Payment entry inserted."),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


