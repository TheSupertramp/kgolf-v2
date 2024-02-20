from flask import Flask, render_template, jsonify

app = Flask(__name__)

JOBS = [
    {
        'id': 1,
        'title': 'Data Analyst',
        'location': 'Auckland, New Zealand',
        'Salary': '$150,000'
    },
        {
        'id': 2,
        'title': 'Data Scientist',
        'location': 'Auckland, New Zealand',
        'Salary': '$180,000'
    },
    {
        'id': 3,
        'title': 'Data Engineer',
        'location': 'Christchurch, New Zealand',
        'Salary': '$160,000'
    },
    {
        'id': 4,
        'title': 'Head of Data',
        'location': 'Wellington, New Zealand',
        'Salary': '$260,000'
    }    
]

def get_hours(start_hour=9, end_hour=23, use_half_hour=True):
    hours = []
    for i in range(start_hour, end_hour + 1):
        hours.append(f'{str(i).zfill(2)}:00')
        if use_half_hour and i < end_hour:
            hours.append(f'{str(i).zfill(2)}:30')
    return hours

def get_bays():
    return [
        {'id': 1, 'name': 'Bay 1'},
        {'id': 2, 'name': 'Bay 2'},
        {'id': 3, 'name': 'Bay 3'},
        {'id': 4, 'name': 'Bay 4'}
    ]

def get_days():
    # Implement your logic for getting days here
    pass

def get_events():
    # Implement your logic for getting events here
    pass

from datetime import datetime, timedelta

@app.template_filter('add_time')
def add_time(time, minutes):
    time_obj = datetime.strptime(time, '%H:%M')
    new_time_obj = time_obj + timedelta(minutes=minutes)
    new_time = new_time_obj.strftime('%H:%M')
    return new_time



@app.route("/")
def kgolf_booking():
    hours = get_hours()
    rooms = get_bays()
    days = get_days()
    events = get_events()    
    return render_template('home.html', 
                           jobs=JOBS,
                           rooms=rooms, days=days, events=events,
                           company_name='KGOLF')


@app.route("/api/jobs")
def list_jobs():
    return jsonify(JOBS)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)