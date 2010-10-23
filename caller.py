from flask import Flask, render_template, request, url_for
import twilio

app = Flask(__name__)

# twilio
ACCOUNT_SID = 'ACc6fcef783eb89ce138e57a84176799ee'
ACCOUNT_TOKEN = 'c4d79f891e25c8f5b08c8ab9cacab1ee'
API_VERSION = '2010-04-01'
CALLER_ID = '4083911392'
tw = twilio.Account(ACCOUNT_SID, ACCOUNT_TOKEN)

@app.before_request
def before_request():
    request.base_url = "http://4nvr.localtunnel.com"

@app.route("/")
def index():
    app.logger.debug(request.values)
    return render_template("index.html", msg=request.form.get("msg", ""))

@app.route("/call/", methods=["POST"])
def call():
    app.logger.debug(request.values)
    number = request.form['number']
    
    # have twilio make the phonecall
    call = {
        'From': CALLER_ID,
        'To': "+1%s" % number,
        'Url': "%s%s" % (request.base_url, url_for("call_return")),
    }
    
    app.logger.debug("Call params: %s" % call)
    
    try:
        response = tw.request('%s/Accounts/%s/Calls' % (API_VERSION, ACCOUNT_SID), 'POST', call)
    except Exception, e:
        app.logger.error("%s: %s" % e, e.read())
    
    return render_template("calling.html", number=number)

@app.route("/call/return/", methods=["GET", "POST"])
def call_return():
    app.logger.debug(request.values)
    return render_template("call_message.xml", 
        transcribe_callback="%s%s" % (request.base_url, url_for("transcribe_callback")))

@app.route("/call/transcription/", methods=["GET", "POST"])
def transcribe_callback():
    app.logger.debug(request.values)
    
    caller = request.form["Caller"]
    
    if request.form.get("TranscriptionStatus") != "completed":
        app.logger.error("Error transcribing from %s" % caller)
    
    recording_url = request.form["RecordingUrl"]
    text = request.form["TranscriptionText"]
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
