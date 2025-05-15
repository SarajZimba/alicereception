import os
from dotenv import load_dotenv
load_dotenv()
import jwt


def nameHash(cName):
    cName = jwt.encode({"cName":cName}, os.getenv('cNametoken'), algorithm="HS256")
    return cName

def emailHash(cEmail):
    cEmail= jwt.encode({"cEmail": cEmail}, os.getenv('cEmailtoken'), algorithm="HS256")
    return cEmail

def phoneHash(cPhone):
    cPhone= jwt.encode({"cPhone": cPhone}, os.getenv('cPhonetoken'), algorithm="HS256")
    return cPhone

def addressHash(cAddress):
    cAddress = jwt.encode({"cAddress":cAddress}, os.getenv('cAddresstoken'), algorithm="HS256")
    return cAddress

def ccHash(ccardno):
    ccardno= jwt.encode({"ccardno":ccardno}, os.getenv('cCardtoken'), algorithm="HS256")
    return ccardno