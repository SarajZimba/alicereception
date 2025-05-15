

def listtojson(result,description):
    row_headers=[x[0] for x in description] 
    json_data=[]
    for res in result:
        json_data.append(dict(zip(row_headers,res)))
    return json_data
    