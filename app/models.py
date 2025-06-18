from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))

    followers = db.relationship('Follow', backref='followers', cascade='all, delete-orphan')
    following = db.relationship('Follow', backref='follow_on', cascade='all, delete-orphan')


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)

    attachments = db.relationship('Attachment', backref='tweet', cascade='all, delete-orphan')


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follow_on_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    class Meta:
        unique_together = (
            ('follower_id', 'follow_on_id'),
        )


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.BigInteger, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    class Meta:
        unique_together = (
            ('tweet_id', 'user_id'),
        )


class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    url = db.Column(db.String(255))
    src = db.Column(db.String(255))