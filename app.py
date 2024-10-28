from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from datetime import datetime
import os

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # Change this to your database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Initialize Flask app and configuration
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Models
class AgentManagement(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    messages = db.relationship('SecureMessage', backref='agent', lazy=True)

class Communication(db.Model):
    __tablename__ = 'communication'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Deal(db.Model):
    __tablename__ = 'deal'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    owner = db.Column(db.String(100), nullable=False)

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
    filename = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Shipment(db.Model):
    __tablename__ = 'shipment'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    shipment_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)

class Announcement(db.Model):
    __tablename__ = 'announcement'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    message = db.Column(db.Text)

class SecureMessage(db.Model):
    __tablename__ = 'secure_messages'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    admin_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.Column(db.String(10), nullable=False)

# Forms
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('search', query=request.form['query']))

    # Fetch current shipments and agents
    shipments = Shipment.query.all()  # Replace with your actual query
    agents = AgentManagement.query.all()  # Replace with your actual query
    announcements = []  # Replace with actual announcements if you have

    return render_template('home.html', shipments=shipments, agents=agents, announcements=announcements)

# Route for the Agent Dashboard
@app.route('/agent_dashboard', methods=['GET'], endpoint='agent_dashboard_view')
def agent_dashboard():
    current_agent_id = 1  # Replace with the actual logged-in agent's ID
    communications = Communication.query.filter_by(agent_id=current_agent_id).order_by(Communication.timestamp.desc()).all()
    return render_template('agent_dashboard.html', communications=communications)

