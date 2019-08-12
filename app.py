# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime

# Connect to database and create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# Reflect database
Base = automap_base()
Base.prepare(engine, reflect = True)

# Extract tables as classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Open session
session = Session(engine)

# Enable Flask
app = Flask(__name__)

# Function to return min-avg and max temps for a date range
def calc_temps(start_date, end_date):
    ###########j####################
    # TMIN, TAVG, and TMAX for a list of dates.
    #
    # Args:
    #    start_date (string): date string in the format %Y-%m-%d
    #    end_date (string): A date string in the format %Y-%m-%d
    #    
    # Returns:
     #   TMIN, TAVG, and TMAX
    ##################################
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


# List routes
@app.route("/")
def main():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return JSON formatted data based on date and precipitation

    print("Running api request for precipitation")

    # Get precipitation data for the last year. Find the last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_string, "%Y-%m-%d")

    begin_date = max_date - datetime.timedelta(366)

    # Get dates and precipitation 
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()
    
    # Create dictionary
    results_dict = {}
    for result in precipitation_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():

    print("Running api request for stations")

    # Select from stations table
    stations_data = session.query(Station).all()

    # Assemble dictionaries in list
    stations_list = []
    for station in stations_data:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Running api request for tobs")

    # Get temperature data for the last year.
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_string, "%Y-%m-%d")

    # Set beginning search query
    begin_date = max_date - datetime.timedelta(366)

    # Get previous temps 
    results = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    print("Running api request for start date.")

    # Get last date
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    # Get temps
    temps = calc_temps(start, max_date)

    # Append to list
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    print("Running api request for date range.")

    temps = calc_temps(start, end)

    # Append to list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})
    return jsonify(return_list)

# Run app
if __name__ == "__main__":
    app.run(debug = True)