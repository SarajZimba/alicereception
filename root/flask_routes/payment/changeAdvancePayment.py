from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file38 = Blueprint('app_file38',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import successmsg,errormsg
from root.utils.converttoJson import listtojson
from datetime import datetime
import pytz

@app_file38.route("/changeAdvancePayment", methods=["POST"])
@cross_origin()
def changeAdvancePayment():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()



        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data =errormsg("No token provided.")
            mydb.close()
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            mydb.close()
            return data,400

        if "paymentMethod" not in json or "advanceAmount" not in json or json["advanceAmount"]=="" or "banquetReservationID" not in json or json["banquetReservationID"]=="" :
            data= errormsg("banquetReservationID or advanceAmount or paymentMethod not supplied.")
            mydb.close()
            return data,400

        banquetReservationID=json["banquetReservationID"]
        advanceAmount=json["advanceAmount"]
        paymentMethod = json["paymentMethod"]
        

        try:
            float(advanceAmount)
        except ValueError:
            data= errormsg("Invalid advanceAmount supplied.")
            mydb.close()
            return data,400

        getPaymentDetailsSql =f"""SELECT a.idtblbanquetPayment_details,a.paymentDate,a.PaymentAmount from tblbanquetPayment_details a, tblbanquetReservation b WHERE  a.banquetReservationID=%s AND b.idtblbanquetReservation=a.banquetReservationID and a.paymentType='Advance' GROUP BY a.idtblbanquetPayment_details"""
        cursor.execute(getPaymentDetailsSql,(banquetReservationID,),)
        result = cursor.fetchall()
        if result == []:
            paymentDate=datetime.now(pytz.timezone('Asia/Kathmandu')).strftime('%Y-%m-%d %H:%M:%S')
            PaymentAmount=advanceAmount
            PaymentMode=paymentMethod
            getCustomerDataSQL=f"""select  customerID,IFNULL(Outlet_Name,"") AS Outlet_Name from tblbanquetReservation where idtblbanquetReservation=%s;"""
            cursor.execute(getCustomerDataSQL,(banquetReservationID,),)
            mydb.commit()
            customeridandoutletresult = cursor.fetchall()
            TotalAmountAmount = listtojson(customeridandoutletresult,cursor.description)
    
            Outlet_Name=TotalAmountAmount[0]["Outlet_Name"]
            customerID=TotalAmountAmount[0]["customerID"]
            
            tblbanquetPayment_detailsSql=f"""INSERT INTO `tblbanquetPayment_details` (`paymentDate`, `PaymentAmount`, `banquetReservationID`,`paymentType`,`customerID`,`PaymentMode`,`Outlet_Name`,`advancePaid`) VALUES (%s, %s, %s,"Advance",%s,%s,%s,%s);"""
            cursor.execute(tblbanquetPayment_detailsSql,(paymentDate,PaymentAmount,banquetReservationID,customerID,PaymentMode,Outlet_Name,PaymentAmount),)
            mydb.commit()
            data=successmsg("Advance payment added successfully.")
            mydb.close()
            return jsonify(data),200



        checkPaymentStatus=f"""SELECT * FROM `tblbanquetPayment_details` WHERE paymentType='Advance'  and paymentStatus IS NULL and banquetReservationID=%s"""
        cursor.execute(checkPaymentStatus,(banquetReservationID,),)
        result=cursor.fetchall()
        if result ==[]:
            data= errormsg("Cannot change advance payment.")
            mydb.close()
            return data,400



        getTotalAmount=f"""SELECT IFNULL((1.13 * (RateAmount * NoOfPax)),0) as TotalAfterTax FROM `tblbanquetRate_details` WHERE banquetReservationID=%s"""
        cursor.execute(getTotalAmount,(banquetReservationID,),)
        totalAmountResult=cursor.fetchall()
        if totalAmountResult ==[]:
            data= errormsg("Cannot change advance payment.")
            mydb.close()
            return data,400


        TotalAmountAmount = listtojson(totalAmountResult,cursor.description)
        totalAmount = TotalAmountAmount[0]["TotalAfterTax"] or "0"
        totalAmount = float(totalAmount)
        totalAmount=round(totalAmount,2)
        advanceAmount=round(float(advanceAmount),2)
        print(advanceAmount,totalAmount)
        print(type(advanceAmount),type(totalAmount))

        if advanceAmount>totalAmount:
            msg = "Advance amount {} cannot be greater than total amount {}".format(advanceAmount,totalAmount)
            data= errormsg(msg)
            mydb.close()
            return data,400



        stateCompletedSql = f"""update tblbanquetPayment_details set PaymentAmount=%s, advancePaid=%s where paymentType='Advance' and  banquetReservationID=%s and  paymentStatus IS NULL"""
        cursor.execute(stateCompletedSql,(advanceAmount,advanceAmount,banquetReservationID,),)
        mydb.commit()


        stateCompletedSql = f"""update tblbanquetReservation set advancePayment=%s where idtblbanquetReservation=%s and paymentStauts IS NULL;"""
        cursor.execute(stateCompletedSql,(advanceAmount,banquetReservationID,),)
        mydb.commit()


        data=successmsg("Advance payment updated successfully.")
        mydb.close()
        return jsonify(data),200
    except Exception as error:
        print(error)
        data ={'error':str(error)}
        return data,400

