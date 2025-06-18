from .app import db
from .models import User, Tweet, Like

def get_user_by_key(api_key):
    user = db.session.query(User).filter_by(api_key=api_key).first()
    if user:
        return user
    else:
        last_user = db.session.query(User).order_by(User.id.desc()).first()
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

def get_likes(tweet_id):
    likes = Like.query.filter_by(tweet_id=tweet_id).all()
    return [{"user_id": like.user_id, "name": like.user.name} for like in likes]

def get_list_tweets(user):
    tweets = Tweet.query.filter_by(Tweet.author_id._in(user.following.id)).all()
    return [
        {"id": tweet.id,
         "content": tweet.content,
         "attachment": tweet.attachment,
         "author": {
             "id": tweet.author_id,
             "name": tweet.author.name
            },
         "likes": get_likes(tweet.id)
         }
        for tweet in tweets]
