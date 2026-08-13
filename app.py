#!/usr/bin/env python3
"""
Test HTTP service with Basic Authentication & Lead Source Database
For testing DocuSign Workflow Builder's "Make a Web Request" step
Includes Lead/Representative database with CRUD operations
"""

from flask import Flask, request, jsonify
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)

# Test credentials
VALID_USERNAME = "docusign_test"
VALID_PASSWORD = "test_password_123"

# In-memory leads database (simulates a database)
leads_db = {
    "LEAD001": {
        "id": "HCAP",
        "lead_source": "HCAP",
        "rep_first_name": "John",
        "rep_last_name": "Smith",
        "rep_number": "REP001",
        "rep_street_address": "123 Main Street, Suite 100",
        "company_name": "HCAP Financial Group",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "phone": "(212) 555-1001",
        "fax": "(212) 555-1002",
        "email": "john.smith@hcapgroup.com",
        "created_at": "2024-01-10T08:00:00Z"
    },
    "LEAD003": {
        "id": "JTF",
        "lead_source": "JTF",
        "rep_first_name": "Michael",
        "rep_last_name": "Davis",
        "rep_number": "REP003",
        "rep_street_address": "789 Market Street, Suite 200",
        "company_name": "JTF Ventures",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "phone": "(415) 555-3001",
        "fax": "(415) 555-3002",
        "email": "michael.davis@jtfventures.com",
        "created_at": "2024-01-15T10:15:00Z"
    },
    "LEAD005": {
        "id": "LOUD",
        "lead_source": "LOUD",
        "rep_first_name": "Robert",
        "rep_last_name": "Wilson",
        "rep_number": "REP005",
        "rep_street_address": "555 North Michigan Avenue, Suite 400",
        "company_name": "LOUD Investments LLC",
        "city": "Chicago",
        "state": "IL",
        "zip": "60611",
        "phone": "(312) 555-5001",
        "fax": "(312) 555-5002",
        "email": "robert.wilson@loudinvest.com",
        "created_at": "2024-01-20T13:00:00Z"
    }    
}

def check_auth(username, password):
    """Check if username and password are valid."""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def authenticate(f):
    """Decorator for routes requiring Basic Auth."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization

        if not auth:
            return jsonify({
                "error": "Missing Authorization header",
                "message": "Please provide Basic Authentication credentials"
            }), 401

        if not check_auth(auth.username, auth.password):
            return jsonify({
                "error": "Invalid credentials",
                "message": f"Authentication failed for username: {auth.username}"
            }), 401

        return f(*args, **kwargs)

    return decorated_function

# ============= PUBLIC ENDPOINTS (No Auth) =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no auth required)."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DocuSign Workflow Test Service with Lead Source Database"
    }), 200

@app.route('/api/credentials', methods=['GET'])
def get_credentials():
    """Get test credentials (no auth required - informational only)."""
    return jsonify({
        "credentials": {
            "username": VALID_USERNAME,
            "password": VALID_PASSWORD
        },
        "note": "Use these credentials for Basic Auth in DocuSign Workflow Builder",
        "endpoints": {
            "health_check": "GET /health",
            "info": "GET /api/info",
            "leads_all": "GET /api/leads (requires auth)",
            "leads_by_source": "GET /api/leads?source={HCAP|JTF|LOUD} (requires auth)",
            "lead_by_id": "GET /api/leads/{id} (requires auth)",
            "create_lead": "POST /api/leads (requires auth)",
            "update_lead": "PUT /api/leads/{id} (requires auth)",
            "delete_lead": "DELETE /api/leads/{id} (requires auth)"
        }
    }), 200

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information."""
    return jsonify({
        "service": "DocuSign Workflow Test Service",
        "version": "3.0",
        "description": "HTTP service with Basic Auth for testing Workflow Builder",
        "features": [
            "Basic Authentication",
            "Lead Source database with CRUD operations",
            "Filter by Lead Source (HCAP, JTF, LOUD)",
            "Representative information management",
            "Sample data included",
            "JSON request/response"
        ],
        "auth_required": "Most endpoints require Basic Auth (docusign_test / test_password_123)",
        "base_url": request.base_url.rstrip('/'),
        "database": {
            "type": "In-memory",
            "table": "leads",
            "total_records": len(leads_db),
            "lead_sources": ["HCAP", "JTF", "LOUD"],
            "fields": [
                "id", "lead_source", "rep_first_name", "rep_last_name",
                "rep_number", "rep_street_address", "company_name",
                "city", "state", "zip", "phone", "fax", "email", "created_at"
            ]
        }
    }), 200

