
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file16 = Blueprint('app_file16',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file16.route("/CustomerHistory", methods=["POST"])
@cross_origin()
def CustomerHistory():
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
        if "customerID" not in json or json["customerID"]=="" or "state" not in json or "reservationDate" not in json or "reservationForDate" not in json:
            data = errormsg("Some fields are missing.")
            mydb.close()
            return data,400
        
        if json["state"]  !="" and json["reservationDate"]=="" and json["reservationForDate"]=="":
            customerID=json["customerID"]
            state=json["state"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationState=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,state,),)
            result = cursor.fetchall()
            
            
        if json["state"]  !=""  and json["reservationDate"] !="" and json["reservationForDate"] =="":
            customerID=json["customerID"]
            state=json["state"]
            reservationDate=json["reservationDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationState=%s and a.reservationDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,state,reservationDate,),)
            result = cursor.fetchall()   
            
        
        if json["state"]  !="" and json["reservationForDate"] !="" and json["reservationDate"] =="":
            customerID=json["customerID"]
            state=json["state"]
            reservationForDate=json["reservationForDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationState=%s and a.reservationForDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,state,reservationForDate,),)
            result = cursor.fetchall()  
            
        if "reservationDate" in json and json["reservationDate"] !="" and json["reservationForDate"] !="" and json["state"] =="":
            customerID=json["customerID"]
            reservationDate=json["reservationDate"]
            reservationForDate=json["reservationForDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationForDate=%s and a.reservationDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,reservationForDate,reservationDate,),)
            result = cursor.fetchall()   
            
        if json["reservationDate"] !="" and json["state"] =="" and json["reservationForDate"] =="":
            customerID=json["customerID"]
            reservationDate=json["reservationDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,reservationDate,),)
            result = cursor.fetchall()    
            
        if json["reservationForDate"] !="" and json["state"] =="" and json["reservationDate"] =="":
            customerID=json["customerID"]
            reservationForDate=json["reservationForDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s and a.reservationForDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,reservationForDate,),)
            result = cursor.fetchall()     
        
        if json["reservationForDate"] !="" and json["state"] !=""  and json["reservationDate"] !="":
            customerID=json["customerID"]
            state=json["state"]
            reservationDate=json["reservationDate"]
            reservationForDate=json["reservationForDate"]
            get_started_sql =f"""SELECT a.idtblbanquetReservation as banquetReservationID, a.reservationState, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and  a.customerID=%s and a.reservationState=%s and a.reservationDate=%s and a.reservationForDate=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,state,reservationDate,reservationForDate,),)
            result = cursor.fetchall()    
        
        if json["state"] =="" and json["reservationForDate"] =="" and json["reservationDate"] =="":
            customerID=json["customerID"]
            get_started_sql =f"""SELECT a.reservationState,a.idtblbanquetReservation as banquetReservationID, b.Name,a.customerID,a.Outlet_Name,a.advancePayment,a.NoOfPax,DATE(a.reservationDate) AS reservationDate, DATE(a.reservationForDate) AS reservationForDate from tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.customerID=%s GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
            cursor.execute(get_started_sql,(customerID,),)
            result = cursor.fetchall()
        
        if result == []:
            data = errormsg("No results found.")
            mydb.close()
            return data,400
        row_headers=[x[0] for x in cursor.description] 
        billItemdata ={}
        for res in result:
            idtblbanquetReservation = dict(zip(row_headers,res))["banquetReservationID"]
            Name = dict(zip(row_headers,res))["Name"]
            customerID = dict(zip(row_headers,res))["customerID"]
            Name = dict(zip(row_headers,res))["Name"]
            Outlet_Name = dict(zip(row_headers,res))["Outlet_Name"]
            advancePayment = dict(zip(row_headers,res))["advancePayment"]
            NoOfPax = dict(zip(row_headers,res))["NoOfPax"]
            reservationDate = dict(zip(row_headers,res))["reservationDate"]
            reservationForDate = dict(zip(row_headers,res))["reservationForDate"]
            reservationState=dict(zip(row_headers,res))["reservationState"]
            getRateSql=f"""SELECT GROUP_CONCAT(HallName SEPARATOR ' / ' ) as HallName, RateName from tblbanquetRate_details  WHERE banquetReservationID=%s"""
            cursor.execute(getRateSql,(idtblbanquetReservation,),)
            rateresult = cursor.fetchall()
            if rateresult == []:
                hall_names = ""
                Startedjsondata={"reservationState":reservationState,"banquetReservationID":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
            else:
                hall_names = listtojson(rateresult,cursor.description)
                hall_names = hall_names[0]["HallName"]
                Startedjsondata={"reservationState":reservationState,"banquetReservationID":idtblbanquetReservation,"customerID":customerID,"Name":Name,"Outlet_Name":Outlet_Name,"advancedPayment":advancePayment,"NoOfPax":NoOfPax,"reservationDate":reservationDate,"reservationForDate":reservationForDate,"hall_names":hall_names}
                billItemdata.setdefault("Details",[]).append(Startedjsondata)
        mydb.close()
        return billItemdata["Details"],200
    except Exception as error:
        data ={'error':str(error)}
        return data,400

