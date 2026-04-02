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

    # Skip faculty-referenced classes
    if hari == "Rujuk Fakulti":
        continue

    # Handle blank day cells
    if hari != "":
        current_day = hari

    if current_day not in day_map:
        continue

    try:
        start_time = datetime.strptime(masa, "%I:%M %p")
    except ValueError:
        continue

    try:
        duration = int(biljam)
    except ValueError:
        duration = 1

    end_time = start_time + timedelta(hours=duration)

    events.append({
        "day": current_day,
        "course_code": kursus,
        "title": tajuk,
        "room": bilik,
        "start": start_time,
        "end": end_time
    })


def create_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//University Timetable//EN"
    ]

    for e in events:

        start_str = e["start"].strftime("%H%M%S")
        end_str = e["end"].strftime("%H%M%S")

        summary = f"{e['title']} ({e['course_code']})"
        location = e["room"] if e["room"] else "TBA"

        lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:{summary}",
            f"LOCATION:{location}",
            f"DTSTART:20260406T{start_str}",
            f"DTEND:20260406T{end_str}",
            "RRULE:FREQ=WEEKLY",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


ics_content = create_ics(events)

with open("timetable.ics", "w") as f:
    f.write(ics_content)

print("timetable.ics generated successfully")
