import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "YOUR_TIMETABLE_URL"

day_map = {
    "Isnin": 0,
    "Selasa": 1,
    "Rabu": 2,
    "Khamis": 3,
    "Jumaat": 4,
    "Sabtu": 5,
    "Ahad": 6
}

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.select("table tr")

events = []
current_day = None

for row in rows[1:]:
    cells = [c.get_text(strip=True) for c in row.find_all("td")]

    if len(cells) < 7:
        continue

    hari, masa, biljam, kursus, tajuk, setkursus, bilik = cells

    if hari != "":
        current_day = hari

    if current_day not in day_map:
        continue

    start_time = datetime.strptime(masa, "%I:%M %p")
    duration = int(biljam)
    end_time = start_time + timedelta(hours=duration)

    events.append({
        "day": current_day,
        "start": start_time,
        "end": end_time,
        "title": tajuk,
        "room": bilik
    })

def create_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0"
    ]

    for e in events:

        start_str = e["start"].strftime("%H%M%S")
        end_str = e["end"].strftime("%H%M%S")

        lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:{e['title']}",
            f"LOCATION:{e['room']}",
            f"DTSTART:20260406T{start_str}",
            f"DTEND:20260406T{end_str}",
            "RRULE:FREQ=WEEKLY",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    return "\n".join(lines)

with open("timetable.ics", "w") as f:
    f.write(create_ics(events))
