
from flask import Flask, Blueprint,request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
app_file14 = Blueprint('app_file14',__name__)
from root.auth.check import token_auth
from root.utils.converttoJson import listtojson
from root.utils.returnJson import successmsg,errormsg


@app_file14.route("/getFinalized", methods=["GET"])
@cross_origin()
def getFinalized():
    try:
        mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
        cursor = mydb.cursor(buffered=True)
        database_sql = "USE {};".format(os.getenv('database'))
        cursor.execute(database_sql)
        getFinalizedSql =f"""SELECT a.idtblbanquetReservation as ResID,b.Name,a.NoOfPax,DATE(a.reservationDate) as reservationDate , DATE(a.reservationForDate) as ReservationFor,b.idtblcustomer as customerID FROM tblbanquetReservation a, tblcustomer b where a.customerID=b.idtblcustomer and a.reservationState='Finalized' GROUP BY a.idtblbanquetReservation ORDER BY  a.idtblbanquetReservation DESC"""
        cursor.execute(getFinalizedSql)
        mydb.commit()
        result = cursor.fetchall()
        if result == []:
            data =errormsg("No data avaliable.")
            mydb.close()
            return data,400
        json_data = listtojson(result,cursor.description)
        mydb.close()
        return json_data,200
    except Exception as error:
        data ={'error':str(error)}
        return data,400


