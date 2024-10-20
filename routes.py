from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from .models import Agent, Deal, Property, Vehicle, Client, Document, Shipment, Announcement
from . import db
from flask_socketio import SocketIO, emit

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('routes.search', query=request.form['query']))

    # Fetch current shipments and agents
    shipments = Shipment.query.all()  # Replace with your actual query
    agents = Agent.query.all()  # Replace with your actual query
    announcements = []  # Replace with actual announcements if you have

    return render_template('home.html', shipments=shipments, agents=agents, announcements=announcements)

@routes.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # Perform search logic based on your data models
        # For example, searching shipments and agents
        shipments = Shipment.query.filter(Shipment.details.contains(query)).all()
        agents = Agent.query.filter(Agent.name.contains(query)).all()

        return render_template('search_results.html', shipments=shipments, agents=agents, query=query)

    return redirect(url_for('routes.home'))  # Redirect if not a POST request

# About Us Route
@routes.route('/about_us')
def about_us():
    return render_template('about_us.html')  # Create this template file


# Contact Us Route
@routes.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Handle contact form submission
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('routes.contact_us'))

    return render_template('contact_us.html')  # Create this template file

@routes.route('/shipments', methods=['GET'])
def shipment_management():
    shipments = Shipment.query.all()
    return render_template('shipment_management.html', shipments=shipments)

# Add Shipment Route
@routes.route('/add_shipment', methods=['GET', 'POST'])
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
            return redirect(url_for('routes.add_shipment'))

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

        return redirect(url_for('routes.home'))

    return render_template('add_shipment.html')



# View Reports Route
@routes.route('/view_reports')
def view_reports():
    return render_template('view_reports.html')  # Ensure this template exists


# Secure Communication Route
@routes.route('/secure_communication')
def secure_communication():
    return render_template('secure_communication.html')  # Ensure this template exists


# Agent Management Route
@routes.route('/agents', methods=['GET', 'POST'])
def agent_management():
    if request.method == 'POST':
        agent_name = request.form.get('name')
        agent_role = request.form.get('role')

        if not agent_name or not agent_role:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('routes.agent_management'))

        new_agent = Agent(name=agent_name, role=agent_role)
        db.session.add(new_agent)
        db.session.commit()
        flash("New agent added successfully.", "success")
        return redirect(url_for('routes.agent_management'))

    agents = Agent.query.all()
    return render_template('agent_management.html', agents=agents)


# Delete Agent Route
@routes.route('/agents/delete/<int:id>', methods=['POST'])
def delete_agent(id):
    agent = Agent.query.get_or_404(id)
    db.session.delete(agent)
    db.session.commit()
    flash(f'Agent {agent.name} deleted successfully.', "success")
    return redirect(url_for('routes.agent_management'))


# Deal Management Route (View Deals and Handle Deal Deletion)
@routes.route('/deals', methods=['GET', 'POST'])
def deal_management():
    deals = Deal.query.all()
    return render_template('deal_management.html', deals=deals)


# Add Deal Route
@routes.route('/deals/add', methods=['POST'])
def add_deal():
    client_name = request.form.get('client_name')
    property_name = request.form.get('property_name')
    amount = request.form.get('amount')
    status = request.form.get('status')

    # Validate form data
    if not client_name or not property_name or not amount or not status:
        flash("Please fill out all fields.", "danger")
        return redirect(url_for('routes.deal_management'))

    try:
        # Create and add new deal
        new_deal = Deal(description=f"{client_name} - {property_name} for ${amount}, Status: {status}")
        db.session.add(new_deal)
        db.session.commit()
        flash("Deal added successfully.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback transaction on error
        flash(f"Error adding deal: {str(e)}", "danger")

    return redirect(url_for('routes.deal_management'))


# Delete Deal Route
@routes.route('/deals/delete/<int:deal_id>', methods=['POST'])
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

    return redirect(url_for('routes.deal_management'))  # Redirect back to deal management page


# Property Management Route
@routes.route('/properties', methods=['GET', 'POST'])
def property_management():
    if request.method == 'POST':
        property_name = request.form.get('name')
        location = request.form.get('location')
        size = request.form.get('size')
        price = request.form.get('price')
        owner = request.form.get('owner')

        if not property_name or not location or not size or not price or not owner:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for('routes.property_management'))

        new_property = Property(name=property_name, location=location, size=size, price=price, owner=owner)
        db.session.add(new_property)
        db.session.commit()
        flash("New property added successfully.", "success")
        return redirect(url_for('routes.property_management'))

    properties = Property.query.all()
    return render_template('property_management.html', properties=properties)


