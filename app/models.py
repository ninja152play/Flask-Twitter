from .app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))

    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.follow_on_id',
        backref='followed_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    tweets = db.relationship('Tweet', backref='author', lazy='dynamic', cascade='all, delete-orphan')


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)

    attachments = db.relationship('Attachment', backref='tweet', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='tweet', cascade='all, delete-orphan')


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follow_on_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'follow_on_id', name='follow_uc'),
    )


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.BigInteger, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.UniqueConstraint('tweet_id', 'user_id', name='like_uc'),
    )


class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    url = db.Column(db.String(255))
    src = db.Column(db.String(255))