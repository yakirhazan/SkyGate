from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import os
import logging
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(filename='/var/log/flask-app.log', level=logging.DEBUG)

# Initialize Azure Key Vault client
try:
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url="https://skygate-vault.vault.azure.net/", credential=credential)
    storage_connection_string = secret_client.get_secret("AzureStorageConnectionString").value
    function_url = secret_client.get_secret("AzureFunctionUrl").value
    pg_password = secret_client.get_secret("PostgresPassword").value
    xai_api_key = secret_client.get_secret("XaiApiKey").value
    logging.debug("Successfully retrieved secrets from Key Vault")
except Exception as e:
    logging.error(f"Failed to retrieve secrets from Key Vault: {e}")
    raise

# Initialize Azure Blob Storage client
try:
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    container_name = "consent-templates"
    logging.debug("Initialized Blob Storage client")
except Exception as e:
    logging.error(f"Failed to initialize Blob Storage client: {e}")
    raise

# Initialize PostgreSQL connection
try:
    pg_conn = psycopg2.connect(
        dbname="skygate",
        user="yakir",
        password=pg_password,
        host="skygate-pg.postgres.database.azure.com",
        port="5432"
    )
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklist (
            id SERIAL PRIMARY KEY,
            business_id VARCHAR(100) NOT NULL,
            task TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    pg_conn.commit()
    logging.debug("Connected to PostgreSQL and ensured checklist table")
except Exception as e:
    logging.error(f"Failed to connect to PostgreSQL: {e}")
    raise

@app.route('/api/audit', methods=['POST'])
def audit():
    try:
        data = request.get_json(silent=True)
        if not data or 'business_id' not in data or 'url' not in data:
            logging.error(f"Invalid audit payload: {request.data}")
            return jsonify({"error": "Missing business_id or url"}), 400
        
        business_id = data['business_id']
        url = data['url']
        
        logging.debug(f"Sending audit request for business_id: {business_id}, url: {url}")
        response = requests.post(function_url, json={"business_id": business_id, "url": url}, timeout=10)
        if response.status_code != 200:
            logging.error(f"Azure Function call failed: {response.text}")
            return jsonify({"error": "Audit failed"}), 500
        
        logging.info(f"Audit triggered for business_id: {business_id}, url: {url}")
        return jsonify({"message": "Audit triggered successfully"}), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logging.error(f"Audit error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/consent', methods=['POST'])
def consent():
    try:
        data = request.get_json(silent=True)
        if not data or 'business_id' not in data or 'template_json' not in data:
            logging.error(f"Invalid consent payload: {request.data}")
            return jsonify({"error": "Missing business_id or template_json"}), 400
        
        business_id = data['business_id']
        template_json = data['template_json']
        
        logging.debug(f"Uploading consent template for business_id: {business_id}")
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=f"{business_id}/consent.json"
        )
        blob_client.upload_blob(json.dumps(template_json), overwrite=True)
        
        logging.info(f"Consent template stored for business_id: {business_id}")
        return jsonify({"message": "Consent template stored successfully"}), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logging.error(f"Consent error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/checklist', methods=['POST'])
def add_checklist():
    try:
        data = request.get_json(silent=True)
        if not data or 'business_id' not in data or 'task' not in data:
            logging.error(f"Invalid checklist payload: {request.data}")
            return jsonify({"error": "Missing business_id or task"}), 400
        
        business_id = data['business_id']
        task = data['task']
        
        logging.debug(f"Adding checklist task for business_id: {business_id}")
        pg_cursor.execute(
            "INSERT INTO checklist (business_id, task) VALUES (%s, %s) RETURNING id;",
            (business_id, task)
        )
        task_id = pg_cursor.fetchone()[0]
        pg_conn.commit()
        
        logging.info(f"Checklist task added for business_id: {business_id}, task_id: {task_id}")
        return jsonify({"message": "Task added successfully", "task_id": task_id}), 200
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        pg_conn.rollback()
        logging.error(f"Checklist POST error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    try:
        business_id = request.args.get('business_id')
        if not business_id:
            logging.error("Missing business_id in GET request")
            return jsonify({"error": "Missing business_id"}), 400
        
        logging.debug(f"Retrieving checklist for business_id: {business_id}")
        pg_cursor.execute(
            "SELECT id, task, created_at FROM checklist WHERE business_id = %s ORDER BY created_at DESC;",
            (business_id,)
        )
        tasks = [{"id": row[0], "task": row[1], "created_at": row[2].isoformat()} for row in pg_cursor.fetchall()]
        
        logging.info(f"Checklist retrieved for business_id: {business_id}")
        return jsonify({"tasks": tasks}), 200
    except Exception as e:
        logging.error(f"Checklist GET error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
