from flask import Flask, render_template, render_template_string, jsonify, request
from database import get_bays, get_timeslots, get_bookings, get_availableStartTimeslots, get_availableEndTimeslots, insert_Booking, get_bookingType
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from htmlcalendar import htmlcalendar
from htmx_flask import Htmx, request

htmx = Htmx()
app = Flask(__name__)
htmx.init_app(app)

date_format = '%Y-%m-%d'
dateBooking = date.today()
app.jinja_env.globals['dateBooking']=dateBooking
app.jinja_env.globals['bayID'] = 1
timeslots = get_timeslots() 
bookingTypes = get_bookingType()


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

def css_today_class():
    todayclasses = ['today']
    return todayclasses

def load_calendar(startdate):
    # app.jinja_env.globals['dateBooking']=dateBooking
    # app.jinja_env.globals['bayID'] = 1    
    # print(app.jinja_env.globals['dateBooking'])
    # print("---")
    # print(app.jinja_env.globals['bayID'])
    class_today = css_today_class()    
    return htmlcalendar(startdate, 
                        months=1,
                        #links=links,
                        #classes=css_class,
                        classes_today=class_today,
                        currentSelectedDate=app.jinja_env.globals['dateBooking'],
                        table_id="booking-calendar",
                        show_year=True,
                        show_month=True,
                        td_custom_attribute_string='id="[[date]]" onclick="selectNewDate(this)" hx-post="/timesheet/[[date]]/" hx-target="#timesheet" hx-indicator="#timesheet-loadingbar" hx-swap="innerHTML show:bottom"')
app.jinja_env.globals['load_calendar']=load_calendar


@app.route('/timesheet/<strbookingdate>/<bayID>', methods=['POST'])
def refresh_timesheet(strbookingdate, bayID):            
    dateBooking = datetime.strptime(strbookingdate, date_format).date()
    app.jinja_env.globals['dateBooking'] = dateBooking
    app.jinja_env.globals['bayID'] = bayID
    bookinglist = get_bookings(bookingDate=dateBooking, bayID=bayID)           
    templ = """
    {% include 'timesheet.html' %}
    """
    return render_template_string(templ, 
                                  bayID=bayID,                                  
                                  bookinglist=bookinglist, 
                                  timeslots=timeslots)

@app.route('/booking/<strbookingdate>/<bayID>/<timeslotID>', methods=['POST'])
def load_new_booking_form(strbookingdate, bayID, timeslotID):
    dateBooking = datetime.strptime(strbookingdate, date_format).date()
    availableStartTimeslots = get_availableStartTimeslots(strBookingDate=strbookingdate, bayID=bayID)
    availableEndTimeslots = get_availableEndTimeslots(strBookingDate=strbookingdate, bayID=bayID, bookingStartTimeID=timeslotID)
    templ = """
    {% include 'timesheet_modal_contents.html' %}
    """
    return render_template_string(templ,                                  
                                  dateBooking=dateBooking,
                                  bayID=bayID,
                                  selectedTimeslotID=timeslotID,
                                  availableStartTimeslots=availableStartTimeslots,
                                  availableEndTimeslots=availableEndTimeslots,
                                  timeslots=timeslots)

@app.route('/get/endtimes/<strbookingdate>/<bayID>', methods=['POST']) #selected Starttime slot info can be found in the HTMX request header
def get_availableEndTimes(strbookingdate, bayID):
    templ ="""
    {% for et in endtimes %}
        <option value="{{ et['ID'] }}">{{ et['HourNameDisplay'] }}</option>
    {% endfor %}
    """
    selectedStartimeSlotID = request.form['floatingInputStartTime']
    endtimes = get_availableEndTimeslots(strbookingdate, bayID, selectedStartimeSlotID) #TODO: inside configure
    return render_template_string(templ, endtimes=endtimes)

