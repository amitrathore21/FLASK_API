import pymongo

from flask import Flask,request,jsonify
from pymongo.collection import Collection
from bson import ObjectId
#import bson.json_util import loads
from random import *

from datetime import datetime

app = Flask(__name__)
connection = pymongo.MongoClient("localhost")
database = connection['my_database']
collection:Collection = database['flight_management']
collection2:Collection = database['booking_management']


@app.route("/")
def index():
    return "this is the flight management API"


@app.route("/flights/")
def flights():
    flights_name = []
    for flight in collection.find():
        flights_name.append(flight)
    print(flights_name)
    return jsonify(flights_name)
    #return (flights_name)



@app.route("/flights/", methods=["POST"])
def insert_flights():
    id = request.args["id"]
    name = request.args["name"]
    model = request.args["model"]
    airline = request.args["airline"]
    capacity = request.args["capacity"]
    manufacturing_date = request.args["manufacturing_date"]
    service = []


    new_flights = collection.insert_one({"_id":id,
                                         "name":name,
                                         "model":model,
                                         "airline":airline,
                                         "capacity":capacity,
                                         "manufacturing_date":manufacturing_date,
                                         "seat_booked":0
                                         })

    return str(new_flights)

@app.route("/flight/<_id>")
def flight_details(_id):
    data = []
    data = collection.find_one(_id)
    if data:
        print(data)
        return jsonify(data)

    else:
        return "no such flight exiest"


@app.route("/flight/<_id>",methods=["HEAD"])
def seartch_flight(_id):
    data = []
    data = collection.find_one(_id)
    if data:
        print(data)
        return "flight available"

    else:
        return "no such flight exiest"



@app.route('/flight/<_id>',methods=["PATCH"])
def update_details(_id):
    data = {}
    for entries in request.args:
        data[entries]= request.args[entries]
    updated =collection.find_one_and_update({"_id":_id},{"$set":data})
    return ("done")

@app.route('/flight/<_id>',methods=["DELETE"])
def delete_flight(_id):
    data = collection.delete_one({'_id': _id})
    return "flight successfully deleted"



###################################################
##Booking Managment


@app.route("/flight/<flight_no>/availability/",methods = ["POST"])
def availability(flight_no):
    data = []
    data = collection.find_one(flight_no)
    avail = int(data['capacity'])-int(data['seat_booked'])
    return "available : "+str(avail)


@app.route("/flight/<flight_number>/book",methods=["POST"])
def seat_booking(flight_number):
    data = []
    data = collection.find_one(flight_number)

    _id = randint(1,1000)
    customer_name = request.args["customer_name"]
    email = request.args["email"]
    contect_number = request.args["contect_number"]
    seat = request.args["seat"]
    flight_id =flight_number
    total_booked_seat = int(data['seat_booked'])+int(seat)
    print(seat)
    print(total_booked_seat)
    customer_details = collection2.insert_one({"_id":_id,
                                               "customer_name":customer_name,
                                               "email":email,
                                               "contect_number":contect_number,
                                               "seat":seat,
                                               "flight_id":flight_number})
    collection.update_one({"_id":flight_number},{"$set":{
        'seat_booked':total_booked_seat
    }})
    return str(customer_details)



@app.route("/seat cancelletion/<ticket_number>/",methods = ['DELETE'])
def delete(ticket_number):
    seat = request.args["seat"]
    booked_seat = collection2.find_one({'_id':ticket_number})
    flight_number = booked_seat['flight_id']
    booked_seat_f1 = collection.find_one({'_id':flight_number})
    flight_number1 = booked_seat_f1['_id']
    if int(seat)<int(booked_seat['seat']):
        updated_seat = int(booked_seat['seat'])-int(seat)
        new_seat = int(booked_seat_f1['seat_booked'])-int(seat)
        collection2.update_one({'_id':ticket_number},{"$set":{
            "seat":updated_seat}})
        collection.update_one({'_id':flight_number1},{"$set":{
            "seat_booked":new_seat
        }})
        return("Succesfully deleted"+seat)
    elif int(seat)==int(booked_seat['seat']):
        collection2.delete_one({"_id":ticket_number})
        new_seat = int(booked_seat_f1['seat_booked'])-int(seat)
        collection.update_one({'_id':flight_number1},{"$set":{
            "seat_booked":new_seat}})
        return ("all seats deleted")
    else:
        return("wrong entry")



@app.route("/flight/<flight_no>/book/<booking_id>")
def booking_details(flight_no,booking_id):
    data = []
    data = collection2.find_one(booking_id)
    return jsonify(data)





@app.route("/service/<flight_no>", methods=["POST"])
def service(flight_no):
    if all(argument in request.args for argument in ["date_of_service","service_by"]):
        service_by = request.args["service_by"]

        date_of_service = datetime.strptime(request.args["date_of_service"], "%d-%m-%Y")


        flight = collection.find_one_and_update({"_id":flight_no},{
            "$addToSet":{
                "service": {"date_of_service": date_of_service,
                            "service_by": service_by}
            }
        })
        if flight:
            return "Success in adding service record"
        else:
            return "No flight found in with this flight_id"


    else:
        return "provide date_of_service and service_by"