# ============= LEAD ENDPOINTS (With Auth) =============

@app.route('/api/leads', methods=['GET'])
@authenticate
def get_leads():
    """Get leads - optionally filtered by lead source (requires auth)."""
    lead_source = request.args.get('source', '').upper()

    if lead_source:
        if lead_source not in ["HCAP", "JTF", "LOUD"]:
            return jsonify({
                "status": "error",
                "error": "Invalid Lead Source",
                "message": f"Lead source '{lead_source}' is not valid",
                "valid_sources": ["HCAP", "JTF", "LOUD"]
            }), 400

        filtered_leads = [
            lead for lead in leads_db.values()
            if lead['lead_source'] == lead_source
        ]
        return jsonify({
            "status": "success",
            "message": f"Retrieved {len(filtered_leads)} leads from source {lead_source}",
            "timestamp": datetime.utcnow().isoformat(),
            "authenticated_user": request.authorization.username,
            "source_filter": lead_source,
            "count": len(filtered_leads),
            "data": filtered_leads
        }), 200
    else:
        leads_list = list(leads_db.values())
        return jsonify({
            "status": "success",
            "message": f"Retrieved {len(leads_list)} total leads",
            "timestamp": datetime.utcnow().isoformat(),
            "authenticated_user": request.authorization.username,
            "count": len(leads_list),
            "data": leads_list
        }), 200

@app.route('/api/leads/<string:lead_id>', methods=['GET'])
@authenticate
def get_lead_by_id(lead_id):
    """Get specific lead by ID (requires auth)."""
    lead_id_upper = lead_id.upper()

    if lead_id_upper not in leads_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Lead with ID '{lead_id}' not found",
            "timestamp": datetime.utcnow().isoformat(),
            "authenticated_user": request.authorization.username,
            "available_ids": list(leads_db.keys())
        }), 404

    lead = leads_db[lead_id_upper]
    return jsonify({
        "status": "success",
        "message": "Lead retrieved successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": lead
    }), 200

