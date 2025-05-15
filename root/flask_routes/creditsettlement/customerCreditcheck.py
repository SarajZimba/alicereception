from flask import Flask, Blueprint,request,jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file25 = Blueprint('app_file25',__name__)
from root.auth.check import token_auth
from root.utils.decodeDetails import *
from root.utils.returnJson import errormsg,resultmsg,successmsg



@app_file25.route("/customerCreditData", methods=["POST"])
@cross_origin()
def customerCreditCheck():
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
        if not "outlet" in json or "customerName" not in json:
            data=  errormsg("Missing parameters.")
            mydb.close()
            return data,400
        get_customer_creditSql =f"""SELECT 	a.idtblcustomer as customerID,a.Name as GuestName,a.Email as guestEmail,a.Phone as guestPhone,a.type,	a.vatno FROM tblcustomer a,CreditHistory b where a.Name=b.customerName  and b.Outlet_Name=%s and b.customerName=%s and a.idtblcustomer=b.customerID and b.customerID!='' GROUP BY b.customerID"""
        cursor.execute(get_customer_creditSql,(json["outlet"],json["customerName"],),)
        result = cursor.fetchall()
        if result == []:
            data =  errormsg("No data available.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        json_data=[]
        for res in result:
            guestID=dict(zip(row_headers,res))["customerID"]
            GuestName=dict(zip(row_headers,res))["GuestName"]
            guestEmail= emailDecode(dict(zip(row_headers,res))["guestEmail"])
            guestPhone=phoneDecode(dict(zip(row_headers,res))["guestPhone"])
            customerType= dict(zip(row_headers,res))["type"]  
            customerVAT= dict(zip(row_headers,res))["vatno"]  
            getAmountdueSql=f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s) as TotalCredit,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Advance' and IFNULL(paymentStatus,'')='Billed' and customerID=%s and Outlet_Name=%s)as AdvanceAmount,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
            cursor.execute(getAmountdueSql,(guestID,json["outlet"],guestID,json["outlet"],guestID,json["outlet"],),)
            amountDueresult = cursor.fetchall()
            duerow_headers=[x[0] for x in cursor.description] 
            amountdueDatajson=[]
            for dueres in amountDueresult:
                amountdueDatajson.append(dict(zip(duerow_headers,dueres)))    
            customercreditCheckJson={"customerVAT":customerVAT,"customerType":customerType,"creditDetails":amountdueDatajson,"customerPhone":guestPhone,"customerEmail":guestEmail,"customerID":guestID,"customerName":GuestName}
            json_data.append(customercreditCheckJson)
        mydb.close()
        return jsonify(json_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

