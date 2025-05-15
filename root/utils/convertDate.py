from datetime import datetime
from dateutil.parser import parse
from pyBSDate import convert_BS_to_AD
from pyBSDate import convert_AD_to_BS




def convertBStoAD(datestring):
    yearint = int(datestring[:4])
    monthint=int(datestring[5:7])
    dayint = int(datestring[8:10])
    reservationDate=convert_BS_to_AD(yearint, monthint, dayint)
    a='-'.join("0{}".format(str(v)) if v<10 else str(v) for v in reservationDate)
    return a



def convertADtoBS(datestring):
    yearint = int(datestring[:4])
    monthint=int(datestring[5:7])
    dayint = int(datestring[8:10])
    x=convert_AD_to_BS(yearint, monthint, dayint)
    a='-'.join("0{}".format(str(v)) if v<10 else str(v) for v in x)
    return a