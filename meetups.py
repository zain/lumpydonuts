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
    meetups = fetch_meetups(SF_TOP_LEFT, SF_BOTTOM_RIGHT, SF_RADIUS)
    
    app.logger.info("Fetched %s meetups using the API." % len(meetups))
    
    # store in simplegeo

def fetch_meetups(top_left_pt, bottom_right_pt, radius):
    exes = [top_left_pt.x, bottom_right_pt.x]
    whys = [top_left_pt.y, bottom_right_pt.y]
    bbox = Polygon.from_bbox((min(exes), min(whys), max(exes), max(whys)))
    point = bbox.centroid
    
    url = "http://api.meetup.com/2/open_events.json?%s" % urllib.urlencode({
        'key': MEETUP_API_KEY,
        'radius': radius.mi,
        'lat': point.y,
        'lon': point.x,
        'time': ',1w',
        'fields': 'trending_rank',
    })
    
    app.logger.debug("Making API call to: %s" % url)
    
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    
    if resp['status'] != '200':
        import ipdb; ipdb.set_trace()
        app.logger.error("API call returned: %s" % content)
        return []
    import ipdb; ipdb.set_trace()
    
    meetups = simplejson.loads(content.decode("utf-8", "replace"), strict=False)['results']
    
    app.logger.info("Fetched %s meetups using the API." % len(meetups))
    
    if len(meetups) < 199:
        return meetups
    else:
        # recurse this mutha
        meetups = []
        
        quadrants = quarter(top_left_pt, bottom_right_pt)
        for q_top_left_pt, q_bottom_right_pt in quadrants:
            meetups += fetch_meetups(q_top_left_pt, q_bottom_right_pt, radius / 2)
        
        return meetups

def quarter(top_left, bottom_right):
    """
    Takes two points that define a bounding box, quarters the bounding box, and
    returns eight points that define the four quandrants
    """
    halfway_between = lambda p, q: Point((p.x+q.x)/2, (p.y+q.y)/2)
    
    top_right = Point(bottom_right.x, top_left.y)
    bottom_left = Point(top_left.x, bottom_right.y)
    
    top_middle = halfway_between(top_left, top_right)
    middle_right = halfway_between(top_right, bottom_right)
    left_middle = halfway_between(top_left, bottom_left)
    bottom_middle = halfway_between(bottom_left, bottom_right)
    middle_middle = halfway_between(top_middle, bottom_middle)
    
    return [
        (top_middle, middle_right), # quadrant 1
        (top_left, middle_middle), # quadrant 2
        (left_middle, bottom_middle), # quadrant 3
        (middle_middle, bottom_right), # quadrant 4
    ]


if __name__ == "__main__":
    app.run(debug=True)
