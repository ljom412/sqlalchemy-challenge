from flask import Flask, jsonify
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from datetime import timedelta, datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = Session(engine)

Base = automap_base()
Base.prepare(engine)

measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)

# Define the homepage route
@app.route('/')
def homepage():
    return f''' 
     <h1>Welcome to Honolulu, Hawaii's Climate App</h1>

     <h3>Available routes:</h3>

     <ul>
         <li><a href="/api/v1.0/precipitation">Precipitation</a></li>
         <li><a href="/api/v1.0/stations">Stations</a></li>
         <li><a href="/api/v1.0/tobs">Tobs</a></li>
         <li><a href="/api/v1.0/2016-01-01">Specified Start Date</a></li>
         <li><a href="/api/v1.0/2016-08-23/2017-08-23">Specified Start/End Date Range</a></li>

    </ul>
 '''

# Define the /api/v1.0/precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').all()
    
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the /api/v1.0/stations route
@app.route('/api/v1.0/stations')
def stations():
    selection = [measurement.station, func.count(measurement.station)]
    most_active_stations = session.query(*selection).group_by(selection[0]).order_by(selection[1].desc()).all()

    station_data = {id:loc for id, loc in most_active_stations}

    return jsonify(station_data)

# Define the /api/v1.0/tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    selection = [measurement.station, func.count(measurement.station)]
    most_active_stations = session.query(*selection).group_by(selection[0]).order_by(selection[1].desc()).all()

    results = session.query(measurement.date, measurement.tobs).filter((measurement.date>='2016-08-23') & 
                                                 (measurement.station==most_active_stations[0][0])).all()
    
    tobs_data = []
    for result in results:
        date, tobs = result
        tobs_data.append({'date': date, 'temperature': tobs})
    
    return(tobs_data)

# Define the /api/v1.0/<start> route
@app.route('/api/v1.0/<start>')
def temperature_stats_start(start):
    # Convert the start date to a datetime object
    start_date = datetime.strptime(start, '%Y-%m-%d')

    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)) \
                     .filter(measurement.date >= start_date) \
                     .all()

    # Convert the query results into a JSON list
    temperature_stats = []
    for result in results:
        tmin, tavg, tmax = result
        temperature_stats.append({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})

    return jsonify(temperature_stats)


# Define the /api/v1.0/<start>/<end> route
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats_range(start, end):
    # Convert the start and end dates to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    # Query the minimum, average, and maximum temperatures for the specified date range
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)) \
                     .filter(measurement.date >= start_date) \
                     .filter(measurement.date <= end_date) \
                     .all()

    # Convert the query results into a JSON list
    temperature_stats = []
    for result in results:
        tmin, tavg, tmax = result
        temperature_stats.append({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})

    return jsonify(temperature_stats)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
