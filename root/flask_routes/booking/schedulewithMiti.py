
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file36 = Blueprint('app_file36',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file36.route("/schedulewithMiti", methods=["POST"])
@cross_origin()
def schedulewithmiti():
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
            return data,400
        if "yearMonth" not in json or json["yearMonth"]=="" or "typeRange" not in json or json["typeRange"]=="":
            data = errormsg("Required parameters not supplied.")
            mydb.close()
            return data,400
        yearMonth = json["yearMonth"]
        typeRange = json["typeRange"]

        allreturnlist=[]
        if typeRange=="ALL":
            getHallDetailsSql=f"""SELECT  a.reservationForDate,a.reservationDate,a.reservationMiti,a.reservationMitiFor,b.HallName,IFNULL(a.paymentStauts,"None") as paymentStauts,a.reservationForDate,a.idtblbanquetReservation,a.customerID,b.TimeSlot,a.NoOfPax,a.Outlet_Name FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and a.reservationState!='Cancelled'  and IFNULL(a.reservationMitiFor,'') like CONCAT(%s, '%') group by a.idtblbanquetReservation"""
            cursor.execute(getHallDetailsSql,(yearMonth,),)
            HallDetailsresult = cursor.fetchall()
            if HallDetailsresult==[]:
                data= errormsg("No data available.")
                mydb.close()
                return data,400
            HallDetailsrow_headers=[u[0] for u in cursor.description] 
            for z in HallDetailsresult:
                reservationForDate= dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                reservationDate= dict(zip(HallDetailsrow_headers,z))["reservationDate"]
                reservationMiti= dict(zip(HallDetailsrow_headers,z))["reservationMiti"]
                reservationMitiFor= dict(zip(HallDetailsrow_headers,z))["reservationMitiFor"]
                pax = dict(zip(HallDetailsrow_headers,z))["NoOfPax"]
                TimeSlot = dict(zip(HallDetailsrow_headers,z))["TimeSlot"]
                customerID = dict(zip(HallDetailsrow_headers,z))["customerID"]
                date = dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                Outlet_Name=dict(zip(HallDetailsrow_headers,z))["Outlet_Name"]
                paymentStauts=dict(zip(HallDetailsrow_headers,z))["paymentStauts"]
                banquetReservationID= dict(zip(HallDetailsrow_headers,z))["idtblbanquetReservation"]
                getCustomernameSql=f"""SELECT Name,type FROM tblcustomer where idtblcustomer=%s limit 1"""
                cursor.execute(getCustomernameSql,(customerID,),)
                customernameresult = cursor.fetchall()
                getCustomernamejson_data = listtojson(customernameresult,cursor.description)
                customername=getCustomernamejson_data[0]["Name"]
                getAmountdueSql=f"""Select (SELECT billno FROM tblbanquetPayment_details where paymentType='billEntry' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s) as billno,(SELECT ifnull(sum(Amount),0)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s and banquetReservationID=%s) as TotalCredit,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Advance' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as AdvanceAmount,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                cursor.execute(getAmountdueSql,(customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,),)
                amountDueresult = cursor.fetchall()
                duerow_headers=[x[0] for x in cursor.description] 
                amountdueDatajson=[]
                for dueres in amountDueresult:
                    amountdueDatajson.append(dict(zip(duerow_headers,dueres)))
                json_data ={"reservationForDate":reservationForDate,"reservationDate":reservationDate,"reservationMiti":reservationMiti,"reservationMitiFor":reservationMitiFor,"paymentStauts":paymentStauts,"banquetReservationID":banquetReservationID,"Outlet":Outlet_Name,"paymentDetails":amountdueDatajson[0],"date":date,"customerName":customername,"paxCount":pax,"timeslot":TimeSlot}
                allreturnlist.append(json_data)



        elif typeRange=="PARTICULAR":
            getHallDetailsSql=f"""SELECT   a.reservationForDate,a.reservationDate,a.reservationMiti,a.reservationMitiFor,b.HallName,IFNULL(a.paymentStauts,"None") as paymentStauts,a.reservationForDate,a.idtblbanquetReservation,a.customerID,b.TimeSlot,a.NoOfPax,a.Outlet_Name FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and a.reservationState!='Cancelled'  and IFNULL(a.reservationMitiFor,'')=%s group by a.idtblbanquetReservation"""
            cursor.execute(getHallDetailsSql,(yearMonth,),)
            HallDetailsresult = cursor.fetchall()
            if HallDetailsresult==[]:
                data= errormsg("No data available.")
                mydb.close()
                return data,400
            HallDetailsrow_headers=[u[0] for u in cursor.description] 
            for z in HallDetailsresult:
                reservationForDate= dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                reservationDate= dict(zip(HallDetailsrow_headers,z))["reservationDate"]
                reservationMiti= dict(zip(HallDetailsrow_headers,z))["reservationMiti"]
                reservationMitiFor= dict(zip(HallDetailsrow_headers,z))["reservationMitiFor"]
                pax = dict(zip(HallDetailsrow_headers,z))["NoOfPax"]
                TimeSlot = dict(zip(HallDetailsrow_headers,z))["TimeSlot"]
                customerID = dict(zip(HallDetailsrow_headers,z))["customerID"]
                date = dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                Outlet_Name=dict(zip(HallDetailsrow_headers,z))["Outlet_Name"]
                paymentStauts=dict(zip(HallDetailsrow_headers,z))["paymentStauts"]
                banquetReservationID= dict(zip(HallDetailsrow_headers,z))["idtblbanquetReservation"]
                getCustomernameSql=f"""SELECT Name,type FROM tblcustomer where idtblcustomer=%s limit 1"""
                cursor.execute(getCustomernameSql,(customerID,),)
                customernameresult = cursor.fetchall()
                getCustomernamejson_data = listtojson(customernameresult,cursor.description)
                customername=getCustomernamejson_data[0]["Name"]
                getAmountdueSql=f"""Select (SELECT billno FROM tblbanquetPayment_details where paymentType='billEntry' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s) as billno,(SELECT ifnull(sum(Amount),0)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s and banquetReservationID=%s) as TotalCredit,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Advance' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as AdvanceAmount,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                cursor.execute(getAmountdueSql,(customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,),)
                amountDueresult = cursor.fetchall()
                duerow_headers=[x[0] for x in cursor.description] 
                amountdueDatajson=[]
                for dueres in amountDueresult:
                    amountdueDatajson.append(dict(zip(duerow_headers,dueres)))
                json_data ={"reservationForDate":reservationForDate,"reservationDate":reservationDate,"reservationMiti":reservationMiti,"reservationMitiFor":reservationMitiFor,"paymentStauts":paymentStauts,"banquetReservationID":banquetReservationID,"Outlet":Outlet_Name,"paymentDetails":amountdueDatajson[0],"date":date,"customerName":customername,"paxCount":pax,"timeslot":TimeSlot}
                allreturnlist.append(json_data)

        else:
            data=errormsg("TYPE not correct.")
            mydb.close()
            return data,400

        mydb.close()
        return jsonify(allreturnlist),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

