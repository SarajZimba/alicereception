from flask import Flask, Blueprint,request,jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file26 = Blueprint('app_file26',__name__)
from root.auth.check import token_auth
from root.utils.returnJson import errormsg,resultmsg,successmsg
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg
from root.utils.decodeDetails import *


@app_file26.route("/customerCreditDetails", methods=["POST"])
@cross_origin()
def customerCreditdetails():
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
            data=errormsg("Invalid token.")
            mydb.close()
            return data,400
        if "customerID" not in json or  "outlet" not in json  or json["outlet"]=="" or json["customerID"]=="":
            data=errormsg("Missing parameters.")
            mydb.close()
            return data,400
        get_customer_credit_DetailsSql =f"""select 	idtblbanquetPayment_details as paymentID,paymentDate as paymentDateTime, Total , subTotal,Tax,billno,banquetReservationID from tblbanquetPayment_details where 	customerID=%s and 	paymentType='billEntry' and Outlet_Name=%s  GROUP by idtblbanquetPayment_details ORDER BY idtblbanquetPayment_details DESC"""
        cursor.execute(get_customer_credit_DetailsSql,(json["customerID"],json["outlet"],),)
        creditWiseBillResult = cursor.fetchall()
        if creditWiseBillResult == []:
            creditWiseBillJson = errormsg("No data available.")
        else:
            row_headers=[x[0] for x in cursor.description] 
            creditWiseBillJson=[]
            for res in creditWiseBillResult:

                banquetReservationID=dict(zip(row_headers,res))["banquetReservationID"]
                Tax=dict(zip(row_headers,res))["Tax"]
                Total=dict(zip(row_headers,res))["Total"]
                billno=dict(zip(row_headers,res))["billno"]
                paymentDateTime=dict(zip(row_headers,res))["paymentDateTime"]
                subTotal=dict(zip(row_headers,res))["subTotal"]
                paymentID=dict(zip(row_headers,res))["paymentID"]

                getBillingAddressSQL=f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
                cursor.execute(getBillingAddressSQL,(banquetReservationID,),)
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
                creditwisebilllistjsondata =  {"billingAddressDetails":billingaddressJSON,"Tax": Tax,"Total":Total,"banquetReservationID":banquetReservationID,"billno":billno,"paymentDateTime":paymentDateTime,"paymentID": paymentID,"subTotal": subTotal}
                creditWiseBillJson.append(creditwisebilllistjsondata)


        get_customer_credit_Payment_DetailsSql =f"""select banquetReservationID,paymentDate as paymentDatetime,	PaymentAmount,PaymentMode,paymentType from tblbanquetPayment_details where  customerID=%s and Outlet_Name=%s and 	(paymentType='Payment' or (paymentType='Advance' and IFNULL(paymentStatus,'')='Billed'))  GROUP BY idtblbanquetPayment_details ORDER BY idtblbanquetPayment_details DESC"""
        cursor.execute(get_customer_credit_Payment_DetailsSql,(json["customerID"],json["outlet"],),)
        creditPaymentResult = cursor.fetchall()
        if creditPaymentResult == []:
            creditWisePaymentJson =  errormsg("No data available.")
        else:
            row_headers=[x[0] for x in cursor.description] 
            creditWisePaymentJson=[]
            for res in creditPaymentResult:
                banquetReservationID= dict(zip(row_headers,res))["banquetReservationID"]
                paymentDatetime=dict(zip(row_headers,res))["paymentDatetime"]
                PaymentAmount=dict(zip(row_headers,res))["PaymentAmount"]
                PaymentMode=dict(zip(row_headers,res))["PaymentMode"]
                paymentType=dict(zip(row_headers,res))["paymentType"]
                getBillingAddressSQL=f"""SELECT * from tblbillingparty WHERE banquetReservationID=%s"""
                cursor.execute(getBillingAddressSQL,(banquetReservationID,),)
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
                creditDetailsJSON={"paymentType":paymentType,"PaymentMode":PaymentMode,"PaymentAmount":PaymentAmount,"paymentDatetime":paymentDatetime,"banquetReservationID":banquetReservationID,"billingAddressDetails":billingaddressJSON}
                creditWisePaymentJson.append(creditDetailsJSON)

        CreditDetails_Paid_Sql =f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s) as TotalCredit,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Advance' and IFNULL(paymentStatus,'')='Billed' and customerID=%s and Outlet_Name=%s)as AdvanceAmount,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
        cursor.execute(CreditDetails_Paid_Sql,(json["customerID"],json["outlet"],json["customerID"],json["outlet"],json["customerID"],json["outlet"],),)
        creditDetailsSummary = cursor.fetchall()
        if creditDetailsSummary == []:
            CreditDetails = errormsg("No data available.")
        else:
            CreditDetails=[]
            row_headers=[x[0] for x in cursor.description] 
            for res in creditDetailsSummary:
                CreditDetails.append(dict(zip(row_headers,res)))
        response_json = {"CreditDetails":CreditDetails[0],"CreditWiseBillList":creditWiseBillJson,"PaymentHistory":creditWisePaymentJson}
        mydb.close()
        return jsonify(response_json),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

