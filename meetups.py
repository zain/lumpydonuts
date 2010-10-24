from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from flask import Flask, render_template, request, url_for
import httplib2, simplegeo, simplejson, urllib
import settings_local as settings

app = Flask(__name__)

# THIS IS SPARTA
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
    
    # eliminate all the meetups that don't have a public venue (so no lat/lon)
    meetups = filter(lambda m: 'venue' in m, meetups)
    
    # add topics to the group section of each meetup
    meetups = add_topics(meetups)
    
    # store in simplegeo
    geo = simplegeo.Client(settings.SIMPLEGEO_AUTH_TOKEN, settings.SIMPLEGEO_AUTH_SECRET)
    records = [meetup2record(m) for m in meetups]
    app.logger.debug("%s records to add to simplegeo." % len(records))
    
    i = 0
    while i < len(records):
        app.logger.debug("Adding #%s to #%s." % (i, i+99))
        geo.add_records(settings.SIMPLEGEO_LAYER_NAME, records[i:i+99])
        i += 99
    
    return "Done!"

def fetch_meetups(point, radius):
    url = "http://api.meetup.com/2/open_events.json?%s" % urllib.urlencode({
        'key': settings.MEETUP_API_KEY,
        'radius': radius.mi,
        'lat': point.y,
        'lon': point.x,
        'time': ',1w',
        'fields': 'trending_rank',
    })
    
    meetups, meta = meetup_api_call(url)
    
    app.logger.info("%s/%s meetups fetched." % (len(meetups), meta['total_count']))
    
    while False and 'next' in meta and meta['next']:
        new_meetups, meta = meetup_api_call(meta['next'])
        meetups += new_meetups
        
        app.logger.info("%s/%s meetups fetched (+%s)." % (len(meetups), meta['total_count'], 
            len(new_meetups)))
    
    return meetups

def add_topics(meetups):
    app.logger.debug("Fetching groups for %s meetups." % len(meetups))
    
    uniqueify = lambda l: list(set(l))
    
    url = "https://api.meetup.com/groups.json?%s" % urllib.urlencode({
        'key': settings.MEETUP_API_KEY,
        'id': ",".join(uniqueify([str(m['group']['id']) for m in meetups])),
    })
    
    groups, meta = meetup_api_call(url)
    
    # change into a table of {'id': ['topic1', 'topic2', 'topic3']}
    group_topics = dict([(g['id'], [t['name'] for t in g['topics']]) for g in groups])
    
    for meetup in meetups:
        group_id = str(meetup['group']['id'])
        meetup['group']['topics'] = group_topics[group_id]
    
    return meetups

def meetup_api_call(url):
    app.logger.debug("Making API call to: %s" % url)
    
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")
    
    if resp['status'] != '200':
        app.logger.error("API call returned: %s" % content)
        return [], {}
    
    response = simplejson.loads(unicode(content, 'latin1'), strict=False)
    
    return response['results'], response['meta']

def meetup2record(meetup):
    return simplegeo.Record(settings.SIMPLEGEO_LAYER_NAME, meetup['id'], meetup['venue']['lat'],
        meetup['venue']['lon'], event_url=meetup['event_url'], group_name=meetup['group']['name'],
        topics=":".join(meetup['group']['topics']), name=meetup['name'], time=meetup['time'],
        trending_rank=meetup['trending_rank'], yes_rsvp_count=meetup['yes_rsvp_count'],
        venue_name=meetup['venue']['name'], venue_id=meetup['venue']['id'])


if __name__ == "__main__":
    app.run(debug=True)