# Route to send a message to the admin
@app.route('/agent_dashboard/send_message', methods=['POST'], endpoint='send_message_to_admin')
def send_message_to_admin():
    data = request.json
    agent_id = 1  # Replace with actual logic to get the logged-in agent's ID

    if 'message' not in data or not data['message'].strip():
        return jsonify({"error": "Message content is required"}), 400

    try:
        new_message = Communication(
            agent_id=agent_id,
            message=data['message'],
            sender='agent',
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"message": "Message sent to admin successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to get messages from the admin
@app.route('/agent_dashboard/get_messages', methods=['GET'], endpoint='get_messages_from_admin')
def get_messages_from_admin():
    agent_id = 1  # Replace with actual logic to get the logged-in agent's ID

    try:
        communications = Communication.query.filter_by(agent_id=agent_id).order_by(Communication.timestamp.desc()).all()
        return jsonify([{
            'message': communication.message,
            'sender': communication.sender,
            'timestamp': communication.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for communication in communications]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin')
#@login_required  # Ensure user is logged in
#@admin_required  # Ensure user has admin privileges
def admin():
    total_agents = AgentManagement.query.count()
    total_users = User.query.count()
    total_shipments = Shipment.query.count()
    total_deals = Deal.query.count()
    total_properties = Property.query.count()
    total_vehicles = Vehicle.query.count()
    total_clients = Client.query.count()

    return render_template('admin.html',
                           total_agents=total_agents,
                           total_users=total_users,
                           total_shipments=total_shipments,
                           total_deals=total_deals,
                           total_properties=total_properties,
                           total_vehicles=total_vehicles,
                           total_clients=total_clients)

@app.route('/admin/inbox', methods=['GET'])
#@login_required  # Ensure the user is logged in as an admin
def admin_inbox():
    # Assuming current_user is an admin and you have Flask-Login to get current_user
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.timestamp.desc()).all()

    return render_template('admin_inbox.html', messages=messages)

@app.route('/admin/messages', methods=['GET', 'POST'])
#@login_required  # Ensure the user is logged in, if you're using Flask-Login
def admin_messages():
    if request.method == 'POST':
        content = request.form.get('content')
        receiver_id = request.form.get('receiver_id')  # ID of the Agent to send the message to

        if not content or not receiver_id:
            return jsonify({"error": "Message content and receiver ID are required."}), 400

        new_message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)

        try:
            db.session.add(new_message)
            db.session.commit()
            return jsonify({"message": "Message sent successfully!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    agents = Agent.query.all()  # Get all agents to display in the form
    return render_template('admin_messages.html', agents=agents)

@app.route('/admin/users')
def user_management():
    users = User.query.all()  # Fetch all users from the database
    return render_template('user_management.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Logic to add a new user
        pass
    return render_template('add_user.html')  # Create this template

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)  # Fetch user details
    if request.method == 'POST':
        # Logic to edit the user
        pass
    return render_template('edit_user.html', user=user)  # Create this template

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('user_management'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # Perform search logic based on your data models
        # For example, searching shipments and agents
        shipments = Shipment.query.filter(Shipment.details.contains(query)).all()
        agents = AgentManagement.query.filter(AgentManagement.name.contains(query)).all()

        return render_template('search_results.html', shipments=shipments, agents=agents, query=query)

    return redirect(url_for('home'))  # Redirect if not a POST request

# About Us Route
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')  # Create this template file


# Contact Us Route
@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Handle contact form submission
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact_us'))

    return render_template('contact_us.html')  # Create this template file

@app.route('/shipments', methods=['GET'])
def shipment_management():
    shipments = Shipment.query.all()
    return render_template('shipment_management.html', shipments=shipments)

# Add Shipment Route
@app.route('/add_shipment', methods=['GET', 'POST'])
def add_shipment():
    if request.method == 'POST':
        # Retrieve form data
        tracking_number = request.form.get('tracking_number')
        description = request.form.get('description')
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        weight = request.form.get('weight')
        shipment_date = request.form.get('shipment_date')
        delivery_date = request.form.get('delivery_date')

        # Validate required fields
        if not tracking_number or not description or not origin or not destination or not weight or not shipment_date or not delivery_date:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('add_shipment'))

        try:
            # Create a new Shipment object
            new_shipment = Shipment(
                tracking_number=tracking_number,
                description=description,
                origin=origin,
                destination=destination,
                weight=weight,
                shipment_date=shipment_date,
                delivery_date=delivery_date
            )
            db.session.add(new_shipment)
            db.session.commit()
            flash("Shipment added successfully.", "success")
        except Exception as e:
            # Handle database errors
            db.session.rollback()  # Rollback in case of error
            flash(f"An error occurred while adding the shipment: {str(e)}", "danger")

        return redirect(url_for('home'))

    return render_template('add_shipment.html')

# Agent Management Route
@app.route('/agents', methods=['GET', 'POST'])
def agent_management():
    if request.method == 'POST':
        agent_name = request.form.get('name')
        agent_role = request.form.get('role')

        if not agent_name or not agent_role:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('agent_management'))

        new_agent = AgentManagement(name=agent_name, role=agent_role)
        db.session.add(new_agent)
        db.session.commit()
        flash("New agent added successfully.", "success")
        return redirect(url_for('agent_management'))

    agents = AgentManagement.query.all()
    return render_template('agent_management.html', agents=agents)


# Delete Agent Route
@app.route('/agents/delete/<int:id>', methods=['POST'])
def delete_agent(id):
    agent = AgentManagement.query.get_or_404(id)
    db.session.delete(agent)
    db.session.commit()
    flash(f'Agent {agent.name} deleted successfully.', "success")
    return redirect(url_for('agent_management'))


# Deal Management Route (View Deals and Handle Deal Deletion)
@app.route('/deals', methods=['GET', 'POST'])
def deal_management():
    deals = Deal.query.all()
    return render_template('deal_management.html', deals=deals)


# Add Deal Route
@app.route('/deals/add', methods=['POST'])
def add_deal():
    client_name = request.form.get('client_name')
    property_name = request.form.get('property_name')
    amount = request.form.get('amount')
    status = request.form.get('status')

    # Validate form data
    if not client_name or not property_name or not amount or not status:
        flash("Please fill out all fields.", "danger")
        return redirect(url_for('deal_management'))

    try:
        # Create and add new deal
        new_deal = Deal(description=f"{client_name} - {property_name} for ${amount}, Status: {status}")
        db.session.add(new_deal)
        db.session.commit()
        flash("Deal added successfully.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback transaction on error
        flash(f"Error adding deal: {str(e)}", "danger")

    return redirect(url_for('deal_management'))


# Delete Deal Route
@app.route('/deals/delete/<int:deal_id>', methods=['POST'])
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    try:
        # Delete the selected deal
        db.session.delete(deal)
        db.session.commit()
        flash(f"Deal with ID {deal_id} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback transaction on error
        flash(f"Error deleting deal: {str(e)}", "danger")

    return redirect(url_for('deal_management'))  # Redirect back to deal management page


# Property Management Route
@app.route('/properties', methods=['GET', 'POST'])
def property_management():
    if request.method == 'POST':
        property_name = request.form.get('name')
        location = request.form.get('location')
        size = request.form.get('size')
        price = request.form.get('price')
        owner = request.form.get('owner')

        if not property_name or not location or not size or not price or not owner:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('property_management'))

        new_property = Property(name=property_name, location=location, size=size, price=price, owner=owner)
        db.session.add(new_property)
        db.session.commit()
        flash("New property added successfully.", "success")
        return redirect(url_for('property_management'))

    properties = Property.query.all()
    return render_template('property_management.html', properties=properties)


# Delete Property Route
@app.route('/properties/delete/<int:id>', methods=['POST'])
def delete_property(id):
    property = Property.query.get_or_404(id)
    db.session.delete(property)
    db.session.commit()
    flash(f'Property {property.name} deleted successfully.', "success")
    return redirect(url_for('property_management'))


# Vehicle Management Route
@app.route('/vehicles', methods=['GET'])
def vehicle_management():
    vehicles = Vehicle.query.all()
    return render_template('vehicle_management.html', vehicles=vehicles)


# Add Vehicle Route
@app.route('/vehicles/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        condition = request.form.get('condition')
        price = request.form.get('price')
        description = request.form.get('description')

        if not make or not model or not year or not mileage or not condition or not price:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('add_vehicle'))

        new_vehicle = Vehicle(make=make, model=model, year=year, mileage=mileage, condition=condition, price=price,
                              description=description)
        db.session.add(new_vehicle)
        db.session.commit()
        flash("Vehicle added successfully.", "success")
        return redirect(url_for('vehicle_management'))

    return render_template('add_vehicle.html')  # Create this template file


# Edit Vehicle Route
@app.route('/vehicles/edit/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)

    if request.method == 'POST':
        vehicle.make = request.form.get('make', vehicle.make)
        vehicle.model = request.form.get('model', vehicle.model)
        vehicle.year = request.form.get('year', vehicle.year)
        vehicle.mileage = request.form.get('mileage', vehicle.mileage)
        vehicle.condition = request.form.get('condition', vehicle.condition)
        vehicle.price = request.form.get('price', vehicle.price)
        vehicle.description = request.form.get('description', vehicle.description)

        db.session.commit()
        flash("Vehicle updated successfully.", "success")
        return redirect(url_for('vehicle_management'))

    return render_template('edit_vehicle.html', vehicle=vehicle)  # Create this template file


# Delete Vehicle Route
@app.route('/vehicles/delete/<int:id>', methods=['POST'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    flash(f"Vehicle {vehicle.make} {vehicle.model} deleted successfully.", "success")
    return redirect(url_for('vehicle_management'))

# Client Management Route
@app.route('/clients', methods=['GET'])
def client_management():
    clients = Client.query.all()  # Retrieve all clients
    return render_template('client_management.html', clients=clients)


# Add Client Route
@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not name or not email or not phone:
            flash("Please fill out all mandatory fields.", "danger")
            return redirect(url_for('add_client'))

        new_client = Client(name=name, email=email, phone=phone, address=address)
        db.session.add(new_client)
        db.session.commit()
        flash("Client added successfully.", "success")
        return redirect(url_for('client_management'))

    return render_template('add_client.html')


# Edit Client Route
@app.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    client = Client.query.get_or_404(id)

    if request.method == 'POST':
        client.name = request.form.get('name', client.name)
        client.email = request.form.get('email', client.email)
        client.phone = request.form.get('phone', client.phone)
        client.address = request.form.get('address', client.address)

        db.session.commit()
        flash("Client updated successfully.", "success")
        return redirect(url_for('client_management'))

    return render_template('edit_client.html', client=client)


# Delete Client Route
@app.route('/clients/delete/<int:id>', methods=['POST'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash(f"Client {client.name} deleted successfully.", "success")
    return redirect(url_for('client_management'))


# Document Management Route (Handle file uploads)
@app.route('/document_management', methods=['GET', 'POST'])
def document_management():
    if request.method == 'POST':
        file = request.files.get('file')

        if file:
            # Validate file type
            if allowed_file(file.filename):
                # Save the file
                file.save(f'uploads/{file.filename}')
                flash("File uploaded successfully.", "success")
            else:
                flash("File type not allowed.", "danger")
        else:
            flash("No file uploaded.", "danger")

    documents = Document.query.all()  # Fetch all documents
    return render_template('document_management.html', documents=documents)


# Helper function to check allowed file types
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace with actual user validation logic
        if username == "admin" and password == "password":  # Replace with hashed check
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Login failed. Check your credentials.", "danger")

    return render_template('login.html')  # Create this template file


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))


# Custom Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# Advanced Analytics Route
@app.route('/advanced_analytics')
def advanced_analytics():
    total_agents = AgentManagement.query.count()
    total_users = User.query.count()
    total_shipments = Shipment.query.count()
    total_deals = Deal.query.count()
    total_properties = Property.query.count()
    total_vehicles = Vehicle.query.count()
    total_clients = Client.query.count()

    analytics_data = {
        "Total Agents": total_agents,
        "Total Users": total_users,
        "Total Shipments": total_shipments,
        "Total Deals": total_deals,
        "Total Properties": total_properties,
        "Total Vehicles": total_vehicles,
        "Total Clients": total_clients,
    }

    return render_template('advanced_analytics.html', analytics_data=analytics_data)  # Create this template file

@app.route('/agent_dashboard')
def agent_dashboard():
    # Example data (you can fetch real data from your database)
    agent_data = {
        'total_clients': 30,
        'active_deals': 5,
        'shipments_in_progress': 12,
        'completed_shipments': 20,
    }
    return render_template('agent_dashboard.html', agent_data=agent_data)

# Main block
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)
