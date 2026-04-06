from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://www.ukm.my/smpweb/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL)

    page.fill('input[name="username"]', "YOUR_USERNAME")
    page.fill('input[name="password"]', "YOUR_PASSWORD")

    page.click('input[type="submit"]')

    page.wait_for_load_state("networkidle")

    page.goto("https://smplucee.ukm.my/smpweb/sx020form.cfm")

    html = page.content()

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    rows = table.find_all("tr")

    for row in rows:
        print(row.text)

    browser.close()