@app.route('/get/duration', methods=['POST'])
def get_duration():        
    if request.method == 'POST'and request.form['floatingInputStartTime'] != '':
        selectedStartimeSlotID = int(request.form['floatingInputStartTime'])
        selectedEndtimeSlotID = int(request.form['floatingInputEndTime'])
        bookingDuration_in_minute = (selectedEndtimeSlotID - selectedStartimeSlotID) * 15
        bookingDuration_hourpart = int(bookingDuration_in_minute / 60)
        bookingDuration_minutepart = bookingDuration_in_minute % 60    
        templ = f"""{bookingDuration_hourpart} Hour(s) {bookingDuration_minutepart} Minute(s)"""
        return render_template_string(templ)
    else:
        return ""
    
        

@app.route('/book', methods=['POST'])
def submit_booking():
    if request.method == 'POST':
        bookingDateSubmitted = datetime.strptime(request.form['dateBooking'], date_format).date()        
        bookingBayIDSubmitted = int(request.form['bookingBayID'])
        bookingTypeID = int(request.form['bookingType'])
        bookingStartTimeSlotID = int(request.form['floatingInputStartTime'])
        bookingEndTimeSlotID = int(request.form['floatingInputEndTime'])
        bookingFirstname = request.form['floatingInputFirstname']
        bookingLastname = request.form['floatingInputLastname']
        bookingEmail = request.form['floatingInputEmail']
        bookingPhone = request.form['floatingInputMobileNumber']
        bookingPassword = request.form['floatingInputPassword']



        bool_insert_result =  insert_Booking(bookingDateSubmitted,
                                             bookingBayIDSubmitted,
                                             bookingTypeID,
                                             bookingStartTimeSlotID,
                                             bookingEndTimeSlotID,
                                             bookingFirstname,
                                             bookingLastname,
                                             bookingEmail,
                                             bookingPhone,
                                             bookingPassword)
        
        if bool_insert_result['result'] == True:
            bookingDuration_in_minute = (bookingEndTimeSlotID - bookingStartTimeSlotID) * 15
            bookingDuration_hourpart = int(bookingDuration_in_minute / 60)
            bookingDuration_minutepart = bookingDuration_in_minute % 60
            bays = get_bays() 
            bookingTypeName = next(x for x in bookingTypes if x.get("ID") == bookingTypeID).get("Name")
            

            templ ="""
                {% include 'booking_confirmation.html' %}    
            """
            return render_template_string(templ, 
                                          bookingDateSubmitted=bookingDateSubmitted, 
                                          bookingBayID=bookingBayIDSubmitted,
                                          bookingBayName=next(x for x in bays if x.get("ID") == bookingBayIDSubmitted).get("BayName"), 
                                          bookingBayDesc=next(x for x in bays if x.get("ID") == bookingBayIDSubmitted).get("BayDescription"),
                                          bookingTypeName=bookingTypeName,
                                          bookingStartTimeText=next(x for x in timeslots if x.get("ID") == bookingStartTimeSlotID).get("HourMinuteNameDisplay"),
                                          bookingEndTimeText=next(x for x in timeslots if x.get("ID") == bookingEndTimeSlotID).get("HourMinuteNameDisplay"), 
                                          bookingDuration_hourpart=bookingDuration_hourpart,
                                          bookingDuration_minutepart=bookingDuration_minutepart,
                                          bookingFullname=bookingFirstname + ' ' + bookingLastname,
                                          bookingEmail=bookingEmail, 
                                          bookingPhone=bookingPhone)
        else:
            templ = """
                {% include 'booking_failed.html' %}
            """
            return render_template_string(templ,
                                          bookingDateSubmitted=bookingDateSubmitted, 
                                          bookingBayID=bookingBayIDSubmitted)        


@app.route("/")
def kgolf_bookingPage():    

    bays = get_bays()      
    timeslots = get_timeslots()
    bookinglist = get_bookings(bookingDate=date.today(), bayID=app.jinja_env.globals['bayID'])    
    return render_template('home.html', 
                           bays=bays,
                           bayID=(app.jinja_env.globals['bayID'] if app.jinja_env.globals['bayID'] is not None else 1),
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