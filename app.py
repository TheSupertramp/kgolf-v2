from flask import Flask, render_template, jsonify
from database import get_bays, get_timeslots, get_bookings
import datetime

app = Flask(__name__)


@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today()}


def load_bookings(bookingDate, bayID):
    bookinglist = get_bookings(bookingDate=bookingDate, bayID=bayID)
    return bookinglist
app.jinja_env.globals['load_bookings']=load_bookings


@app.route("/")
def kgolf_bookingPage():
    bays = get_bays()      
    timeslots = get_timeslots()
    return render_template('home.html', 
                           bays=bays,
                           timeslots=timeslots,
                           bookings=None,
                           company_name='KGOLF')

@app.route("/api/bays")
def list_bays():
    bays = get_bays()
    return jsonify(bays)

@app.route("/api/timeslots")
def list_timeslots():
    timeslots = get_timeslots()
    return jsonify(timeslots)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)