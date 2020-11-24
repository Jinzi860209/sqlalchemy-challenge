# Dependencies
import numpy as np
import pandas as pd
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import datetime as dt


###################################################
# Database Setup
###################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
        return """<html>
<p>Welcome to Hawaiian Vacation Weather API!</p>        
<p>Precipitation Analysis:</p>
<ul>
  <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
</ul>
<p>Station Analysis:</p>
<ul>
  <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
</ul>
<p>Temperature Analysis:</p>
<ul>
  <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
</ul>
<p>Start Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-11">/api/v1.0/2017-03-11</a></li>
</ul>
<p>Start & End Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-11/2017-03-18">/api/v1.0/2017-03-11/2017-03-18</a></li>
</ul>
</html>
"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)        
    # Calculate the date 1 year ago from the last data point in the Database
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a query to retrieve the last 12 months of precipitation data selecting only the `date` and `prcp` Values
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
    # Convert list of tuples into a dictionary
    prcp_data_list = dict(prcp_data)
    # Return JSON representation of dictionary
    return jsonify(prcp_data_list)    
    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    # Query all stations
    results = session.query(Station.station, Station.name).all()
    session.close()
    #Create a dictionary from the row data and append to a list of station_list
    station_list = []
    for station in results:
        station_dict = {}
        station_dict["Station"] = station.station
        station_dict["Name"] = station.name
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query for the Dates and Temperature Observations from a Year from the Last Data Point
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
                filter(Measurement.station =='USC00519281').order_by(Measurement.date).all()
    # Convert List of Tuples Into Normal List
    tobs_data_list = list(results)
    # Return JSON List of Temperature Observations (tobs) for the Previous Year
    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>")
def start(start):
        # Create our session (link) from Python to the DB
    session = Session(engine)

    start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).group_by(Measurement.date).all()
    # Convert list of tuples into normal list
    start_day_list = list(start_day)
    # Return JSON list of Min temp, Avg temp and Max temp for a given start range
    return jsonify(start_day_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
        # Create our session (link) from Python to the DB
    session = Session(engine)
    start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.date).all()
    # Convert list of tuples into normal list
    start_end_day_list = list(start_end_day)
    # Return JSON list of Min temp, Avg temp and Max temp for a given start-end range
    return jsonify(start_end_day_list)

if __name__ == '__main__':
    app.run(debug=True)