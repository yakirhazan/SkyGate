import azure.functions as func
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        business_id = data.get('business_id')
        url = data.get('url')

        if not business_id or not url:
            return func.HttpResponse(
                json.dumps({"error": "Missing business_id or url"}),
                status_code=400,
                mimetype="application/json"
            )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        issues = []
        if not soup.find(text=lambda t: 'cookie' in t.lower() and 'consent' in t.lower()):
            issues.append('Missing GDPR-compliant cookie consent banner')

        return func.HttpResponse(
            json.dumps({"audit_date": datetime.now().isoformat(), "issues": issues}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Audit failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
