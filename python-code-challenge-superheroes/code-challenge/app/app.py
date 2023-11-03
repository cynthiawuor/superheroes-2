#!/usr/bin/env python3
from random import seed
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow


app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db, seed)

db.init_app(app)

@app.route('/')
def home():
    return ''

# Define Hero model
class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    super_name = db.Column(db.String(100), nullable=False)
    powers = db.relationship('Power', secondary='hero_power', backref='heroes')

# Define Power model
class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

# Define HeroPower model to establish many-to-many relationship
class HeroPower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('power.id'), nullable=False)
    strength = db.Column(db.String(20), nullable=False)  # Add validation for 'strength'

# Define Marshmallow schemas for serialization
class HeroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hero

class PowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Power

# Routes

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_schema = HeroSchema(many=True)
    return jsonify(hero_schema.dump(heroes))

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        hero_schema = HeroSchema()
        return jsonify(hero_schema.dump(hero))
    return jsonify({'error': 'Hero not found'}), 404

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    power_schema = PowerSchema(many=True)
    return jsonify(power_schema.dump(powers))

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power:
        power_schema = PowerSchema()
        return jsonify(power_schema.dump(power))
    return jsonify({'error': 'Power not found'}), 404

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power:
        description = request.json.get('description')
        if description and len(description) >= 20:
            power.description = description
            db.session.commit()
            power_schema = PowerSchema()
            return jsonify(power_schema.dump(power))
        else:
            return jsonify({'errors': ['Validation errors']}), 400
    return jsonify({'error': 'Power not found'}), 404

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    strength = request.json.get('strength')
    power_id = request.json.get('power_id')
    hero_id = request.json.get('hero_id')
    
    # Add validation for 'strength' and check if power and hero exist

    hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
    db.session.add(hero_power)
    db.session.commit()

    # Fetch the updated Hero data
    hero = Hero.query.get(hero_id)
    hero_schema = HeroSchema()
    return jsonify(hero_schema.dump(hero))

if __name__ == '__main__':
    app.run(port=5555)

