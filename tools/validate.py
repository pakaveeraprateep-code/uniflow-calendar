#!/usr/bin/env python3
# ตรวจไฟล์ปฏิทินก่อนอัปขึ้น GitHub ด้วยกฎเดียวกับที่แอปใช้ (ไฟล์ไม่ผ่าน แอปจะไม่ใช้)
#   python3 tools/validate.py lru-regular.json
import json, sys, datetime

KINDS = {"termStart", "termBreak", "registration", "payment", "withdraw", "exam", "holiday", "makeup"}

def day(text):
    return datetime.date.fromisoformat(text)

def check(path):
    doc = json.load(open(path, encoding="utf8"))
    errors = []
    expected_id = path.rsplit("/", 1)[-1].removesuffix(".json")
    if doc.get("schema") != 1: errors.append("schema ต้องเป็น 1")
    if doc.get("id") != expected_id: errors.append(f"id ต้องตรงกับชื่อไฟล์ ({expected_id})")
    try: day(doc["updated"])
    except Exception: errors.append("updated ต้องเป็นวันที่แบบ 2026-10-16")
    events = doc.get("events", [])
    if not events or len(events) > 500: errors.append("events ต้องมี 1–500 รายการ")
    ids = [e.get("id") for e in events]
    if len(set(ids)) != len(ids): errors.append("id ของแต่ละรายการต้องไม่ซ้ำกัน")
    for e in events:
        name = e.get("id", "?")
        if e.get("kind") not in KINDS: print(f"  ⚠️ {name}: kind '{e.get('kind')}' แอปเวอร์ชันปัจจุบันไม่รู้จัก (จะถูกข้าม)")
        if not e.get("title") or len(e["title"]) > 120: errors.append(f"{name}: title ว่างหรือยาวเกิน 120 ตัว")
        if len(e.get("note") or "") > 200: errors.append(f"{name}: note ยาวเกิน 200 ตัว")
        try:
            s, t = day(e["start"]), day(e["end"])
            if s > t: errors.append(f"{name}: start อยู่หลัง end")
            if not 2020 <= s.year <= 2100: errors.append(f"{name}: ปีต้องเป็น ค.ศ. (2020–2100) ไม่ใช่ พ.ศ.")
        except Exception:
            errors.append(f"{name}: start/end ต้องเป็นวันที่ ค.ศ. แบบ 2026-11-02")
    return doc, errors

if __name__ == "__main__":
    ok = True
    for path in sys.argv[1:]:
        doc, errors = check(path)
        if errors:
            ok = False
            print(f"❌ {path}"); [print("  -", e) for e in errors]
        else:
            last = max(e["end"] for e in doc["events"])
            print(f"✅ {path}: {len(doc['events'])} รายการ, updated {doc['updated']}, มีข้อมูลถึง {last}")
    sys.exit(0 if ok else 1)
