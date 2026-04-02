import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

LOGIN_URL = "https://www.ukm.my/smpweb/"
TIMETABLE_URL = "https://smplucee.ukm.my/smpweb/sx020form.cfm"

username = os.environ["UNI_USERNAME"]
password = os.environ["UNI_PASSWORD"]

session = requests.Session()

login_payload = {
    "username": username,
    "password": password
}

session.post(LOGIN_URL, data=login_payload)

response = session.get(TIMETABLE_URL)

soup = BeautifulSoup(response.text, "html.parser")

rows = soup.select("table tr")

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

    start_time = datetime.strptime(masa, "%I:%M %p")
    duration = int(biljam)
    end_time = start_time + timedelta(hours=duration)

    events.append({
        "day": current_day,
        "course": f"{tajuk} ({kursus})",
        "room": bilik,
        "start": start_time,
        "end": end_time
    })

def create_ics(events):

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Timetable Export//EN"
    ]

    for e in events:

        start_str = e["start"].strftime("%H%M%S")
        end_str = e["end"].strftime("%H%M%S")

        lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:{e['course']}",
            f"LOCATION:{e['room']}",
            f"DTSTART:20260406T{start_str}",
            f"DTEND:20260406T{end_str}",
            "RRULE:FREQ=WEEKLY",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")

    return "\n".join(lines)

ics = create_ics(events)

with open("timetable.ics", "w") as f:
    f.write(ics)
