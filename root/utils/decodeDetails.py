import os
from dotenv import load_dotenv
load_dotenv()
import jwt


def nameDecode(cName):
    if not cName or  cName =="":
        return ""
    cName = jwt.decode(cName, os.getenv('cNametoken'), algorithms=['HS256'])
    return cName["cName"]

def emailDecode(cEmail):
    if not cEmail or  cEmail =="":
        return ""
    cEmail= jwt.decode(cEmail, os.getenv('cEmailtoken'), algorithms=['HS256'])
    return cEmail["cEmail"]

def phoneDecode(cPhone):
    if not cPhone or  cPhone =="":
        return ""
    cPhone= jwt.decode(cPhone, os.getenv('cPhonetoken'), algorithms=['HS256'])
    return cPhone["cPhone"]

def addressDecode(cAddress):
    if not cAddress or  cAddress =="":
        return ""
    cAddress = jwt.decode(cAddress, os.getenv('cAddresstoken'), algorithms=['HS256'])
    return cAddress["cAddress"]

def ccDecode(ccardno):
    if not ccardno or  ccardno =="":
        return ""
    ccardno= jwt.decode(ccardno, os.getenv('cCardtoken'), algorithms=['HS256'])
    return ccardno["ccardno"]