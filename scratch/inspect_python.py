import json
with open("data/processed/skills.json", "r", encoding="utf-8") as f:
    skills = json.load(f)

for s in skills:
    if s["skill_id"] == "SK_00240":
        print("SK_00240 detail:", s)
    if "python" in s["skill_name"].lower():
        print(f"Found Python skill: ID={s['skill_id']}, Name={s['skill_name']}, Norm={s.get('normalized_name')}")
