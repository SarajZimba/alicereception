from flask import  Blueprint,request,jsonify
import mysql.connector
from flask_cors import cross_origin
import os
from dotenv import load_dotenv
load_dotenv()
app_file27 = Blueprint('app_file27',__name__)
from root.auth.check import token_auth
from root.utils.decodeDetails import *
from root.utils.returnJson import errormsg,resultmsg,successmsg




@app_file27.route("/customerCreditleft", methods=["POST"])
@cross_origin()
def CustomerCreditLeft():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        json = request.get_json()
        if "token" not in json  or not any([json["token"]])  or json["token"]=="":
            data = {"error":"No token provided."}
            mydb.close()
            return data,400
        token = json["token"]
        if not token_auth(token):
            data = {"error":"Invalid token."}
            mydb.close()
            return data,400
        if not "outlet" in json or json["outlet"]=="" or not "type" in json or json["type"]=="":
            data= {"error":"Missing parameters."}
            mydb.close()
            return data,400
        if not json["type"]=='All' and not json["type"]=='Ranged':
            data=errormsg("Type can either be All or Ranged.")
            mydb.close()
            return data,400
        if json["type"]=='All':
            guestIDsql=f"""SELECT DISTINCT customerID as guestID, customerName as GuestName from CreditHistory where 	creditState='billEntry' and customerID!=''  and Outlet_Name=%s"""
            cursor.execute(guestIDsql,(json["outlet"],),)
            result = cursor.fetchall()
            if result == []:
                data = {"error":"No data available."}
                mydb.close()
                return data,400
            row_headers=[x[0] for x in cursor.description] 
            GuestIDjson=[]
            for res in result:
                GuestIDjson.append(dict(zip(row_headers,res)))
            json_data=[]
            for x in GuestIDjson:
                guestID=x["guestID"]
                creditSummaryDetailsSql=f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s) as TotalCredit,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Advance' and IFNULL(paymentStatus,'')='Billed' and customerID=%s and Outlet_Name=%s)as AdvanceAmount,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s)as TotalPaymentMade, (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                cursor.execute(creditSummaryDetailsSql,(guestID,json["outlet"],guestID,json["outlet"],guestID,json["outlet"],),)
                result = cursor.fetchall()
                row_headers=[z[0] for z in cursor.description] 
                creditSummaryjson=[]
                for res in result:
                    creditSummaryjson.append(dict(zip(row_headers,res)))
                try:
                    if float(creditSummaryjson[0]["RemainingAmount"]):
                        creditSummaryPersonalDetailsSql=f"""Select Name,Email,Phone,Address,idtblcustomer as customerID,type,vatno from tblcustomer where idtblcustomer=%s limit 1"""
                        cursor.execute(creditSummaryPersonalDetailsSql,(guestID,),)
                        privateSummaryDetails = cursor.fetchall()
                        row_headers2=[q[0] for q in cursor.description] 
                        creditSummaryPrivatejson=[]
                        for x in privateSummaryDetails:
                            guest=dict(zip(row_headers2,x))["Name"]
                            guestEmail= emailDecode(dict(zip(row_headers2,x))["Email"])
                            guestPhone=phoneDecode(dict(zip(row_headers2,x))["Phone"])
                            guestAddress=addressDecode(dict(zip(row_headers2,x))["Address"])
                            customerType= dict(zip(row_headers2,x))["type"]  
                            customerVAT= dict(zip(row_headers2,x))["vatno"]
                            customerID=dict(zip(row_headers2,x))["customerID"]
                            customerData_json={"customerID":customerID,"vatNo":customerVAT,"guestType":customerType,"guestAddress":guestAddress,"guestPhone":guestPhone,"guestEmail":guestEmail,"guest":guest,"guestPhone":guestPhone}
                            creditSummaryPrivatejson.append(customerData_json)
                        jsondataObject={"guestVatNo":creditSummaryPrivatejson[0]["vatNo"],"guestType":creditSummaryPrivatejson[0]["guestType"],"guestPhone":creditSummaryPrivatejson[0]["guestPhone"],"customerID":creditSummaryPrivatejson[0]["customerID"],"guestEmail":creditSummaryPrivatejson[0]["guestEmail"],"guestAddress":creditSummaryPrivatejson[0]["guestAddress"],"guest":creditSummaryPrivatejson[0]["guest"],"AdvanceAmount":creditSummaryjson[0]["AdvanceAmount"],"TotalPaymentMade":creditSummaryjson[0]["TotalPaymentMade"],"TotalCredit":creditSummaryjson[0]["TotalCredit"],"RemainingAmount":creditSummaryjson[0]["RemainingAmount"]}
                        json_data.append(jsondataObject)
                except Exception as error:
                    if not creditSummaryjson[0]["RemainingAmount"]:
                        creditSummaryjson[0]["RemainingAmount"]=creditSummaryjson[0]["TotalCredit"]
                    creditSummaryPersonalDetailsSql=f"""Select Name,Email,Phone,Address,idtblcustomer as customerID,type,vatno from tblcustomer where idtblcustomer=%s limit 1"""
                    cursor.execute(creditSummaryPersonalDetailsSql,(guestID,),)
                    privateSummaryDetails = cursor.fetchall()
                    row_headers2=[t[0] for t in cursor.description] 
                    creditSummaryPrivatejson=[]
                    for x in privateSummaryDetails:
                        guest=dict(zip(row_headers,x))["Name"]
                        guestEmail= emailDecode(dict(zip(row_headers2,x))["Email"])
                        guestPhone=phoneDecode(dict(zip(row_headers2,x))["Phone"])
                        guestAddress=addressDecode(dict(zip(row_headers2,x))["Address"])
                        customerType= dict(zip(row_headers2,x))["type"]  
                        customerVAT= dict(zip(row_headers2,x))["vatno"]
                        customerID=dict(zip(row_headers2,x))["customerID"]
                        customerData_json={"customerID":customerID,"vatNo":customerVAT,"guestType":customerType,"guestAddress":guestAddress,"guestPhone":guestPhone,"guestEmail":guestEmail,"guest":guest,"guestPhone":guestPhone}
                        creditSummaryPrivatejson.append(customerData_json)
                    jsondataObject={"guestVatNo":creditSummaryPrivatejson[0]["vatNo"],"guestType":creditSummaryPrivatejson[0]["guestType"],"guestPhone":creditSummaryPrivatejson[0]["guestPhone"],"customerID":creditSummaryPrivatejson[0]["customerID"],"guestEmail":creditSummaryPrivatejson[0]["guestEmail"],"guestAddress":creditSummaryPrivatejson[0]["guestAddress"],"guest":creditSummaryPrivatejson[0]["guest"],"AdvanceAmount":creditSummaryjson[0]["AdvanceAmount"],"TotalPaymentMade":creditSummaryjson[0]["TotalPaymentMade"],"TotalCredit":creditSummaryjson[0]["TotalCredit"],"RemainingAmount":creditSummaryjson[0]["RemainingAmount"]}
                    json_data.append(jsondataObject)
            mydb.commit()
            mydb.close()
            return json_data,200
        if json["type"]=='Ranged':
            if not "dateStart" in json or json["dateStart"]=="" or  not "dateEnd" in json or json["dateEnd"]=="" :
                data= {"error":"Missing parameters."}
                mydb.close()
                return data,400
            startDate=json["dateStart"]
            endDate=json["dateEnd"]
            guestIDsql=f"""SELECT DISTINCT customerID as guestID, customerName as GuestName from CreditHistory where creditState='billEntry' and customerID!=''  and Outlet_Name=%s and Date BETWEEN %s and %s"""
            cursor.execute(guestIDsql,(json["outlet"],startDate,endDate,),)
            result = cursor.fetchall()
            if result == []:
                data = {"error":"No data available."}
                mydb.close()
                return data,400
            row_headers=[x[0] for x in cursor.description] 
            GuestIDjson=[]
            for res in result:
                GuestIDjson.append(dict(zip(row_headers,res)))
            json_data=[]
            for x in GuestIDjson:
                guestID=x["guestID"]
                creditSummaryDetailsSql=f"""Select (SELECT sum(Amount)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and Outlet_Name=%s and Date BETWEEN %s and %s) as TotalCredit,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Advance' and IFNULL(paymentStatus,'')='Billed' and customerID=%s and Outlet_Name=%s and DATE(paymentDate) BETWEEN %s and %s)as AdvanceAmount,(SELECT sum(PaymentAmount) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s and DATE(paymentDate) BETWEEN %s and %s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                cursor.execute(creditSummaryDetailsSql,(guestID,json["outlet"],startDate,endDate,guestID,json["outlet"],startDate,endDate,guestID,json["outlet"],startDate,endDate),)
                result = cursor.fetchall()
                row_headers=[x[0] for x in cursor.description] 
                creditSummaryjson=[]
                for res in result:
                    creditSummaryjson.append(dict(zip(row_headers,res)))
                try:
                    if float(creditSummaryjson[0]["RemainingAmount"]):
                        creditSummaryPersonalDetailsSql=f"""Select Name,Email,Phone,Address,idtblcustomer as customerID,type,vatno from tblcustomer where idtblcustomer=%s limit 1"""
                        cursor.execute(creditSummaryPersonalDetailsSql,(guestID,),)
                        privateSummaryDetails = cursor.fetchall()
                        row_headers2=[r[0] for r in cursor.description] 
                        creditSummaryPrivatejson=[]
                        for x in privateSummaryDetails:
                            guest=dict(zip(row_headers2,x))["Name"]
                            guestEmail= emailDecode(dict(zip(row_headers2,x))["Email"])
                            guestPhone=phoneDecode(dict(zip(row_headers2,x))["Phone"])
                            guestAddress=addressDecode(dict(zip(row_headers2,x))["Address"])
                            customerType= dict(zip(row_headers2,x))["type"]  
                            customerVAT= dict(zip(row_headers2,x))["vatno"]
                            customerID=dict(zip(row_headers2,x))["customerID"]
                            customerData_json={"customerID":customerID,"vatNo":customerVAT,"guestType":customerType,"guestAddress":guestAddress,"guestPhone":guestPhone,"guestEmail":guestEmail,"guest":guest,"guestPhone":guestPhone}
                            creditSummaryPrivatejson.append(customerData_json)
                        jsondataObject={"guestVatNo":creditSummaryPrivatejson[0]["vatNo"],"guestType":creditSummaryPrivatejson[0]["guestType"],"guestPhone":creditSummaryPrivatejson[0]["guestPhone"],"customerID":creditSummaryPrivatejson[0]["customerID"],"guestEmail":creditSummaryPrivatejson[0]["guestEmail"],"guestAddress":creditSummaryPrivatejson[0]["guestAddress"],"guest":creditSummaryPrivatejson[0]["guest"],"AdvanceAmount":creditSummaryjson[0]["AdvanceAmount"],"TotalPaymentMade":creditSummaryjson[0]["TotalPaymentMade"],"TotalCredit":creditSummaryjson[0]["TotalCredit"],"RemainingAmount":creditSummaryjson[0]["RemainingAmount"]}
                        json_data.append(jsondataObject)
                except Exception as error:
                    if not creditSummaryjson[0]["RemainingAmount"]:
                        creditSummaryjson[0]["RemainingAmount"]=creditSummaryjson[0]["TotalCredit"]
                    creditSummaryPersonalDetailsSql=f"""Select Name,Email,Phone,Address,idtblcustomer as customerID,type,vatno from tblcustomer where idtblcustomer=%s limit 1"""
                    cursor.execute(creditSummaryPersonalDetailsSql,(guestID,),)
                    privateSummaryDetails = cursor.fetchall()
                    row_headers2=[z[0] for z in cursor.description] 
                    creditSummaryPrivatejson=[]
                    for x in privateSummaryDetails:
                        guest=dict(zip(row_headers2,x))["Name"]
                        guestEmail= emailDecode(dict(zip(row_headers2,x))["Email"])
                        guestPhone=phoneDecode(dict(zip(row_headers2,x))["Phone"])
                        guestAddress=addressDecode(dict(zip(row_headers2,x))["Address"])
                        customerType= dict(zip(row_headers2,x))["type"]  
                        customerVAT= dict(zip(row_headers2,x))["vatno"]
                        customerID=dict(zip(row_headers2,x))["customerID"]
                        customerData_json={"customerID":customerID,"vatNo":customerVAT,"guestType":customerType,"guestAddress":guestAddress,"guestPhone":guestPhone,"guestEmail":guestEmail,"guest":guest,"guestPhone":guestPhone}
                        creditSummaryPrivatejson.append(customerData_json)
                    jsondataObject={"guestVatNo":creditSummaryPrivatejson[0]["vatNo"],"guestType":creditSummaryPrivatejson[0]["guestType"],"guestPhone":creditSummaryPrivatejson[0]["guestPhone"],"customerID":creditSummaryPrivatejson[0]["customerID"],"guestEmail":creditSummaryPrivatejson[0]["guestEmail"],"guestAddress":creditSummaryPrivatejson[0]["guestAddress"],"guest":creditSummaryPrivatejson[0]["guest"],"AdvanceAmount":creditSummaryjson[0]["AdvanceAmount"],"TotalPaymentMade":creditSummaryjson[0]["TotalPaymentMade"],"TotalCredit":creditSummaryjson[0]["TotalCredit"],"RemainingAmount":creditSummaryjson[0]["RemainingAmount"]}
                    json_data.append(jsondataObject)
            mydb.commit()
            mydb.close()
            return jsonify(json_data),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

