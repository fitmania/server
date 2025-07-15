from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

KEYWORDS = [
    "трансляция",
    "видеоконференция",
    "видеотрансляция",
    "светодиодный экран",
    "программно-техническое"
]

@app.route("/")
def home():
    return "Сервер работает. Перейди на /tenders для получения данных."

@app.route("/tenders")
def get_tenders():
    try:
        url = "https://goszakupki.by/tenders/posted"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []
        count = 0

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

            count += 1

        print(f"Найдено тендеров: {count}")
        return jsonify(results)

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
