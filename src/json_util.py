import json

def loadToJSON(data: str):
    try:
        return json.loads(data)
    except Exception as _:
        return "Empty"
    
def loadToString(data):
    try:
        return json.dumps(data)
    except Exception as _:
        return ""

def modifyJSON(data: str, key: str, value, dumpToString: bool = False):
    jsonData = loadToJSON(data)
    if jsonData == "Empty":
        return

    jsonData[key] = value
    return loadToString(jsonData) if dumpToString else jsonData

def getValueFromJSON(data: str, key: str):
    jsonData = loadToJSON(data)
    if jsonData == "Empty":
        return ""
    
    return jsonData[key]