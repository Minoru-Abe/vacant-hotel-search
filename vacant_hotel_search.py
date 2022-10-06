import requests
import time


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

#Define input parameter files
paramdatefile = open("param_date.csv", "r")
paramhotelfile = open("param_hotel.csv", "r")
paramappidfile = open("param_appid.csv", "r")

#Skip header line in parameter files
fileheader = next(paramdatefile)
fileheader = next(paramhotelfile)
fileheader = next(paramappidfile)

#Define output files and output the header line
outputfile = open("output.csv", "w", encoding="utf_8_sig")
outputheader = CHECKINDATE + COMMA + CHECKOUTDATE + COMMA + HOTELNAME + COMMA + ROOMNAME + COMMA + CHARGE + COMMA + REVIEWCOUNT + COMMA + REVIEWAVERAGE + COMMA + HOTELMAPIMAGEURL
outputfile.write(outputheader)
outputfile.write(LINECODE)

#Read appid from appid parameter file for API variable
line = paramappidfile.readline()
appid = line.replace(LINECODE,"")

#Compile target hotels from hotelno parameter file for API variable
hotelno = ""
linecount = 1

print("Target hotels are like the followings.")

for line in paramhotelfile:
    print(line.replace(LINECODE,""))
    separatedLine = line.replace(LINECODE,"").split(COMMA)
    if linecount > 1:
        hotelno = hotelno + COMMA
    hotelno = hotelno + separatedLine[0]
    linecount+=1

#Calling API with inputed checkinDate and checkoutDate.
for line in paramdatefile:
    #sleep time to avoid "too many requests within certain period time frame"
    time.sleep(1)
    #Read checkinDate and checkoutDate from parameter file
    separatedLine = line.replace(LINECODE,"").split(COMMA)
    checkinDate = separatedLine[0]
    checkoutDate = separatedLine[1]

    params = {
        "applicationId":appid,
        "checkinDate":checkinDate,
        "checkoutDate":checkoutDate,
        "hotelNo":hotelno,
        "sort":"-roomCharge",
        "adultNum":2,
        "lowClassNum":1,
        "infantWithMBNum":1
    }

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

    res = requests.get(REQUEST_URL, params)

    #Check whether the return code is "data not found" or not. If data is not found, go to next loop.
    if res.status_code == requests.codes.not_found:
        continue

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

paramdatefile.close()
paramhotelfile.close()
paramappidfile.close()
outputfile.close()
