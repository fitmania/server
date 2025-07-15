from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

KEYWORDS = [
    "видеоконференция"
]

@app.route("/tenders")
def get_tenders():
    url = "https://goszakupki.by/tenders/posted"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for block in soup.select(".purchase-card__wrapper"):
        title_el = block.select_one(".purchase-card__title")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        full_url = "https://goszakupki.by" + href

        if not any(kw in title.lower() for kw in KEYWORDS):
            continue

        customer_el = block.select_one(".purchase-card__customers")
        deadline_el = block.select_one(".purchase-card__deadline-date")
        price_el = block.select_one(".purchase-card__sum")

        results.append({
            "title": title,
            "url": full_url,
            "customer": customer_el.get_text(strip=True) if customer_el else "",
            "deadline": deadline_el.get_text(strip=True) if deadline_el else "",
            "price": price_el.get_text(strip=True) if price_el else ""
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
