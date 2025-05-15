from flask import Flask, Blueprint
app = Flask(__name__)
from flask_cors import CORS,cross_origin
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'secret!'
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()


mydb = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv('password'))
cursor = mydb.cursor(buffered=True)
database_sql = "USE {};".format(os.getenv('database'))
cursor.execute(database_sql)
disableGroupErrorSQL=f"""SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"""
cursor.execute(disableGroupErrorSQL)
mydb.commit()
cursor.close()
mydb.close()

from root.flask_routes.customerRegistration.customer import app_file1
from root.flask_routes.customerRegistration.checkCustomerExists import app_file2
from root.flask_routes.banquet.reservation import app_file3
from root.flask_routes.GetdropdownList.Outlets import app_file4
from root.flask_routes.GetdropdownList.Hall import app_file5
from root.flask_routes.GetdropdownList.cName import app_file6
from root.flask_routes.Status.Started.GetStarted import app_file7
from root.flask_routes.Status.Started.paymentHistory import app_file8
from root.flask_routes.Status.Started.rateDetails import app_file9
from root.flask_routes.Status.Started.RateEdit import app_file10
from root.flask_routes.CustomerDetails.Customer import app_file11
from root.flask_routes.Status.Finalize.finalize import app_file12
from root.flask_routes.Status.Cancel.Cancel import app_file13
from root.flask_routes.Status.Finalized.getFinalized import app_file14
from root.flask_routes.Status.Finalized.getFinalizedDetails import app_file15
from root.flask_routes.Status.customerHistorybyID import app_file16
from root.flask_routes.CustomerDetails.getcustomerByName import app_file17
from root.flask_routes.Status.customerHistorybyName import app_file18
from root.flask_routes.booking.schedule import app_file19
from root.flask_routes.payment.initialbill import app_file20
from root.flask_routes.payment.makePayment import app_file21
from root.flask_routes.CustomerDetails.customerNamelist import app_file22
from root.flask_routes.booking.bookingDetails import app_file23
from root.flask_routes.creditsettlement.CreditCustomerList import app_file24
from root.flask_routes.creditsettlement.customerCreditcheck import app_file25
from root.flask_routes.creditsettlement.customerCreditdetails import app_file26
from root.flask_routes.creditsettlement.customerCreditleft import app_file27
from root.flask_routes.stats.summaryToday import app_file28
from root.flask_routes.login.login import app_file29
from root.flask_routes.customerRegistration.customerDetailsUpdate import app_file30
from root.flask_routes.customerRegistration.customerDelete import app_file31
from root.flask_routes.Status.Finalized.getFinalizedByname import app_file32
from root.flask_routes.Status.Started.editStarted import app_file33
from root.flask_routes.CustomerDetails.customerSpecialRequests import app_file34
from root.flask_routes.payment.billingParty import app_file35
from root.flask_routes.booking.schedulewithMiti import app_file36
from root.flask_routes.payment.deletebillingParty import app_file37
from root.flask_routes.payment.changeAdvancePayment import app_file38

app.register_blueprint(app_file1)
app.register_blueprint(app_file2)
app.register_blueprint(app_file3)
app.register_blueprint(app_file4)
app.register_blueprint(app_file5)
app.register_blueprint(app_file6)
app.register_blueprint(app_file7)
app.register_blueprint(app_file8)
app.register_blueprint(app_file9)
app.register_blueprint(app_file10)
app.register_blueprint(app_file11)
app.register_blueprint(app_file12)
app.register_blueprint(app_file13)
app.register_blueprint(app_file14)
app.register_blueprint(app_file15)
app.register_blueprint(app_file16)
app.register_blueprint(app_file17)
app.register_blueprint(app_file18)
app.register_blueprint(app_file19)
app.register_blueprint(app_file20)
app.register_blueprint(app_file21)
app.register_blueprint(app_file22)
app.register_blueprint(app_file23)
app.register_blueprint(app_file24)
app.register_blueprint(app_file25)
app.register_blueprint(app_file26)
app.register_blueprint(app_file27)
app.register_blueprint(app_file28)
app.register_blueprint(app_file29)
app.register_blueprint(app_file30)
app.register_blueprint(app_file31)
app.register_blueprint(app_file32)
app.register_blueprint(app_file33)
app.register_blueprint(app_file34)
app.register_blueprint(app_file35)
app.register_blueprint(app_file36)
app.register_blueprint(app_file37)
app.register_blueprint(app_file38)









@app.route("/")
@cross_origin()
def index():
    return "working"



