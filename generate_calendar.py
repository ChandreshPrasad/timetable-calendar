import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid

LOGIN_URL = "https://www.ukm.my/smpweb/"
TIMETABLE_URL = "https://smplucee.ukm.my/smpweb/sx020form.cfm"

username = os.environ["UNI_USERNAME"]
password = os.environ["UNI_PASSWORD"]

session = requests.Session()

# --- FIX 1: Add headers to avoid bot rejection ---
headers = {
    "User-Agent": "Mozilla/5.0"
}

# --- FIX 2: Proper login payload (adjust if needed) ---
login_payload = {
    "username": username,
    "password": password
}

login_response = session.post(LOGIN_URL, data=login_payload, headers=headers)

# --- FIX 3: Validate login ---
if "login" in login_response.url.lower():
    raise Exception("Login failed - check credentials or form fields")

response = session.get(TIMETABLE_URL, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

# --- FIX 4: Target the correct table (adjust if needed) ---
table = soup.find("table")
rows = table.find_all("tr") if table else []

day_map = {
    "Isnin": 0,
    "Selasa": 1,
    "Rabu": 2,
    "Khamis": 3,
    "Jumaat": 4,
    "Sabtu": 5,
    "Ahad": 6
}

events = []
current_day = None

for row in rows[1:]:
    cells = [c.get_text(strip=True) for c in row.find_all("td")]

    if len(cells) < 7:
        continue

    hari, masa, biljam, kursus, tajuk, setkursus, bilik = cells

    if hari == "Rujuk Fakulti":
        continue

    if hari != "":
        current_day = hari

    if current_day not in day_map:
        continue

    # --- FIX 5: Robust time parsing ---
    try:
        if "-" in masa:
            start_raw = masa.split("-")[0].strip()
        else:
            start_raw = masa.strip()

        try:
    if "-" in masa:
        start_raw, end_raw = masa.split("-")
        start_raw = start_raw.strip().replace(".", ":")
        end_raw = end_raw.strip().replace(".", ":")
        
        start_time = datetime.strptime(start_raw, "%H:%M")
        end_time = datetime.strptime(end_raw, "%H:%M")
    else:
        continue
    print("ROW:", cells)


   
    events.append({
        "day": current_day,
        "course": f"{tajuk} ({kursus})",
        "room": bilik,
        "start": start_time,
        "end": end_time
    })

# --- DEBUG CHECK ---
if len(events) == 0:
    raise Exception("No events extracted - parsing failed")

def create_ics(events):

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Timetable Export//EN"
    ]

    base_date = datetime(2026, 4, 6)  # Monday reference

    for e in events:
        event_date = base_date + timedelta(days=day_map[e["day"]])

        start_dt = event_date.replace(
            hour=e["start"].hour,
            minute=e["start"].minute,
            second=0
        )

        end_dt = event_date.replace(
            hour=e["end"].hour,
            minute=e["end"].minute,
            second=0
        )

        uid = str(uuid.uuid4())

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{e['course']}",
            f"LOCATION:{e['room']}",
            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
            "RRULE:FREQ=WEEKLY",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")

    return "\n".join(lines)

ics = create_ics(events)

with open("timetable.ics", "w") as f:
    f.write(ics)
