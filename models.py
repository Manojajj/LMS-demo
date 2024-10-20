from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # Import for datetime handling

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Change this to your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Agent {self.name}>"

class Deal(db.Model):
    __tablename__ = 'deal'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Deal {self.id}: {self.description}>"

class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    owner = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Property {self.name}>"

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Vehicle {self.make} {self.model}>"

class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(100))
    address = db.Column(db.String(255))

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)


class Shipment(db.Model):
    __tablename__ = 'shipment'

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)  # Unique tracking number for the shipment
    description = db.Column(db.String(255), nullable=False)  # Description of the shipment
    origin = db.Column(db.String(100), nullable=False)  # Origin location of the shipment
    destination = db.Column(db.String(100), nullable=False)  # Destination location of the shipment
    weight = db.Column(db.Float, nullable=False)  # Weight of the shipment
    shipment_date = db.Column(db.Date, nullable=False)  # Date when the shipment was created
    delivery_date = db.Column(db.Date, nullable=False)  # Expected delivery date

    def __repr__(self):
        return f"<Shipment {self.tracking_number} from {self.origin} to {self.destination}>"


class Announcement(db.Model):
    __tablename__ = 'announcement'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))  # Adjust the type and length as needed
    message = db.Column(db.Text)  # Adjust the type as needed

# Create all tables
with app.app_context():
    db.create_all()

# API Routes for Vehicle Management
@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    required_fields = ['make', 'model', 'year', 'mileage', 'condition', 'price']

    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required."}), 400

    try:
        new_vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            mileage=data['mileage'],
            condition=data['condition'],
            price=data['price'],
            description=data.get('description')
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({"message": "Vehicle added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify([{
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'mileage': vehicle.mileage,
            'condition': vehicle.condition,
            'price': vehicle.price,
            'description': vehicle.description
        } for vehicle in vehicles]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.json

    # Update fields only if provided
    vehicle.make = data.get('make', vehicle.make)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.year = data.get('year', vehicle.year)
    vehicle.mileage = data.get('mileage', vehicle.mileage)
    vehicle.condition = data.get('condition', vehicle.condition)
    vehicle.price = data.get('price', vehicle.price)
    vehicle.description = data.get('description', vehicle.description)

    try:
        db.session.commit()
        return jsonify({"message": "Vehicle updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    try:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({"message": "Vehicle deleted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

