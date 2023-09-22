from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return'<h1>This is your message tabs</h1>'


@app.route('/messages')
def messages():
    # Query for all messages, ordered by created_at in ascending order
    messages = Message.query.order_by(Message.created_at.asc()).all()

    # Create a list of message data as dictionaries
    message_list = [{"id": message.id, 
                     "username": message.username,
                     "content": message.body,
                     "created_at": message.created_at
                    } 
                     for message in messages]

    response = make_response(
        jsonify(message_list),
        200
    )
    response.headers["Content-Type"] = "application/json"

    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):

    message = Message.query.filter_by(id=id).first()
    message_serialized = message.to_dict()

    response = make_response(
        message_serialized,
        200
    )
    return response

@app.route('/messages', methods=['POST'])
def create_message():
    # Retrieve data from the request parameters
    body = request.form.get('body')
    username = request.form.get('username')

    # Create a new message object and add it to the database
    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()

    # Return the newly created message as JSON
    message_data = {
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at
    }

    # Create a custom response with the newly created message as JSON
    response = make_response(jsonify(message_data), 201)  # 201 Created status code

    return response


#How we do the patch request in this format
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # Retrieve data from the request parameters
    new_body = request.form.get('body')

    # Query for the message by ID
    message = Message.query.get(id)

    if message is None:
        return jsonify({"message": "Message not found"}), 404  # Custom status code for "Not Found"

    # Update the message's body
    message.body = new_body
    db.session.commit()

    # Return the updated message as JSON
    message_data = {
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at
    }

    # Create a custom response with the updated message as JSON
    response = make_response(jsonify(message_data))

    return response


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # Query for the message by ID
    message = Message.query.get(id)

    if message is None:
        return jsonify({"message": "Message not found"}), 404  # Custom status code for "Not Found"

    # Delete the message from the database
    db.session.delete(message)
    db.session.commit()

    # Return a JSON message confirming the deletion
    response_data = {"message": f"Message with ID {id} has been deleted."}

    # Create a custom response with the confirmation message as JSON
    response = make_response(jsonify(response_data))

    return response
if __name__ == '__main__':
    app.run(port=5555)
