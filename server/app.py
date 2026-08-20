#!/usr/bin/env python3

from flask import Flask, make_response, session
from flask_migrate import Migrate

from models import db, Article, ArticleSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/clear')
def clear_session():
    """
    Clears the session data for page views.
    Useful for resetting the paywall limit during testing or development.
    """
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200


@app.route('/articles')
def index_articles():
    """
    Returns a JSON list of all available articles.
    """
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)


@app.route('/articles/<int:id>')
def show_article(id):
    """
    Returns a specific article by ID, enforcing a 3-article page view limit.
    
    Logic:
    1. Initializes session['page_views'] to 0 if it doesn't exist.
    2. Increments session['page_views'] by 1 on every request.
    3. Returns the article data if page_views <= 3.
    4. Returns a 401 Unauthorized error with a message if page_views > 3.
    """
    # Step 1: Initialize the Session for Page Views
    if 'page_views' not in session:
        session['page_views'] = 0
        
    # Step 2: Increment the Session on Each Request
    session['page_views'] += 1
    
    # Step 3: Send Response Based on Session Data
    if session['page_views'] <= 3:
        article = db.session.get(Article, id)
        if article:
            return make_response(ArticleSchema().dump(article))
        else:
            return make_response({'message': 'Article not found'}, 404)
    else:
        return make_response({'message': 'Maximum pageview limit reached'}, 401)


if __name__ == '__main__':
    app.run(port=5555)