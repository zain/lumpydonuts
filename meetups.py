from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from flask import Flask, render_template, request, url_for
import httplib2, simplegeo, simplejson, urllib

app = Flask(__name__)


# meetup settings
MEETUP_API_KEY = '786e7745f52527d5f5b14783949'

# simplegeo settings
SIMPLEGEO_AUTH_TOKEN = ''
SIMPLEGEO_AUTH_SECRET = ''

geo = simplegeo.Client(SIMPLEGEO_AUTH_TOKEN, SIMPLEGEO_AUTH_SECRET)

# THIS IS SPARTA
SF_TOP_LEFT = Point(-122.5300, 37.8049)
SF_BOTTOM_RIGHT = Point(-122.3815, 37.7224)
SF_CENTROID = Point(-122.45575, 37.76365)
SF_RADIUS = D(mi=5)

@app.route("/")
def index():
    return render_template("index.html", msg=request.form.get("msg", ""))

@app.route("/update/")
def update():
    # make the meetup call
    meetups = fetch_meetups(SF_CENTROID, SF_RADIUS)
    
    app.logger.info("Fetched a total of %s meetups using the API." % len(meetups))
    
    # store in simplegeo

def fetch_meetups(point, radius):
    url = "http://api.meetup.com/2/open_events.json?%s" % urllib.urlencode({
        'key': MEETUP_API_KEY,
        'radius': radius.mi,
        'lat': point.y,
        'lon': point.x,
        'time': ',1w',
        'fields': 'trending_rank',
    })
    
    meetups, meta = meetup_api_call(url)
    
    total_count = meta['total_count']
    
    app.logger.info("%s/%s meetups fetched." % (len(meetups), total_count))
    
    while 'next' in meta and meta['next']:
        new_meetups, meta = meetup_api_call(meta['next'])
        meetups += new_meetups
        
        app.logger.info("%s/%s meetups fetched (+%s)." % (len(meetups), total_count, 
            len(new_meetups)))
    
    return meetups

def meetup_api_call(url):
    app.logger.debug("Making API call to: %s" % url)
    
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    
    if resp['status'] != '200':
        app.logger.error("API call returned: %s" % content)
        return []
    
    try:
        response = simplejson.loads(unicode(content, 'latin1'), strict=False)
    except simplejson.JSONDecodeError, e:
        app.logger.error("JSONDecodeError: %s" % e)
        import ipdb; ipdb.set_trace()
    
    meetups = response['results']
    meta = response['meta']
    
    return meetups, meta


if __name__ == "__main__":
    app.run(debug=True)