@app.route('/api/leads', methods=['POST'])
@authenticate
def create_lead():
    """Create a new lead (requires auth)."""
    if not request.is_json:
        return jsonify({
            "status": "error",
            "error": "Invalid Content-Type",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()

    # Validate required fields
    required_fields = [
        'lead_source', 'rep_first_name', 'rep_last_name', 'rep_number',
        'company_name', 'city', 'state', 'zip', 'phone', 'email'
    ]
    missing_fields = [f for f in required_fields if f not in data or not data[f]]

    if missing_fields:
        return jsonify({
            "status": "error",
            "error": "Missing Fields",
            "message": f"Required fields missing: {', '.join(missing_fields)}",
            "required_fields": required_fields,
            "optional_fields": ["rep_street_address", "fax"]
        }), 400

    # Validate lead source
    if data['lead_source'].upper() not in ["HCAP", "JTF", "LOUD"]:
        return jsonify({
            "status": "error",
            "error": "Invalid Lead Source",
            "message": f"Lead source must be HCAP, JTF, or LOUD",
            "valid_sources": ["HCAP", "JTF", "LOUD"]
        }), 400

    # Generate ID
    lead_id = f"LEAD{len(leads_db) + 1:03d}"

    # Check if ID already exists
    if lead_id in leads_db:
        return jsonify({
            "status": "error",
            "error": "Conflict",
            "message": f"Lead ID {lead_id} already exists"
        }), 409

    # Create new lead record
    new_lead = {
        "id": lead_id,
        "lead_source": data['lead_source'].upper(),
        "rep_first_name": data['rep_first_name'],
        "rep_last_name": data['rep_last_name'],
        "rep_number": data['rep_number'],
        "rep_street_address": data.get('rep_street_address', ''),
        "company_name": data['company_name'],
        "city": data['city'],
        "state": data['state'],
        "zip": data['zip'],
        "phone": data['phone'],
        "fax": data.get('fax', ''),
        "email": data['email'],
        "created_at": datetime.utcnow().isoformat()
    }

    leads_db[lead_id] = new_lead

    return jsonify({
        "status": "success",
        "message": "Lead created successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": new_lead
    }), 201

@app.route('/api/leads/<string:lead_id>', methods=['PUT'])
@authenticate
def update_lead(lead_id):
    """Update an existing lead (requires auth)."""
    lead_id_upper = lead_id.upper()

    if lead_id_upper not in leads_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Lead with ID '{lead_id}' not found",
            "available_ids": list(leads_db.keys())
        }), 404

    if not request.is_json:
        return jsonify({
            "status": "error",
            "error": "Invalid Content-Type",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()
    lead = leads_db[lead_id_upper]

    # Update allowed fields
    updatable_fields = [
        'lead_source', 'rep_first_name', 'rep_last_name', 'rep_number',
        'rep_street_address', 'company_name', 'city', 'state', 'zip',
        'phone', 'fax', 'email'
    ]

    for field in updatable_fields:
        if field in data and data[field] is not None:
            if field == 'lead_source':
                source = data[field].upper()
                if source not in ["HCAP", "JTF", "LOUD"]:
                    return jsonify({
                        "status": "error",
                        "error": "Invalid Lead Source",
                        "message": f"Lead source must be HCAP, JTF, or LOUD"
                    }), 400
                lead[field] = source
            else:
                lead[field] = data[field]

    # Always update timestamp
    lead['updated_at'] = datetime.utcnow().isoformat()

    return jsonify({
        "status": "success",
        "message": "Lead updated successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": lead
    }), 200

@app.route('/api/leads/<string:lead_id>', methods=['DELETE'])
@authenticate
def delete_lead(lead_id):
    """Delete a lead (requires auth)."""
    lead_id_upper = lead_id.upper()

    if lead_id_upper not in leads_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Lead with ID '{lead_id}' not found",
            "available_ids": list(leads_db.keys())
        }), 404

    lead = leads_db[lead_id_upper]
    del leads_db[lead_id_upper]

    return jsonify({
        "status": "success",
        "message": "Lead deleted successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "deleted_lead": lead,
        "remaining_leads": len(leads_db)
    }), 200

# ============= SEARCH & FILTER ENDPOINTS =============

@app.route('/api/leads/search/by-name', methods=['GET'])
@authenticate
def search_leads_by_name():
    """Search leads by representative name (requires auth)."""
    name_query = request.args.get('q', '').lower()

    if not name_query:
        return jsonify({
            "status": "error",
            "error": "Missing Parameter",
            "message": "Query parameter 'q' is required",
            "example": "/api/leads/search/by-name?q=smith"
        }), 400

    matching_leads = [
        lead for lead in leads_db.values()
        if (name_query in lead['rep_first_name'].lower() or
            name_query in lead['rep_last_name'].lower() or
            name_query in lead['company_name'].lower())
    ]

    return jsonify({
        "status": "success",
        "message": f"Found {len(matching_leads)} leads matching '{name_query}'",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "query": name_query,
        "count": len(matching_leads),
        "data": matching_leads
    }), 200

