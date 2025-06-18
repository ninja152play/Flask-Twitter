import os
from flask import Flask, g, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_restx import Api, Resource, fields, Namespace, reqparse

db = SQLAlchemy()
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def create_app():
    app = Flask(__name__,
                static_folder='../dist',
                template_folder='../dist')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/twitter_db'
    #To prod postgresql://admin:admin@db:5432/twitter_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    api = Api(
        app,
        version='1.0',
        title='Twitter API',
        description='A simple Twitter API',
        doc='/docs/',
        security='Api-Key',
        authorizations={
            'Api-Key': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Api-Key',
                'description': 'Api-Key for authentication'
            }
        }
    )

    user_model = api.model("User", {
        "id": fields.Integer,
        "name": fields.String,
    })

    profile_model = api.model("Profile", {
        "id": fields.Integer,
        "name": fields.String,
        "followers": fields.List(fields.Nested(user_model)),
        "following": fields.List(fields.Nested(user_model)),
    })

    tweet_model = api.model("Tweet", {
        "id": fields.Integer,
        "author_id": fields.Integer,
        "content": fields.String,
        "attachments": fields.List(fields.Nested(api.model("Attachment", {
            "id": fields.Integer,
            "url": fields.String,
            "src": fields.String,
        }))),
        "likes": fields.List(fields.Nested(api.model("Like", {
            "id": fields.Integer,
            "tweet_id": fields.Integer,
            "user_id": fields.Integer,
        }))),
    })

    tweets_ns = api.namespace("api/tweets", description="Operations with tweets")
    users_ns = api.namespace("api/users", description="Operations with users")
    media_ns = api.namespace("api/media", description="Just media")

    upload_parser = reqparse.RequestParser()
    upload_parser.add_argument("file", type=str, location="files", required=True, help="File required")

    from .models import User, Tweet, Follow, Like, Attachment
    from .utils import get_user_by_key, get_list_tweets, get_user_by_id

    def init_db():
        print("Инициализация базы данных")
        db.create_all()

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @app.cli.command("init-db")
    def init_once_per_process():
        """Команда для инициализации БД."""
        if not hasattr(g, "_db_initialized"):
            init_db()
            g._db_initialized = True
            print("База инициализирована.")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route('/')
    def index():
        return send_from_directory(app.template_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.template_folder, 'index.html')

    @app.route("/api/tweets", methods=['POST'])
    def create_tweet():
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        tweet_data = request.get_json()
        tweet = Tweet(
            author_id=user.id,
            content=tweet_data['tweet_data']
        )
        if 'media_ids' in tweet_data:
            media_items = Attachment.query.filter(Attachment.id.in_(tweet_data['media_ids'])).all()
            tweet.attachments.extend(media_items)
        db.session.add(tweet)
        db.session.commit()
        return {"result": True, "tweet_id": tweet.id}

    @app.route("/api/medias", methods=['POST'])
    def create_media():
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(app.root_path, 'uploads')
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            media = Attachment(
                url=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                src=file.filename
            )
            db.session.add(media)
            db.session.commit()
            return {"result": True, "media_id": media.id}
        else:
            return 400

    @app.route("/api/tweets/<int:tweet_id>", methods=['DELETE'])
    def delete_tweet(tweet_id):
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        tweet = Tweet.query.get(tweet_id)
        if tweet and tweet.author_id == user.id:
            db.session.delete(tweet)
            db.session.commit()
            return {"result": True}
        else:
            return 404

    @app.route("/api/tweets/<int:tweet_id>/likes", methods=['POST'])
    def like_tweet(tweet_id):
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        like = Like(
            user_id=user.id,
            tweet_id=tweet_id
        )
        db.session.add(like)
        db.session.commit()
        return {"result": True}

    @app.route("/api/tweets/<int:tweet_id>/likes", methods=['DELETE'])
    def unlike_tweet(tweet_id):
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        like = Like.query.filter_by(user_id=user.id, tweet_id=tweet_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
        return {"result": True}

    @app.route("/api/users/<int:user_id>/follow", methods=['POST'])
    def follow_user(user_id):
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        follow = Follow(
            follow_on_id=user_id,
            follower_id=user.id
        )
        db.session.add(follow)
        db.session.commit()
        return {"result": True}

    @app.route("/api/users/<int:user_id>/follow", methods=['DELETE'])
    def unfollow_user(user_id):
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        follow = Follow.query.filter_by(follow_on_id=user_id, follower_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()
        return {"result": True}

    @app.route("/api/tweets")
    def get_tweets_list():
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return 401
        user = get_user_by_key(api_key)
        try:
            tweets = get_list_tweets(user)
        except Exception as e:
            print(e)
            return {"result": False, "error_type": "db_error", "error_message": "Ошибка при получении списка твитов"}
        return {"result": True, "tweets": tweets}

    @app.route("/api/users/me")
    def get_user_info():
        api_key = request.headers.get('Api-Key')
        if not api_key:
            return "No API key", 401
        user = get_user_by_key(api_key)
        followers = Follow.query.filter_by(follower_id=user.id).all()
        followings = Follow.query.filter_by(follow_on_id=user.id).all()
        return {
            "result": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [{"id": follower.follower_id, "name": get_user_by_id(follower.follower_id).name} for follower in
                              followers],
                "following": [{"id": following.follow_on_id, "name": get_user_by_id(following.follow_on_id).name} for following in
                              followings],
            }
        }

    @app.route("/api/users/<int:user_id>")
    def get_user_info_by_id(user_id):
        user = User.query.get(user_id)
        followers = Follow.query.filter_by(follower_id=user.id).all()
        followings = Follow.query.filter_by(follow_on_id=user.id).all()
        return {
            "result": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [{"id": following.follow_on_id, "name": get_user_by_id(following.follow_on_id).name} for following in
                              followings],
                "following": [{"id": follower.follower_id, "name": get_user_by_id(follower.follower_id).name} for follower in
                              followers],
            }
        }

    @tweets_ns.route("/")
    class TweetList(Resource):
        @tweets_ns.doc(security="Api-Key")
        @tweets_ns.response(401, "Api-Key not found")
        @tweets_ns.marshal_list_with(tweet_model)
        def get(self):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            try:
                tweets = get_list_tweets(user)
            except Exception:
                return {"result": False, "error_type": "db_error",
                        "error_message": "Error in database"}
            return {"result": True, "tweets": tweets}

        @tweets_ns.doc(security="Api-Key")
        @tweets_ns.expect(api.model("TweetCreate", {
            "tweet_data": fields.String(required=True),
            "media_ids": fields.List(fields.Integer, description="ID media"),
        }))
        @tweets_ns.response(201, "Tweet created", api.model("TweetCreateID", {"tweet_id": fields.Integer}))
        def post(self):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            tweet_data = request.get_json()
            tweet = Tweet(
                author_id=user.id,
                content=tweet_data['tweet_data']
            )
            if 'media_ids' in tweet_data:
                media_items = Attachment.query.filter(Attachment.id.in_(tweet_data['media_ids'])).all()
                tweet.attachments.extend(media_items)
            db.session.add(tweet)
            db.session.commit()
            return {"result": True, "tweet_id": tweet.id}

    @tweets_ns.route("/<int:tweet_id>")
    class TweetResource(Resource):
        @tweets_ns.doc(security="Api-Key")
        @tweets_ns.response(401, "Api-Key not found")
        @tweets_ns.response(404, "Tweet not found")
        @tweets_ns.response(204, "Tweet deleted")
        def delete(self, tweet_id):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            tweet = Tweet.query.get(tweet_id)
            if tweet and tweet.author_id == user.id:
                db.session.delete(tweet)
                db.session.commit()
                return {"result": True}, 204
            else:
                api.abort(404, "Tweet not found")

    @media_ns.route("/")
    class MediaUpload(Resource):
        @media_ns.doc(security="Api-Key")
        @media_ns.response(401, "Api-Key not found")
        @media_ns.response(400, "File not allowed")
        @media_ns.expect(upload_parser)
        @media_ns.response(201, "Media uploaded", api.model("MediaUploadID", {"media_id": fields.Integer}))
        def post(self):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(app.root_path, 'uploads')
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                media = Attachment(
                    url=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                    src=file.filename
                )
                db.session.add(media)
                db.session.commit()
                return {"result": True, "media_id": media.id}, 201
            else:
                api.abort(400, "File not allowed")

    @users_ns.route("/<int:user_id>/follow")
    class FollowResource(Resource):
        @users_ns.doc(security="Api-Key")
        @users_ns.response(401, "Api-Key not found")
        @users_ns.response(201, "Follow created")
        def post(self, user_id):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            follow = Follow(
                follow_on_id=user_id,
                follower_id=user.id
            )
            return {"result": True}, 201

        @users_ns.doc(security="Api-Key")
        @users_ns.response(401, "Api-Key not found")
        @users_ns.response(204, "Follow deleted")
        def delete(self, user_id):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            follow = Follow.query.filter_by(follow_on_id=user_id, follower_id=user.id).first()
            if follow:
                db.session.delete(follow)
                db.session.commit()
            return {"result": True}, 204
    @tweets_ns.route("/<int:tweet_id>")
    class LikeResource(Resource):
        @tweets_ns.doc(security="Api-Key")
        @tweets_ns.response(401, "Api-Key not found")
        @tweets_ns.response(201, "Like created")
        def post(self, tweet_id):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            like = Like(
                user_id=user.id,
                tweet_id=tweet_id
            )
            db.session.add(like)
            db.session.commit()
            return {"result": True}, 201

        @tweets_ns.doc(security="Api-Key")
        @tweets_ns.response(401, "Api-Key not found")
        @tweets_ns.response(204, "Like deleted")
        def delete(self, tweet_id):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                return 401
            user = get_user_by_key(api_key)
            like = Like.query.filter_by(user_id=user.id, tweet_id=tweet_id).first()
            if like:
                db.session.delete(like)
                db.session.commit()
            return {"result": True}

    @users_ns.route("/me")
    class UserMeResource(Resource):
        @users_ns.doc(security="Api-Key")
        @users_ns.response(401, "Api-Key not found")
        @users_ns.marshal_with(profile_model)
        def get(self):
            api_key = request.headers.get('Api-Key')
            if not api_key:
                api.abort(401, "Api-Key required")
            user = get_user_by_key(api_key)
            followers = Follow.query.filter_by(follower_id=user.id).all()
            followings = Follow.query.filter_by(follow_on_id=user.id).all()
            return {
                "result": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "followers": [{"id": follower.follower_id, "name": follower.follower.user.name} for follower in
                                  followers],
                    "following": [{"id": following.follow_on_id, "name": following.follow_on.user.name} for following in
                                  followings],
                }
            }

    @users_ns.route("/<int:user_id>")
    class UserResource(Resource):
        @users_ns.doc(security="Api-Key")
        @users_ns.response(404, "User not found")
        @users_ns.marshal_with(profile_model)
        def get(self, user_id):
            user = User.query.get(user_id)
            if not user:
                api.abort(404, "User not found")
            followers = Follow.query.filter_by(follower_id=user.id).all()
            followings = Follow.query.filter_by(follow_on_id=user.id).all()
            return {
                "result": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "followers": [{"id": follower.follower_id, "name": follower.follower.user.name} for follower in
                                  followers],
                    "following": [{"id": following.follow_on_id, "name": following.follow_on.user.name} for following in
                                  followings],
                }
            }

    return app

