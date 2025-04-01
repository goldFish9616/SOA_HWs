import grpc
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from concurrent import futures
import time
import requests

import promocodes.promocode_pb2 as promocode_pb2
import promocodes.promocode_pb2_grpc as promocode_pb2_grpc

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)
USER_SERVICE_URL = "http://user_service:5001"
channel = grpc.insecure_channel('promocode_service:5002') 
promocode_stub = promocode_pb2_grpc.PromocodeServiceStub(channel)

def verify_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{USER_SERVICE_URL}/verify", headers=headers)
    return response.status_code == 200

@app.route('/secure-endpoint', methods=['GET'])
def secure_endpoint():
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify({"message": "Access granted"}), 200


@app.route('/create_promocode', methods=['POST'])
@jwt_required()
def create_promocode():
    current_user = get_jwt_identity()

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    promocode_request = promocode_pb2.CreatePromocodeRequest(name=name, description=description)
    response = promocode_stub.CreatePromocode(promocode_request)

    return jsonify({
        'id': response.id,
        'name': response.name,
        'description': response.description
    }), 201

@app.route('/delete_promocode/<int:promocode_id>', methods=['DELETE'])
@jwt_required()
def delete_promocode(promocode_id):
    current_user = get_jwt_identity()

    promocode_request = promocode_pb2.DeletePromocodeRequest(id=promocode_id)
    response = promocode_stub.DeletePromocode(promocode_request)

    return jsonify({'message': 'Promocode deleted successfully'}), 200

@app.route('/update_promocode/<int:promocode_id>', methods=['PUT'])
@jwt_required()
def update_promocode(promocode_id):
    current_user = get_jwt_identity()

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    promocode_request = promocode_pb2.UpdatePromocodeRequest(id=promocode_id, name=name, description=description)
    response = promocode_stub.UpdatePromocode(promocode_request)

    return jsonify({
        'id': response.id,
        'name': response.name,
        'description': response.description
    }), 200

@app.route('/get_promocode/<int:promocode_id>', methods=['GET'])
@jwt_required()
def get_promocode(promocode_id):
    current_user = get_jwt_identity()

    promocode_request = promocode_pb2.GetPromocodeRequest(id=promocode_id)
    response = promocode_stub.GetPromocode(promocode_request)

    return jsonify({
        'id': response.id,
        'name': response.name,
        'description': response.description
    }), 200

@app.route('/list_promocodes', methods=['GET'])
@jwt_required()
def list_promocodes():
    current_user = get_jwt_identity()

    promocode_request = promocode_pb2.ListPromocodesRequest()
    response = promocode_stub.ListPromocodes(promocode_request)

    promocodes = [{'id': promo.id, 'name': promo.name, 'description': promo.description} for promo in response.promocodes]
    return jsonify(promocodes), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