# Delete Property Route
@routes.route('/properties/delete/<int:id>', methods=['POST'])
def delete_property(id):
    property = Property.query.get_or_404(id)
    db.session.delete(property)
    db.session.commit()
    flash(f'Property {property.name} deleted successfully.', "success")
    return redirect(url_for('routes.property_management'))


# Vehicle Management Route
@routes.route('/vehicles', methods=['GET'])
def vehicle_management():
    vehicles = Vehicle.query.all()
    return render_template('vehicle_management.html', vehicles=vehicles)


# Add Vehicle Route
@routes.route('/vehicles/add', methods=['GET', 'POST'])
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
            return redirect(url_for('routes.add_vehicle'))

        new_vehicle = Vehicle(make=make, model=model, year=year, mileage=mileage, condition=condition, price=price,
                              description=description)
        db.session.add(new_vehicle)
        db.session.commit()
        flash("Vehicle added successfully.", "success")
        return redirect(url_for('routes.vehicle_management'))

    return render_template('add_vehicle.html')  # Create this template file


# Edit Vehicle Route
@routes.route('/vehicles/edit/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('routes.vehicle_management'))

    return render_template('edit_vehicle.html', vehicle=vehicle)  # Create this template file


# Delete Vehicle Route
@routes.route('/vehicles/delete/<int:id>', methods=['POST'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    flash(f"Vehicle {vehicle.make} {vehicle.model} deleted successfully.", "success")
    return redirect(url_for('routes.vehicle_management'))

# Client Management Route
@routes.route('/clients', methods=['GET'])
def client_management():
    clients = Client.query.all()  # Retrieve all clients
    return render_template('client_management.html', clients=clients)


# Add Client Route
@routes.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not name or not email or not phone:
            flash("Please fill out all mandatory fields.", "danger")
            return redirect(url_for('routes.add_client'))

        new_client = Client(name=name, email=email, phone=phone, address=address)
        db.session.add(new_client)
        db.session.commit()
        flash("Client added successfully.", "success")
        return redirect(url_for('routes.client_management'))

    return render_template('add_client.html')


# Edit Client Route
@routes.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    client = Client.query.get_or_404(id)

    if request.method == 'POST':
        client.name = request.form.get('name', client.name)
        client.email = request.form.get('email', client.email)
        client.phone = request.form.get('phone', client.phone)
        client.address = request.form.get('address', client.address)

        db.session.commit()
        flash("Client updated successfully.", "success")
        return redirect(url_for('routes.client_management'))

    return render_template('edit_client.html', client=client)


# Delete Client Route
@routes.route('/clients/delete/<int:id>', methods=['POST'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash(f"Client {client.name} deleted successfully.", "success")
    return redirect(url_for('routes.client_management'))


# Document Management Route (Handle file uploads)
@routes.route('/document_management', methods=['GET', 'POST'])
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
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace with actual user validation logic
        if username == "admin" and password == "password":  # Replace with hashed check
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('routes.home'))
        else:
            flash("Login failed. Check your credentials.", "danger")

    return render_template('login.html')  # Create this template file


# Logout Route
@routes.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('routes.home'))


# Custom Error Handlers
@routes.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@routes.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# Advanced Analytics Route
@routes.route('/advanced_analytics')
def advanced_analytics():
    total_shipments = Shipment.query.count()
    total_deals = Deal.query.count()
    total_properties = Property.query.count()
    total_vehicles = Vehicle.query.count()
    total_clients = Client.query.count()

    analytics_data = {
        "Total Shipments": total_shipments,
        "Total Deals": total_deals,
        "Total Properties": total_properties,
        "Total Vehicles": total_vehicles,
        "Total Clients": total_clients,
    }

    return render_template('advanced_analytics.html', analytics_data=analytics_data)  # Create this template file