@app.route('/api/leads/search/by-city', methods=['GET'])
@authenticate
def search_leads_by_city():
    """Search leads by city (requires auth)."""
    city_query = request.args.get('q', '').lower()

    if not city_query:
        return jsonify({
            "status": "error",
            "error": "Missing Parameter",
            "message": "Query parameter 'q' is required",
            "example": "/api/leads/search/by-city?q=chicago"
        }), 400

    matching_leads = [
        lead for lead in leads_db.values()
        if city_query in lead['city'].lower()
    ]

    return jsonify({
        "status": "success",
        "message": f"Found {len(matching_leads)} leads in '{city_query}'",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "city_query": city_query,
        "count": len(matching_leads),
        "data": matching_leads
    }), 200

# ============= STATISTICS ENDPOINTS =============

@app.route('/api/stats', methods=['GET'])
@authenticate
def get_stats():
    """Get database statistics (requires auth)."""
    if not leads_db:
        source_breakdown = {}
    else:
        source_breakdown = {}
        for lead in leads_db.values():
            source = lead['lead_source']
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

    # Count by state
    state_breakdown = {}
    for lead in leads_db.values():
        state = lead['state']
        state_breakdown[state] = state_breakdown.get(state, 0) + 1

    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "statistics": {
            "total_leads": len(leads_db),
            "leads_by_source": source_breakdown,
            "leads_by_state": state_breakdown,
            "available_sources": ["HCAP", "JTF", "LOUD"]
        }
    }), 200

