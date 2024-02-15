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

@app.route("/")
def hello_world():
    return render_template('home.html', 
                           jobs=JOBS,
                           company_name='KGOLF')


@app.route("/api/jobs")
def list_jobs():
    return jsonify(JOBS)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)