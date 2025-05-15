import re


def phonecheck(number):
    phoneregex = re.match(r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$",number)
    if phoneregex:
        return True
    if not phoneregex:
        return False