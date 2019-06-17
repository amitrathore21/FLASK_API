import pymongo
from flask import Flask
from pymongo import MongoClient
from datetime import datetime, timedelta
from pymongo.collection import Collection

app = Flask(__name__)
try:
    client = MongoClient()
    print("DB connected Successfully")
except:
    print("Could not connect to Database")

connection = pymongo.MongoClient("localhost")
database = connection['my_database']
collection:Collection = database['flight_management']
collection2:Collection = database['booking_management']

#QUERY ONE
print("1. Flights whose model is 737\n")
model = "737"
flight = collection.find_one({"model":model})
if flight:
    print(flight)
else:
    print("No such flight with model " + model + " found.")


#QUERY 2
capacity = 40
print("\n\n\n2.Flights whose capacity is "+ str(capacity) +" and above\n")
flight = collection.find()
for i in flight:
    if int(i['capacity'])>=40:
        print(i['name'])
    else:
        print("no flights whoes capacity is "+str(capacity)+" and above.")


# QUERY 3
print("\n\n\n3.All flights whose service done 5 or more months back.\n")

months = 5
date_gap = datetime.today() - timedelta(days=30*months)
flight_details = collection.find({"service.date_of_service":{"$lte":date_gap}})
if flight_details:
    for i in flight_details:
        print(i['name'])
else:
    print("no flight serviced 5 or more months back")



#QUERY 4
print("\n\n\n4. Which flight was services more.\n")
all_flights = collection.find()
flight_id = []
ser_len = []
max = {}
for i in all_flights:
    flight_id.append(i['_id'])
    ser_len.append(len(i['service']))
max = dict(zip(flight_id,ser_len))

temp = sorted(max)
id = temp[-1]
print(id)


#QUERY 5
print("\n\n\n5. to find  lousy service?\n")
all_flights = collection.find()
data = []
for flight in all_flights:
    data.append(flight)

min = datetime.now() - datetime.strptime("01-01-1970", "%d-%m-%Y")
lousy_team = ""
flight_no = ""

for flight in data:
    service = flight["service"]
    for i in range(len(service)-1):

        time_diff = abs(service[i+1]["date_of_service"] - service[i]["date_of_service"])
        if time_diff < min:
            min = time_diff
            lousy_team = service[i]["service_by"]
            flight_no = flight["_id"] + " - " + flight["name"]
print("Most lousy service team is \"" + lousy_team )
