from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

import os
from flask import Flask, abort, request, jsonify, g, url_for

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import json


# extensions
auth = HTTPBasicAuth()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    count = db.Column(db.Integer)
    fortressid = db.Column(db.Integer, db.ForeignKey('fortress.id'))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))


class Alliance(db.Model):
    __tablename__ = 'alliance'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    users = db.relationship("User", backref=db.backref("alliance"))
    fortresses = db.relationship("Fortress", backref=db.backref("alliance"))


class Fortress(db.Model):
    __tablename__ = 'fortress'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  # name of fort is the name of the streamer
    allianceid = db.Column(db.Integer, db.ForeignKey(
        "alliance.id"), nullable=False)
    items = db.relationship("Item", backref=db.backref("fortress"))


class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    count = db.Column(db.Integer)


class Ship(db.Model):
    __tablename__ = 'ship'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String)

# upgrades are attached to one ship


class Upgrade(db.Model):
    __tablename__ = 'upgrade'
    id = db.Column(db.Integer, primary_key=True)
    shipid = db.Column(db.Integer, db.ForeignKey('ship.id'))
    type = db.Column(db.String)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    inventory = db.relationship("Item", backref=db.backref("user"))
    inventorysize = db.Column(db.Integer, default=100)
    allianceid = db.Column(db.Integer, db.ForeignKey('alliance.id'))
    twitchuserid = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(64))
    color = db.String(32)

    isModerator = db.Column(db.Boolean)
    isSubscriber = db.Column(db.Boolean)

    x = db.Column(db.Integer, default=0)
    y = db.Column(db.Integer, default=0)

    # STATS #
    meleeAtkXp = db.Column(db.Integer, default=0)
    magicAtkXp = db.Column(db.Integer, default=0)
    rangeAtkXp = db.Column(db.Integer, default=0)

    healthXp = db.Column(db.Integer, default=0)
    shieldXp = db.Column(db.Integer, default=0)
    evasionXp = db.Column(db.Integer, default=0)
    sizeXp = db.Column(db.Integer, default=0)
    blockXp = db.Column(db.Integer, default=0)
    ResistXp = db.Column(db.Integer, default=0)
    speedXp = db.Column(db.Integer, default=0)

    '''The hash_password() method takes a plain password as argument and stores a hash of it with the user.
    This method is called when a new user is registering with the server, or when the user changes the password.'''

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    ''' The verify_password() method takes a plain password as argument and returns True if the password is correct or
    False if not. This method is called whenever the user provides credentials and they need to be validated.'''

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

    def update_password(self, password, new_password):
        if(self.verify_password(password) == True):
            self.hash_password(new_password)
            print("Updated password for {}".format(self.username))
        else:
            return("Password change failed, password hash did not match for user: {}".format(self.username))
