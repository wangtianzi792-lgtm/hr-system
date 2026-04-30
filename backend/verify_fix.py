import requests
r = requests.get('http://localhost:8000/api/employees?page=1&page_size=3')
data = r.json()
print('Status:', r.status_code)
for e in data['items']:
    print(f"{e['name']}: gender={e['gender']}, age={e['age']}, work_years={e['work_years']}, medical={e['medical_exam_type']}")
