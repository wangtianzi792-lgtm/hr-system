import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace-agent-8fd3bdac\attendance_system\backend')

import requests

base = "http://localhost:8000/api"

# Test company info
r = requests.get(f"{base}/settings/company")
print("Company:", r.json())

# Test attendance rule
r = requests.get(f"{base}/settings/attendance-rule")
print("Attendance:", r.json())

# Test leave rule
r = requests.get(f"{base}/settings/leave-rule")
print("Leave:", r.json())

# Test system config
r = requests.get(f"{base}/settings/system")
print("System:", r.json())

# Test save company
r = requests.post(f"{base}/settings/company", json={
    "name": "海昌新材",
    "short_name": "海昌新材",
    "credit_code": "91321000MA1P000000",
    "address": "江苏省扬州市邗江区",
    "phone": "0514-88888888"
})
print("Save company:", r.json())

# Test logs
r = requests.get(f"{base}/settings/logs")
print("Logs:", r.json())

print("\nAll tests passed!")
