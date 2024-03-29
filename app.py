#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
from flask_cors import CORS
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import wikipedia as wiki
import os
from scrapes.coursera import courserascrape 
from scrapes.edx import edxscrape
from scrapes.youtube import youtube_search_keyword
from scrapes.libgen import libgenscrape
from scrapes.udemy import udemyscrape
from scrapes.dev import devscrape
from scrapes.github import scrapegithub
import requests
import json
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
CORS(app)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/<course>', methods=['POST', 'GET'])
def my_courses_search(course):
    # text = request.form['text']
    github=scrapegithub(course)
    # resp = requests.get('https://dev.to/api/articles/')
    # print(resp.json())
    coursera = courserascrape(course)
    youtube= youtube_search_keyword(course,7)
    
    
    # edx = edxscrape(text)
    libgen = libgenscrape(course)
    dev= devscrape(course)
    # print(dev)
    # udemy = udemyscrape(text)
    # youtube= youtubescrape(text)
    # print(youtubescrape(text))
    try:
        wiki_summary = wiki.summary(course)
    except:
        wiki_summary = False
    
    if wiki_summary:
        wiki_summary = wiki_summary.split('\n')[:2]
        wiki_summary[0] = "n:/" + course + ": "+ wiki_summary[0]
        print(wiki_summary)
    processed_text = { "WIKIPEDIA":wiki_summary,"COURSERA":coursera, "LIBGEN": libgen, "EDX": [], "UDEMY": [], "YOUTUBE":youtube, "DEV":dev, "GITHUB":github}
    return json.dumps(processed_text)
    return render_template('pages/results.html', summary = wiki_summary, websites = processed_text)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='127.0.0.1', port=port)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
