import requests
import time
import line_util
import sys

REQUEST_URL = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"
COMMA = ","
LINECODE = "\n"

CHECKINDATE = "checkinDate"
CHECKOUTDATE = "checkoutDate"
HOTELNAME = "hotelName"
ROOMNAME = "roomName"
CHARGE = "charge"
REVIEWCOUNT = "reviewCount"
REVIEWAVERAGE = "reviewAverage"
HOTELMAPIMAGEURL = "hotelMapImageUrl"
INVALIDFLAG = "0"
LINE_MESSAGE_SEPARATOR = "*************************************"

#Read argument from command line
#1st argument is to send notification to line. The values are True or False
args = sys.argv
send_line_flag = args[1]
print(send_line_flag)

#Define input parameter files
paramdatefile = open("param_date.csv", "r")
paramhotelfile = open("param_hotel.csv", "r")
paramappidfile = open("param_appid.csv", "r")
paramothersfile = open("param_others.csv", "r")

#Skip header line in parameter files
fileheader = next(paramdatefile)
fileheader = next(paramhotelfile)
fileheader = next(paramappidfile)
fileheader = next(paramothersfile)

#Define output files and output the header line
outputfile = open("output.csv", "w", encoding="utf_8_sig")
outputheader = CHECKINDATE + COMMA + CHECKOUTDATE + COMMA + HOTELNAME + COMMA + ROOMNAME + COMMA + CHARGE + COMMA + REVIEWCOUNT + COMMA + REVIEWAVERAGE + COMMA + HOTELMAPIMAGEURL
outputfile.write(outputheader)
outputfile.write(LINECODE)

#Read appid from appid parameter file for API variable
line = paramappidfile.readline()
appid = line.replace(LINECODE,"")

#Initialize parameter dictionary with mandatory items
params = {
    "applicationId":appid,
    "sort":"-roomCharge",
    "adultNum":2,
    "lowClassNum":1,
    "infantWithMBNum":1
}

#Compile target hotels from hotelno parameter file for API variable to call API]
#If some hotels are specified, set them to the parameters.
hotelno = ""
linecount = 1
print("Target hotels are as following." )
for line in paramhotelfile:
    separatedLine = line.replace(LINECODE,"").split(COMMA)
    validFlag = separatedLine[0]
    #If validFlag is invalid (value=0), go to next loop
    if validFlag == INVALIDFLAG:
        continue
    print(line.replace(LINECODE,""))
    if linecount > 1:
        hotelno = hotelno + COMMA
    hotelno = hotelno + separatedLine[1]
    linecount+=1

if not hotelno:
    print("No hotel no was specified.")
else:
    params["hotelNo"] = hotelno

#Define a message to be sent to line
message_to_line = ""

#Read param_others.csv and use it to call API
for line in paramothersfile:
    separatedLine = line.replace(LINECODE,"").split(COMMA)
    validFlag = separatedLine[0]
    #If validFlag is invalid (value=0), go to next loop
    if validFlag == INVALIDFLAG:
        continue
    print(line.replace(LINECODE,""))
    paramName = separatedLine[1]
    paramValue = separatedLine[2]
    params[paramName] = paramValue

#Calling API with inputed checkinDate and checkoutDate.
for line in paramdatefile:
    #Read checkinDate and checkoutDate from parameter file and set those items to parameter dictionary to call API
    separatedLine = line.replace(LINECODE,"").split(COMMA)
    validFlag = separatedLine[0]
    checkinDate = separatedLine[1]
    checkoutDate = separatedLine[2]
    #If validFlag is invalid (value=0), go to next loop
    if validFlag == INVALIDFLAG:
        continue

    params["checkinDate"] = checkinDate
    params["checkoutDate"] = checkoutDate

    #If you want to search hotel not by hotelno but by class code, please use the following parameter sets
    #You can get class code list in the following URL
    #https://rakuten-api-documentation.antoniotajuelo.com/ja/rakuten-travel/travel-getareaclass

    #params = {
    #    "applicationId":appid,
    #    "checkinDate":checkinDate,
    #    "checkoutDate":checkoutDate,
    #    "largeClassCode":"japan",
    #    "middleClassCode":"hokkaido",
    #    "smallClassCode":"sapporo",
    #    "detailClassCode":"A",
    #    "sort":"-roomCharge",
    #    "adultNum":2,
    #    "lowClassNum":1,
    #    "infantWithMBNum":1
    #}

    #sleep time to avoid "too many requests within certain period time frame"
    time.sleep(1)

    res = requests.get(REQUEST_URL, params)

    #Check whether the return code is "data not found" or not. If data is not found, go to next loop.
    if res.status_code == requests.codes.not_found:
        continue

    res.raise_for_status()

    result = res.json()
    hotels = result["hotels"]

    for hotel in hotels:
        hotelname = hotel["hotel"][0]["hotelBasicInfo"]["hotelName"]
        reviewcount = hotel["hotel"][0]["hotelBasicInfo"]["reviewCount"]
        reviewAverage = hotel["hotel"][0]["hotelBasicInfo"]["reviewAverage"]
        hotelmapimageurl = hotel["hotel"][0]["hotelBasicInfo"]["hotelMapImageUrl"]
        for num in range(1, len(hotel["hotel"])):
            roomname = hotel["hotel"][num]["roomInfo"][0]["roomBasicInfo"]["roomName"]
            charge = hotel["hotel"][num]["roomInfo"][1]["dailyCharge"]["total"]
            resultline = checkinDate + COMMA + checkoutDate + COMMA + hotelname + COMMA + roomname + COMMA + str(charge) + COMMA + str(reviewcount) + COMMA + str(reviewAverage) + COMMA + hotelmapimageurl
            outputfile.write(resultline)
            outputfile.write(LINECODE)
            print(resultline)
            message_to_line = message_to_line + resultline
            message_to_line = message_to_line + LINECODE
            message_to_line = message_to_line + LINE_MESSAGE_SEPARATOR
            message_to_line = message_to_line + LINECODE

#Send the result message to line if send_line_flag is true
if send_line_flag == "True":
    message_sender = line_util.SendNotification
    message_sender.send_message(message_to_line)


paramdatefile.close()
paramhotelfile.close()
paramappidfile.close()
outputfile.close()
