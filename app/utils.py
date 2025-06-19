from .app import db
from .models import User, Tweet, Like, Attachment

def get_user_by_key(api_key):
    user = User.query.filter_by(api_key=api_key).first()
    if user:
        return user
    else:
        last_user = User.query.order_by(User.id.desc()).first()
        if last_user:
            user = User(
                api_key=api_key,
                name=f'User@{last_user.id + 1}',
            )
        else:
            user = User(
                api_key=api_key,
                name='User@1',
            )
        db.session.add(user)
        db.session.commit()
        return user

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_likes(tweet_id):
    likes = Like.query.filter_by(tweet_id=tweet_id).all()
    return [{"user_id": like.user_id, "name": get_user_by_id(like.user_id).name} for like in likes]

def get_attachments(tweet_id):
    attachments = Attachment.query.filter_by(tweet_id=tweet_id).all()
    return [attachment.url for attachment in attachments]

def get_list_tweets(user):
    tweets = Tweet.query.all()
    return [
        {"id": tweet.id,
         "content": tweet.content,
         "attachments": get_attachments(tweet.id),
         "author": {
             "id": tweet.author_id,
             "name": tweet.author.name
            },
         "likes": get_likes(tweet.id)
         }
        for tweet in tweets]
