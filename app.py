from flask import Flask, render_template, render_template_string, jsonify
from database import get_bays, get_timeslots, get_bookings
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from htmlcalendar import htmlcalendar

app = Flask(__name__)


@app.context_processor
def inject_today_date():
    today_date = date.today()    
    return dict(today_date=today_date,
                this_month_date=today_date,
                next1_month_date=today_date + relativedelta(months=1),
                next2_month_date=today_date + relativedelta(months=2)
                )


def load_bookings(bookingDate, bayID):
    bookinglist = get_bookings(bookingDate=bookingDate, bayID=bayID)
    return bookinglist
app.jinja_env.globals['load_bookings']=load_bookings


@app.route('/timesheet/<strbookingdate>/<bayID>', methods=['POST'])
def refresh_timesheet(strbookingdate, bayID):    
    date_format = '%Y-%m-%d'
    dateBooked = datetime.strptime(strbookingdate, date_format)
    bookinglist = get_bookings(bookingDate=dateBooked, bayID=bayID)    
    timeslots = get_timeslots()    
    templ = """
    {% include 'timesheet.html' %}
    """
    return render_template_string(templ, 
                                  bayID=bayID,
                                  dateShowing=strbookingdate,
                                  bookinglist=bookinglist, 
                                  timeslots=timeslots)


# def links(date):
#         if date.weekday() == 5:
#                 return "https://github.com/"

# def css_class(date):
#     return ["cursor-pointer"]     
#         # if date.weekday() == 5:
#         #         return ["pe-auto"]        

def css_today_class():
    todayclasses = ['today','selected']
    return todayclasses

def load_calendar(startdate):
    class_today = css_today_class()    
    return htmlcalendar(startdate, 
                        months=1,
                        #links=links,
                        #classes=css_class,
                        classes_today=class_today,
                        table_id="booking-calendar",
                        show_year=True,
                        show_month=True,
                        td_custom_attribute_string='id="[[date]]" onclick="selectNewDate(this)" hx-post="/timesheet/[[date]]/" hx-target="#timesheet" hx-indicator="#timesheet-loadingbar" hx-swap="innerHTML show:bottom"')
app.jinja_env.globals['load_calendar']=load_calendar


@app.route("/")
def kgolf_bookingPage():    
    bays = get_bays()      
    timeslots = get_timeslots()
    bookinglist = get_bookings(bookingDate=date.today(), bayID=1)    
    return render_template('home.html', 
                           bays=bays,
                           timeslots=timeslots,
                           bookinglist=bookinglist,
                           company_name='KGOLF')


# APIs

@app.route("/api/bays")
def list_bays():
    bays = get_bays()
    return jsonify(bays)

@app.route("/api/timeslots")
def list_timeslots():
    timeslots = get_timeslots()
    return jsonify(timeslots)


# Main

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)