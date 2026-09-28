import urllib.request
import json

def test_incident_api():
    base = "http://127.0.0.1:8000"
    
    # 1. Fetch incidents for SES-3F082779 or query database directly
    import sys
    sys.path.append("backend")
    from services.incident_manager import incident_manager
    from database.models import Incident
    from database.database import SessionLocal

    # Create a test incident
    created = incident_manager.create_incident(
        session_id="SES-3F082779",
        incident_type="FIRE",
        severity="CRITICAL",
        confidence=0.942,
        timestamp="00:43",
        details="Fire detected in Sector B"
    )
    inc_id = created["incident"]["id"]
    print(f"Created incident: {inc_id} with status {created['incident']['status']}")

    # 2. Acknowledge via PATCH HTTP
    req_ack = urllib.request.Request(f"{base}/api/incidents/{inc_id}/acknowledge", method="PATCH")
    with urllib.request.urlopen(req_ack) as res:
        ack_data = json.loads(res.read().decode('utf-8'))
        print(f"Acknowledged incident: status={ack_data['incident']['status']}")
        assert ack_data['incident']['status'] == "ACKNOWLEDGED"

    # 3. Resolve via PATCH HTTP
    req_res = urllib.request.Request(f"{base}/api/incidents/{inc_id}/resolve", method="PATCH")
    with urllib.request.urlopen(req_res) as res:
        res_data = json.loads(res.read().decode('utf-8'))
        print(f"Resolved incident: status={res_data['incident']['status']}")
        assert res_data['incident']['status'] == "RESOLVED"

    # 4. Fetch session incidents list
    req_list = urllib.request.Request(f"{base}/api/sessions/SES-3F082779/incidents")
    with urllib.request.urlopen(req_list) as res:
        all_inc = json.loads(res.read().decode('utf-8'))
        print(f"Session incidents count: {len(all_inc)}")

    print("INCIDENT LIFECYCLE TEST PASSED!")

if __name__ == "__main__":
    test_incident_api()
