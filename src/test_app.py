import pytest
from flask import Flask, jsonify, request
import logging

# Simulando um servidor Flask para testes
app = Flask(__name__)

activities = {
    "Yoga": {
        "description": "A relaxing yoga session.",
        "schedule": "Monday 6 PM",
        "max_participants": 10,
        "participants": ["test@example.com"]
    }
}

@app.route('/activities', methods=['GET'])
def get_activities():
    return jsonify(activities)

@app.route('/activities/<activity>/signup', methods=['POST'])
def signup_activity(activity):
    email = request.args.get('email')
    if activity in activities and len(activities[activity]["participants"]) < activities[activity]["max_participants"]:
        activities[activity]["participants"].append(email)
        return jsonify({"message": "Signup successful"}), 200
    return jsonify({"detail": "Activity full or not found"}), 400

@app.route('/activities/<activity>/cancel', methods=['DELETE'])
def cancel_activity(activity):
    email = request.args.get('email')
    if activity in activities and email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
        return jsonify({"message": "Signup canceled"}), 200
    return jsonify({"detail": "Participant not found"}), 400

# Testes com pytest
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajustando o teste para verificar o conteúdo correto do HTML

def test_root_redirection():
    logger.info("Testando redirecionamento da raiz")
    response = client.get("/")
    assert response.status_code == 200
    logger.info("Status code correto")
    assert "<!DOCTYPE html>" in response.text  # Verifica o início do HTML
    logger.info("HTML inicial correto")
    assert "<html lang=\"en\">" in response.text  # Verifica a tag <html> com atributo lang
    assert "<head>" in response.text  # Verifica a presença da tag <head>
    assert "<body>" in response.text  # Verifica a presença da tag <body>

# Test getting activities
def test_get_activities():
    logger.info("Testando obtenção de atividades")
    response = client.get("/activities")
    assert response.status_code == 200
    logger.info("Status code correto")
    assert isinstance(response.json(), dict)
    logger.info("Resposta é um dicionário")
    assert "Chess Club" in response.json()

# Test signing up for an activity
def test_signup_for_activity_success():
    logger.info("Testando inscrição bem-sucedida em uma atividade")
    response = client.post("/activities/Chess Club/signup", params={"email": "newuser@mergington.edu"})
    assert response.status_code == 200
    logger.info("Status code correto")
    assert response.json()["message"] == "Signed up newuser@mergington.edu for Chess Club"

def test_signup_for_nonexistent_activity():
    logger.info("Testando inscrição em uma atividade inexistente")
    response = client.post("/activities/Nonexistent/signup", params={"email": "newuser@mergington.edu"})
    assert response.status_code == 404
    logger.info("Status code correto")
    assert response.json()["detail"] == "Activity not found"

def test_signup_for_activity_already_signed_up():
    logger.info("Testando inscrição duplicada em uma atividade")
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert response.status_code == 400
    logger.info("Status code correto")
    assert response.json()["detail"] == "Student is already signed up for this activity"

# Test canceling an activity
def test_cancel_activity_success():
    logger.info("Testando cancelamento bem-sucedido de inscrição")
    response = client.delete("/activities/Chess Club/cancel", params={"email": "michael@mergington.edu"})
    assert response.status_code == 200
    logger.info("Status code correto")
    assert response.json()["message"] == "Canceled enrollment of michael@mergington.edu from Chess Club"

def test_cancel_nonexistent_activity():
    logger.info("Testando cancelamento de uma atividade inexistente")
    response = client.delete("/activities/Nonexistent/cancel", params={"email": "michael@mergington.edu"})
    assert response.status_code == 404
    logger.info("Status code correto")
    assert response.json()["detail"] == "Activity not found"

def test_cancel_activity_not_signed_up():
    logger.info("Testando cancelamento de inscrição não existente")
    response = client.delete("/activities/Chess Club/cancel", params={"email": "not_signed_up@mergington.edu"})
    assert response.status_code == 400
    logger.info("Status code correto")
    assert response.json()["detail"] == "Student is not signed up for this activity"

def test_edit_email_success():
    logger.info("Testando atualização de email bem-sucedida")
    response = client.put(
        "/activities/Chess Club/edit-email",
        json={"old_email": "michael@mergington.edu", "new_email": "newmichael@mergington.edu"}
    )
    assert response.status_code == 200
    logger.info("Status code correto")
    assert response.json()["message"] == "Updated email from michael@mergington.edu to newmichael@mergington.edu for Chess Club"

def test_edit_email_activity_not_found():
    logger.info("Testando atualização de email para uma atividade inexistente")
    response = client.put(
        "/activities/Nonexistent/edit-email",
        json={"old_email": "michael@mergington.edu", "new_email": "newmichael@mergington.edu"}
    )
    assert response.status_code == 404
    logger.info("Status code correto")
    assert response.json()["detail"] == "Activity not found"

def test_edit_email_old_email_not_found():
    logger.info("Testando atualização de email com email antigo não encontrado")
    response = client.put(
        "/activities/Chess Club/edit-email",
        json={"old_email": "notfound@mergington.edu", "new_email": "newmichael@mergington.edu"}
    )
    assert response.status_code == 400
    logger.info("Status code correto")
    assert response.json()["detail"] == "Old email not found in participants"

def test_edit_email_new_email_already_participant():
    logger.info("Testando atualização de email com novo email já participante")
    response = client.put(
        "/activities/Chess Club/edit-email",
        json={"old_email": "michael@mergington.edu", "new_email": "daniel@mergington.edu"}
    )
    assert response.status_code == 400
    logger.info("Status code correto")
    assert response.json()["detail"] == "New email is already a participant"