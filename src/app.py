from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'todo.db')
db_uri = 'sqlite:///{}'.format(db_path)

app.config['SECRET_KEY'] = 'thisisscret'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    publicId    = db.Column(db.String(50), unique=True)
    name        = db.Column(db.String(50))
    password    = db.Column(db.String(200))
    admin       = db.Column(db.Boolean)

class ToDo(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    text        = db.Column(db.String(50))    
    isComplete  = db.Column(db.Boolean)
    userId      = db.Column(db.Integer)

@app.route('/user',methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        userData = {}
        userData['publicID']    =   user.publicId
        userData['name']        =   user.name
        userData['password']    =   user.password
        userData['admin']       =   user.admin
        output.append(userData)
    return jsonify({'users':output})

@app.route('/user/<publicID>',methods=['GET'])
def get_user(publicID):    
    user = User.query.filter_by(publicId=publicID).first()
    if user:
        userData = {}
        userData['publicID']    =   user.publicId
        userData['name']        =   user.name
        userData['password']    =   user.password
        userData['admin']       =   user.admin
        return jsonify({'user':userData})
    else:
        return jsonify({'message': 'No user found'})

@app.route('/user', methods=['POST'])
def create_user():
    userData = request.get_json()
    print(userData)
    hashed = generate_password_hash(userData['password'], method='sha256')
    new_user = User(publicId=str(uuid.uuid4()), name=userData['name'], password=hashed, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created'}) 

@app.route('/user/<publicID>', methods=['PUT'])
def promote_user(publicID):    
    user = User.query.filter_by(publicId=publicID).first()
    if user:
        user.admin = True
        db.session.commit()
        return jsonify({'message': 'The user has been promoted'})
    else:
        return jsonify({'message': 'No user found'})

@app.route('/user/<publicID>', methods=['DELETE'])
def delete_user(publicID):
    user = User.query.filter_by(publicId=publicID).first()
    if user:
       db.session.delete(user)
       db.session.commit()
       return jsonify({'message': 'The user has been deleted'})
    else:
        return jsonify({'message': 'No user found'})


if __name__ == '__main__':
    app.run(debug=True)
