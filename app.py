from flask import Flask, render_template, jsonify
from database import get_bays

app = Flask(__name__)


@app.route("/")
def kgolf_booking():
    bays = get_bays()  
    return render_template('home.html', 
                           bays=bays,
                           company_name='KGOLF')


@app.route("/api/bays")
def list_jobs():
    bays = get_bays()
    return jsonify(bays)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)