@app.route('/api/reset', methods=['POST'])
@authenticate
def reset_database():
    """Reset database to initial state (requires auth)."""
    global leads_db

    initial_leads = {
        "LEAD001": {
            "id": "LEAD001",
            "lead_source": "HCAP",
            "rep_first_name": "John",
            "rep_last_name": "Smith",
            "rep_number": "REP001",
            "rep_street_address": "123 Main Street, Suite 100",
            "company_name": "HCAP Financial Group",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "phone": "(212) 555-1001",
            "fax": "(212) 555-1002",
            "email": "john.smith@hcapgroup.com",
            "created_at": "2024-01-10T08:00:00Z"
        },
        "LEAD002": {
            "id": "LEAD002",
            "lead_source": "HCAP",
            "rep_first_name": "Sarah",
            "rep_last_name": "Johnson",
            "rep_number": "REP002",
            "rep_street_address": "456 Park Avenue, Floor 15",
            "company_name": "HCAP Capital Partners",
            "city": "New York",
            "state": "NY",
            "zip": "10022",
            "phone": "(212) 555-2001",
            "fax": "(212) 555-2002",
            "email": "sarah.johnson@hcapgroup.com",
            "created_at": "2024-01-12T09:30:00Z"
        },
        "LEAD003": {
            "id": "LEAD003",
            "lead_source": "JTF",
            "rep_first_name": "Michael",
            "rep_last_name": "Davis",
            "rep_number": "REP003",
            "rep_street_address": "789 Market Street, Suite 200",
            "company_name": "JTF Ventures",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102",
            "phone": "(415) 555-3001",
            "fax": "(415) 555-3002",
            "email": "michael.davis@jtfventures.com",
            "created_at": "2024-01-15T10:15:00Z"
        },
        "LEAD004": {
            "id": "LEAD004",
            "lead_source": "JTF",
            "rep_first_name": "Emily",
            "rep_last_name": "Chen",
            "rep_number": "REP004",
            "rep_street_address": "321 Geary Street, Suite 300",
            "company_name": "JTF Capital Management",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94108",
            "phone": "(415) 555-4001",
            "fax": "(415) 555-4002",
            "email": "emily.chen@jtfventures.com",
            "created_at": "2024-01-18T11:45:00Z"
        },
        "LEAD005": {
            "id": "LEAD005",
            "lead_source": "LOUD",
            "rep_first_name": "Robert",
            "rep_last_name": "Wilson",
            "rep_number": "REP005",
            "rep_street_address": "555 North Michigan Avenue, Suite 400",
            "company_name": "LOUD Investments LLC",
            "city": "Chicago",
            "state": "IL",
            "zip": "60611",
            "phone": "(312) 555-5001",
            "fax": "(312) 555-5002",
            "email": "robert.wilson@loudinvest.com",
            "created_at": "2024-01-20T13:00:00Z"
        },
        "LEAD006": {
            "id": "LEAD006",
            "lead_source": "LOUD",
            "rep_first_name": "Lisa",
            "rep_last_name": "Martinez",
            "rep_number": "REP006",
            "rep_street_address": "888 South Wabash Avenue, Suite 500",
            "company_name": "LOUD Capital Group",
            "city": "Chicago",
            "state": "IL",
            "zip": "60605",
            "phone": "(312) 555-6001",
            "fax": "(312) 555-6002",
            "email": "lisa.martinez@loudinvest.com",
            "created_at": "2024-01-22T14:30:00Z"
        }
    }

    leads_db = initial_leads

    return jsonify({
        "status": "success",
        "message": "Database reset to initial state",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "leads_restored": len(leads_db)
    }), 200

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "path": request.path,
        "method": request.method,
        "available_endpoints": {
            "health": "GET /health",
            "info": "GET /api/info",
            "credentials": "GET /api/credentials",
            "leads_all": "GET /api/leads (auth required)",
            "leads_by_source": "GET /api/leads?source=HCAP|JTF|LOUD (auth required)",
            "lead_by_id": "GET /api/leads/{id} (auth required)",
            "create_lead": "POST /api/leads (auth required)",
            "update_lead": "PUT /api/leads/{id} (auth required)",
            "delete_lead": "DELETE /api/leads/{id} (auth required)",
            "search_by_name": "GET /api/leads/search/by-name?q=query (auth required)",
            "search_by_city": "GET /api/leads/search/by-city?q=query (auth required)",
            "stats": "GET /api/stats (auth required)",
            "reset": "POST /api/reset (auth required)"
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    print("\n" + "="*70)
    print("TEST HTTP SERVICE - DocuSign Workflow Builder with Lead Database")
    print("="*70)
    print("\nTest Credentials:")
    print(f"  Username: {VALID_USERNAME}")
    print(f"  Password: {VALID_PASSWORD}")
    print("\n" + "-"*70)
    print("PUBLIC ENDPOINTS (No Auth Required):")
    print("-"*70)
    print("  GET  /health                          - Service health check")
    print("  GET  /api/info                        - API information")
    print("  GET  /api/credentials                 - Show test credentials")
    print("\n" + "-"*70)
    print("LEAD CRUD ENDPOINTS (Auth Required):")
    print("-"*70)
    print("  GET  /api/leads                       - Get all leads")
    print("  GET  /api/leads?source=HCAP|JTF|LOUD - Get leads by source")
    print("  GET  /api/leads/{id}                  - Get lead by ID")
    print("  POST /api/leads                       - Create new lead")
    print("  PUT  /api/leads/{id}                  - Update lead")
    print("  DELETE /api/leads/{id}                - Delete lead")
    print("\n" + "-"*70)
    print("SEARCH & FILTER (Auth Required):")
    print("-"*70)
    print("  GET  /api/leads/search/by-name?q=term - Search by rep name")
    print("  GET  /api/leads/search/by-city?q=term - Search by city")
    print("  GET  /api/stats                       - Database statistics")
    print("  POST /api/reset                       - Reset to initial data")
    print("\n" + "-"*70)
    print("Lead Sources: HCAP, JTF, LOUD")
    print("-"*70)
    print("\nUsage in DocuSign Workflow Builder:")
    print("  1. Add 'Make a Web Request' step")
    print("  2. Set URL: https://your-public-url/api/leads?source=HCAP")
    print("  3. Set Method: GET")
    print("  4. Authentication Type: Basic Authentication")
    print(f"  5. Username: {VALID_USERNAME}")
    print(f"  6. Password: {VALID_PASSWORD}")
    print("\n" + "="*70)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("="*70 + "\n")

    app.run(debug=False, host='0.0.0.0', port=port)
