import os
import tempfile
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from app.app import create_app, db as _db
from app.models import *

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with _app.app_context():
        _db.create_all()

    yield _app

    with _app.app_context():
        _db.drop_all()

@pytest.fixture
def db(app):
    """Give access to database instance."""
    with app.app_context():
        yield _db.session
        _db.session.remove()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Return headers with API key for authenticated requests."""
    return {'Api-Key': 'test-api-key'}

@pytest.fixture
def user_factory(db):
    counter = 0
    def factory(name=None, api_key=None):
        nonlocal counter
        counter += 1
        if name is None:
            name = f'user{counter}'
        if api_key is None:
            api_key = f'api-key-{counter}'
        user = User(name=name, api_key=api_key)
        db.add(user)
        db.commit()
        return user
    return factory

@pytest.fixture
def user(user_factory):
    return user_factory()

@pytest.fixture
def second_user(user_factory):
    return user_factory(name='second', api_key='second-api-key')

@pytest.fixture
def tweet_factory(db):
    def factory(author=None):
        if author is None:
            author = User(name='test', api_key='test-api-key')
            db.add(author)
        tweet = Tweet(author=author, content='test tweet')
        db.add(tweet)
        db.commit()
        return tweet
    return factory

@pytest.fixture
def tweet(tweet_factory):
    return tweet_factory()

@pytest.fixture
def follow_factory(db, user_factory):
    def factory(follower=None, followed=None):
        if follower is None:
            follower = user_factory()
        if followed is None:
            followed = user_factory(name='followed', api_key='followed-api-key')
        follow = Follow(follower_id=follower.id, followee_id=followed.id)
        db.add(follow)
        db.commit()
        return follow
    return factory

@pytest.fixture
def like_factory(db, user_factory, tweet_factory):
    def factory(tweet=None, user=None):
        if tweet is None:
            tweet = tweet_factory()
        if user is None:
            user = user_factory()
        like = Like(tweet=tweet.id, user=user.id)
        db.add(like)
        db.commit()
        return like
    return factory

@pytest.fixture
def attachment_factory(db, tweet_factory):
    def factory(tweet=None):
        if tweet is None:
            tweet = tweet_factory()
        attachment = Attachment(tweet_id=tweet.id, url='uploads/test.png', src='test.png')
        db.add(attachment)
        db.commit()
        return attachment
    return factory


@pytest.fixture
def test_file():
    """Create a test file"""
    import io
    file = FileStorage(
        stream=open('tests/test.png', 'rb'),
        filename='test.png',
        content_type='image/png'
    )
    return file