from flask import Flask, render_template  
from flask_bootstrap import Bootstrap
  
app = Flask(__name__)
Bootstrap(app)
  
@app.route("/")
def home_view():
    return render_template('index.html')
