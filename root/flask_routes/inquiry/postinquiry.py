from flask import Blueprint, request
from flask_cors import cross_origin
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
from root.utils.returnJson import successmsg, errormsg
from root.auth.check import token_auth
from datetime import datetime

app_file39 = Blueprint('app_file39', __name__)

@app_file39.route("/submitInquiry", methods=["POST"])
@cross_origin()
def submit_inquiry():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(buffered=True)
        cursor.execute(f"USE {os.getenv('database')}")

        json = request.get_json()

        # Validate token
        if "token" not in json or not json["token"]:
            mydb.close()
            return errormsg("No token provided."), 400
        if not token_auth(json["token"]):
            mydb.close()
            return errormsg("Invalid token."), 400

        # Validate required fields
        if "customer_name" not in json or "contact_no" not in json:
            mydb.close()
            return errormsg("Required fields missing: customer_name or contact_no"), 400

        # Optional fields
        customer_name = json["customer_name"]
        contact_no = json["contact_no"]
        reservation_date = json.get("reservation_date")  # Should be in YYYY-MM-DD
        about = json.get("about")

        insert_sql = """
            INSERT INTO customer_inquiry (customer_name, contact_no, reservation_date, about)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (customer_name, contact_no, reservation_date, about))
        mydb.commit()
        mydb.close()
        return successmsg("Customer inquiry submitted successfully."), 200

    except Exception as e:
        return {"error": str(e)}, 400


@app_file39.route("/getInquiries", methods=["GET"])
@cross_origin()
def get_inquiries():
    try:
        token = request.args.get("token")
        if not token:
            return errormsg("No token provided."), 400
        if not token_auth(token):
            return errormsg("Invalid token."), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(f"USE {os.getenv('database')}")

        cursor.execute("SELECT * FROM customer_inquiry ORDER BY id DESC")
        rows = cursor.fetchall()
        mydb.close()

        return {
            "message": "Inquiries fetched successfully.",
            "data": rows
        }, 200

    except Exception as e:
        return errormsg(f"Error fetching inquiries: {str(e)}"), 400

@app_file39.route("/deleteInquiry", methods=["DELETE"])
@cross_origin()
def delete_inquiry():
    try:
        json = request.get_json()
        token = json.get("token")
        inquiry_id = json.get("id")

        if not token:
            return errormsg("No token provided."), 400
        if not token_auth(token):
            return errormsg("Invalid token."), 400
        if not inquiry_id:
            return errormsg("Inquiry ID is required."), 400

        mydb = mysql.connector.connect(
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        cursor = mydb.cursor()
        cursor.execute(f"USE {os.getenv('database')}")

        # Check if inquiry exists
        cursor.execute("SELECT * FROM customer_inquiry WHERE id = %s", (inquiry_id,))
        if not cursor.fetchone():
            mydb.close()
            return errormsg("Inquiry not found."), 404

        # Delete the inquiry
        cursor.execute("DELETE FROM customer_inquiry WHERE id = %s", (inquiry_id,))
        mydb.commit()
        mydb.close()

        return successmsg("Inquiry deleted successfully."), 200

    except Exception as e:
        return errormsg(f"Error deleting inquiry: {str(e)}"), 400

