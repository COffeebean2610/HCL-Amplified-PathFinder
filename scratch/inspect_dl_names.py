import json
with open("data/processed/skills.json", "r", encoding="utf-8") as f:
    skills = json.load(f)

for s in skills:
    if "deep learning" in s["skill_name"].lower():
        print(f"Found DL: ID={s['skill_id']}, Name={s['skill_name']}, Norm={s.get('normalized_name')}")
