from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_cors import CORS
from flask_migrate import Migrate

from datetime import datetime

from timeformat import utc_timestamp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)


# Configuring Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(64))
    pwd = db.Column(db.String(64))


    def __init__(self, username, email, pwd):
        self.username = username
        self.email = email
        self.pwd = pwd

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship('User', foreign_keys=uid)
    text = db.Column(db.String(280))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Methods for Users

def getUsers():
    users = User.query.all()
    return [ 
        {
            "id": i.id,
            "username": i.username,
            "email": i.email,
            "pwd": i.pwd,
        }
        for i in users
    ]
def getUser(uid):
    user = User.query.get(uid)
    return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "pwd": user.pwd
        }
def addUser(username, email, pwd):
    try:
        user = User(username, email, pwd)
        db.session.add(user)
        db.session.commit()
        return True        
    except Exception as e:
        print(e)
        return False

def removeUser(uid):
    try:
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False

# API for users

@app.route('/api/users')
def get_users():
    return jsonify(getUsers())

@app.route('/api/users/create', methods=["POST"])
def add_user():
    try:
        username = request.json['username']
        email = request.json['email']
        pwd = request.json['pwd']

        addUser(username, email, pwd)
        return jsonify({
            "success": True
        })
    except Exception as e:
        print(e)
        return jsonify({"error": "Invalid form"})


# Methods for Tweets

def getTweets():
    tweets = Tweet.query.order_by(desc('created_at'))
    return [{
        "id": i.id,
        "text": i.text,
        "created_at": utc_timestamp(i.created_at),
        "user": getUser(i.uid)
        }
        for i in tweets
    ]
def getUserTweets(uid):
    tweets = Tweet.query.filter_by(uid).all()
    return [{
        "id": i.id,
        "text": i.text,
        "created_at": i.created_at,
        "userid": uid
        }
        for i in tweets
    ]

def createTweet(text, uid):
    if text and uid:
        try:
            user = User.query.get(uid)
            tweet = Tweet(uid=uid, text=text)
            db.session.add(tweet)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    return False

def deleteTweet(tid):
    try:
        tweet = Tweet.query.get(tid)
        db.session.delete(tweet)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False

# API for Tweets
@app.route("/api/tweets")
def get_tweets():
    return jsonify(getTweets())

@app.route("/api/tweets/create", methods=["POST"])
def create_tweet():
    try:
        text = request.json['text']
        uid = request.json['uid']
        if createTweet(text, uid):
            return jsonify({
                "success": True
            })
        return jsonify({"error": "Tweet creation failed"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Invalid form"})

@app.route("/api/tweets/delete", methods=["DELETE"])
def delete_tweet():
    try:
        tid = request.json['id']
        if deleteTweet(tid):
            return jsonify({
                "success": True
            })
        return jsonify({"error": "Tweet deletion failed"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Invalid form"})


if __name__ == '__main__':
    app.run(debug=True)