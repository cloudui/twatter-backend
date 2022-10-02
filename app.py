from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

# Configuring Database

db = SQLAlchemy(app)
class Users(db.Model):
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


@app.route("/api/users", methods=["GET", "POST", "DELETE"])
def users():
    method = request.method
    if method.lower() == "get":
        users = Users.query.all()
        return jsonify([ 
            {
                "id": i.id,
                "username": i.username,
                "email": i.email,
                "pwd": i.pwd,
            }
            for i in users
        ])
    elif method.lower() == "post":
        try:
            username = request.json["username"]
            email = request.json["email"]
            pwd = request.json["pwd"]
            if username and pwd and email:
                try:
                    user = Users(username, email, pwd)
                    db.session.add(user)
                    db.session.commit()
                    return jsonify({"success": True})
                except Exception as e:
                    return ({"error": e})
            else:
                return jsonify({"error": "Invalid form"})
        except:
            return jsonify({"error": "Invalid form"})

    elif method.lower() == "delete":
        try:
            uid = request.json["id"]
            if uid:
                try:
                    user = Users.query.get(uid)
                    db.session.delete(user)
                    db.session.commit()
                    return jsonify({"success": True})
                except Exception as e:
                    return jsonify({"error": e})
            else:
                return jsonify({"error": "Invalid Form"})
        except:
            return jsonify({"error": "m"})

# Methods for Tweets
def getTweets():
    tweets = Tweet.query.all()
    return [{
        "id": i.id,
        "text": i.text,
        "user": getUser(i.uid)
        }
        for i in tweets
    ]
def getUserTweets(uid):
    tweets = Tweet.query.filter_by(uid=uid).all()
    return [{
        "id": i.id,
        "text": i.text,
        "userid": uid
        }
        for i in tweets
    ]

def addTweet(content, uid):
    if content and uid:
        try:
            user = Users.query.get(uid=uid)
            tweet = Tweet(uid=uid, content=content)
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

if __name__ == '__main__':
    app.run(debug=True)