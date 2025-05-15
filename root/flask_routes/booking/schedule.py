
from flask import Flask, Blueprint,request,jsonify
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file19 = Blueprint('app_file19',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file19.route("/schedule", methods=["POST"])
@cross_origin()
def schedule():
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
        if "startDate" not in json or json["startDate"]=="" or "endDate" not in json or json["endDate"]=="":
            data = errormsg("Dates not supplied.")
            mydb.close()
            return data,400
        startDate = json["startDate"]
        endDate= json["endDate"]
        getLunchHallNames =f"""SELECT DISTINCT HallName FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and (b.TimeSlot="Lunch" or b.TimeSlot="Both"  ) and a.reservationState!='Cancelled'  and a.reservationForDate BETWEEN %s and %s"""
        cursor.execute(getLunchHallNames,(startDate,endDate,),)
        result = cursor.fetchall()
        returndata ={}
        if result != []:
            row_headers=[x[0] for x in cursor.description] 
            for res in result:
                tempHallname = dict(zip(row_headers,res))["HallName"]
                getHallDetailsSql=f"""SELECT  IFNULL(a.paymentStauts,"None") as paymentStauts,a.reservationForDate,a.idtblbanquetReservation,a.customerID,b.TimeSlot,a.NoOfPax,a.Outlet_Name FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and (b.TimeSlot="Lunch" or b.TimeSlot="Both") and b.HallName=%s and a.reservationState!='Cancelled'  and a.reservationForDate BETWEEN %s and %s"""
                cursor.execute(getHallDetailsSql,(tempHallname,startDate,endDate,),)
                HallDetailsresult = cursor.fetchall()
                HallDetailsrow_headers=[u[0] for u in cursor.description] 
                temphalldata ={}
                for z in HallDetailsresult:
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
        
                    json_data ={"banquetReservationID":banquetReservationID,"Outlet":Outlet_Name,"paymentDetails":amountdueDatajson[0],"date":date,"customerName":customername,"paxCount":pax,"timeslot":TimeSlot}
                    temphalldata.setdefault(tempHallname,[]).append(json_data)
                returndata.setdefault('lunch',[]).append(temphalldata)
        
        getdinnerHallNames =f"""SELECT DISTINCT HallName FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and (b.TimeSlot="Dinner" or b.TimeSlot="Both" )  and a.reservationState!='Cancelled' and a.reservationForDate BETWEEN %s and %s"""
        cursor.execute(getdinnerHallNames,(startDate,endDate,),)
        result = cursor.fetchall()
        if result != []:
            row_headers=[x[0] for x in cursor.description] 
            for res in result:
                tempHallname = dict(zip(row_headers,res))["HallName"]
                getHallDetailsSql=f"""SELECT  IFNULL(a.paymentStauts,"None") as paymentStauts,a.reservationForDate,a.idtblbanquetReservation,a.customerID,b.TimeSlot,a.NoOfPax,a.Outlet_Name  FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and (b.TimeSlot="Dinner" or b.TimeSlot="Both")  and b.HallName=%s and a.reservationState!='Cancelled'  and a.reservationForDate BETWEEN %s and %s"""
                cursor.execute(getHallDetailsSql,(tempHallname,startDate,endDate,),)
                HallDetailsresult = cursor.fetchall()
                HallDetailsrow_headers=[u[0] for u in cursor.description] 
                temphalldata ={}
                for z in HallDetailsresult:
                    pax = dict(zip(HallDetailsrow_headers,z))["NoOfPax"]
                    TimeSlot = dict(zip(HallDetailsrow_headers,z))["TimeSlot"]
                    customerID = dict(zip(HallDetailsrow_headers,z))["customerID"]
                    date = dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                    paymentStauts=dict(zip(HallDetailsrow_headers,z))["paymentStauts"]
                    banquetReservationID= dict(zip(HallDetailsrow_headers,z))["idtblbanquetReservation"]
                    getCustomernameSql=f"""SELECT Name,type FROM tblcustomer where idtblcustomer=%s limit 1"""
                    cursor.execute(getCustomernameSql,(customerID,),)
                    customernameresult = cursor.fetchall()
                    getCustomernamejson_data = listtojson(customernameresult,cursor.description)
                    customername=getCustomernamejson_data[0]["Name"]
                    Outlet_Name=dict(zip(HallDetailsrow_headers,z))["Outlet_Name"]
                    getAmountdueSql=f"""Select (SELECT billno FROM tblbanquetPayment_details where paymentType='billEntry' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s) as billno,(SELECT ifnull(sum(Amount),0)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s and banquetReservationID=%s) as TotalCredit,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Advance' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as AdvanceAmount,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                    cursor.execute(getAmountdueSql,(customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,),)
                    amountDueresult = cursor.fetchall()
                    duerow_headers=[x[0] for x in cursor.description] 
                    amountdueDatajson=[]
                    for dueres in amountDueresult:
                        amountdueDatajson.append(dict(zip(duerow_headers,dueres)))
                    json_data ={"banquetReservationID":banquetReservationID,"Outlet":Outlet_Name,"paymentDetails":amountdueDatajson[0],"date":date,"customerName":customername,"paxCount":pax,"timeslot":TimeSlot}
                    temphalldata.setdefault(tempHallname,[]).append(json_data)
                returndata.setdefault('dinner',[]).append(temphalldata)
        
        getBothHallNames =f"""SELECT DISTINCT HallName FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and b.TimeSlot="Both" and a.reservationState!='Cancelled'  and a.reservationForDate BETWEEN %s and %s"""
        cursor.execute(getBothHallNames,(startDate,endDate,),)
        result = cursor.fetchall()
        if result != []:
            row_headers=[x[0] for x in cursor.description] 
            for res in result:
                tempHallname = dict(zip(row_headers,res))["HallName"]
                getHallDetailsSql=f"""SELECT  IFNULL(a.paymentStauts,"None") as paymentStauts,a.reservationForDate,a.idtblbanquetReservation,a.customerID,b.TimeSlot,a.NoOfPax,a.Outlet_Name  FROM tblbanquetReservation a, tblbanquetReservation_details b WHERE a.idtblbanquetReservation=b.banquetReservationID and b.TimeSlot="Both" and b.HallName=%s and a.reservationState!='Cancelled'  and a.reservationForDate BETWEEN %s and %s"""
                cursor.execute(getHallDetailsSql,(tempHallname,startDate,endDate,),)
                HallDetailsresult = cursor.fetchall()
                HallDetailsrow_headers=[u[0] for u in cursor.description] 
                temphalldata ={}
                for z in HallDetailsresult:
                    pax = dict(zip(HallDetailsrow_headers,z))["NoOfPax"]
                    TimeSlot = dict(zip(HallDetailsrow_headers,z))["TimeSlot"]
                    customerID = dict(zip(HallDetailsrow_headers,z))["customerID"]
                    date = dict(zip(HallDetailsrow_headers,z))["reservationForDate"]
                    banquetReservationID= dict(zip(HallDetailsrow_headers,z))["idtblbanquetReservation"]
                    getCustomernameSql=f"""SELECT Name,type FROM tblcustomer where idtblcustomer=%s limit 1"""
                    cursor.execute(getCustomernameSql,(customerID,),)
                    customernameresult = cursor.fetchall()
                    getCustomernamejson_data = listtojson(customernameresult,cursor.description)
                    customername=getCustomernamejson_data[0]["Name"]
                    Outlet_Name=dict(zip(HallDetailsrow_headers,z))["Outlet_Name"]
                    paymentStauts=dict(zip(HallDetailsrow_headers,z))["paymentStauts"]
                    getAmountdueSql=f"""Select (SELECT billno FROM tblbanquetPayment_details where paymentType='billEntry' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s) as billno,(SELECT ifnull(sum(Amount),0)  FROM CreditHistory where 	creditState='billEntry' and   customerID=%s  and 	Outlet_Name=%s and banquetReservationID=%s) as TotalCredit,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Advance' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as AdvanceAmount,(SELECT ifnull(sum(PaymentAmount),0) from tblbanquetPayment_details where paymentType='Payment' and customerID=%s and Outlet_Name=%s and banquetReservationID=%s)as TotalPaymentMade,  (SELECT ifnull(TotalCredit,0)-ifnull(TotalPaymentMade,0)-ifnull(AdvanceAmount,0)) AS RemainingAmount"""
                    cursor.execute(getAmountdueSql,(customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,customerID,Outlet_Name,banquetReservationID,),)
                    amountDueresult = cursor.fetchall()
                    duerow_headers=[x[0] for x in cursor.description] 
                    amountdueDatajson=[]
                    for dueres in amountDueresult:
                        amountdueDatajson.append(dict(zip(duerow_headers,dueres)))
                    json_data ={"banquetReservationID":banquetReservationID,"Outlet":Outlet_Name,"paymentDetails":amountdueDatajson[0],"date":date,"customerName":customername,"paxCount":pax,"timeslot":TimeSlot}
                    temphalldata.setdefault(tempHallname,[]).append(json_data)
                returndata.setdefault('both',[]).append(temphalldata)

        mydb.close()
        return jsonify(returndata),200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

