import requests

base = "http://localhost:8000/api/evaluation"

print("=== Test Evaluation API ===")

# 1. 获取考核周期列表
r = requests.get(f"{base}/cycles")
print(f"\n1. Cycles: {r.status_code}")
if r.status_code == 200:
    cycles = r.json()
    print(f"   Found {len(cycles)} cycles")
    if cycles:
        print(f"   First: {cycles[0]['name']} (status={cycles[0]['status']})")

# 2. 获取统计
if cycles:
    cycle_id = cycles[0]['id']
    r = requests.get(f"{base}/stats/{cycle_id}")
    print(f"\n2. Stats for cycle {cycle_id}: {r.status_code}")
    if r.status_code == 200:
        print(f"   {r.json()}")

# 3. 获取我的任务
r = requests.get(f"{base}/my-tasks")
print(f"\n3. My tasks: {r.status_code}")
if r.status_code == 200:
    print(f"   {r.json()}")

print("\n=== Done ===")
