import urllib
from flask import session, redirect, url_for, escape, request, render_template, make_response

from requestbin import app, db

def update_recent_bins(name):
    if 'recent' not in session:
        session['recent'] = []
    if name in session['recent']:
        session['recent'].remove(name)
    session['recent'].insert(0, name)
    if len(session['recent']) > 10:
        session['recent'] = session['recent'][:10]
    session.modified = True


def expand_recent_bins():
    if 'recent' not in session:
        session['recent'] = []
    recent = []
    try:
        all_keys = db.get_all_keys()
        print "db.get_all_keys() is working! :)"
        print str(all_keys)
    except Exception:
        print "stops at db.get_all_keys() in expand_recent_bins()"
    else:
        print "What??? I'm in else block???"
    
    # for name in session['recent']:
    print "looping 'all_keys'..."
    for name in all_keys:
        print "................................................................."
        try:
            gotBin = db.lookup_bin(name)
            print "[view.py] gotBin: " + str(gotBin)
            recent.append(gotBin)
            print "[view.py] recent:" + str(recent)
        except KeyError:
            print "[view.py] Oh no, it's a key error in db.lookup_bin(name)"
            session['recent'].remove(name)
            session.modified = True
    
    print "[view.py] recent will be returned as:" + str(recent);
    return recent

@app.endpoint('views.home')
def home():
    print "[view.py] visiting home"
    return render_template('home.html', recent=expand_recent_bins())


@app.endpoint('views.bin')
def bin(name):
    try:
        bin = db.lookup_bin(name)
    except KeyError:
        return "Not found\n", 404
    if request.query_string == 'inspect':
        if bin.private and session.get(bin.name) != bin.secret_key:
            return "Private bin\n", 403
        update_recent_bins(name)
        return render_template('bin.html',
            bin=bin,
            base_url=request.scheme+'://'+request.host)
    else:
        db.create_request(bin, request)
        resp = make_response("ok\n")
        resp.headers['x-csrf-token'] = 'mocktoken'
        resp.headers['Sponsored-By'] = "https://www.runscope.com"
        return resp


@app.endpoint('views.docs')
def docs(name):
    doc = db.lookup_doc(name)
    if doc:
        return render_template('doc.html',
                content=doc['content'],
                title=doc['title'],
                recent=expand_recent_bins())
    else:
        return "Not found", 404
