import datetime as dt
import email.utils
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from html import unescape

RSS_SOURCES = [
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "BBC Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml"},
    {"name": "BBC Europe", "url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml"},
    {"name": "BBC US & Canada", "url": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"},
    {"name": "BBC Middle East", "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"},
    {"name": "BBC Africa", "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml"},
    {"name": "BBC Latin America", "url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml"}
]

COUNTRY_PATTERNS = {
    "US": [r"\bUnited States\b", r"\bU\.S\.\b", r"\bUS\b", r"\bAmerica\b"],
    "GB": [r"\bUnited Kingdom\b", r"\bBritain\b", r"\bEngland\b", r"\bUK\b"],
    "JP": [r"\bJapan\b", r"\bTokyo\b"],
    "CN": [r"\bChina\b", r"\bBeijing\b"],
    "KR": [r"\bSouth Korea\b", r"\bSeoul\b"],
    "KP": [r"\bNorth Korea\b", r"\bPyongyang\b"],
    "TW": [r"\bTaiwan\b", r"\bTaipei\b"],
    "IN": [r"\bIndia\b", r"\bNew Delhi\b"],
    "PK": [r"\bPakistan\b", r"\bIslamabad\b"],
    "BD": [r"\bBangladesh\b", r"\bDhaka\b"],
    "ID": [r"\bIndonesia\b", r"\bJakarta\b"],
    "TH": [r"\bThailand\b", r"\bBangkok\b"],
    "VN": [r"\bVietnam\b", r"\bHanoi\b"],
    "PH": [r"\bPhilippines\b", r"\bManila\b"],
    "MY": [r"\bMalaysia\b", r"\bKuala Lumpur\b"],
    "SG": [r"\bSingapore\b"],
    "AU": [r"\bAustralia\b", r"\bSydney\b", r"\bCanberra\b"],
    "NZ": [r"\bNew Zealand\b", r"\bWellington\b"],
    "RU": [r"\bRussia\b", r"\bMoscow\b"],
    "UA": [r"\bUkraine\b", r"\bKyiv\b"],
    "FR": [r"\bFrance\b", r"\bParis\b"],
    "DE": [r"\bGermany\b", r"\bBerlin\b"],
    "IT": [r"\bItaly\b", r"\bRome\b"],
    "ES": [r"\bSpain\b", r"\bMadrid\b"],
    "PT": [r"\bPortugal\b", r"\bLisbon\b"],
    "NL": [r"\bNetherlands\b", r"\bAmsterdam\b"],
    "BE": [r"\bBelgium\b", r"\bBrussels\b"],
    "PL": [r"\bPoland\b", r"\bWarsaw\b"],
    "SE": [r"\bSweden\b", r"\bStockholm\b"],
    "NO": [r"\bNorway\b", r"\bOslo\b"],
    "FI": [r"\bFinland\b", r"\bHelsinki\b"],
    "TR": [r"\bTurkey\b", r"\bTurkiye\b", r"\bAnkara\b", r"\bIstanbul\b"],
    "IL": [r"\bIsrael\b", r"\bJerusalem\b"],
    "PS": [r"\bGaza\b", r"\bWest Bank\b", r"\bPalestinian\b"],
    "SA": [r"\bSaudi Arabia\b", r"\bRiyadh\b"],
    "AE": [r"\bUAE\b", r"\bUnited Arab Emirates\b", r"\bDubai\b", r"\bAbu Dhabi\b"],
    "IR": [r"\bIran\b", r"\bTehran\b"],
    "IQ": [r"\bIraq\b", r"\bBaghdad\b"],
    "SY": [r"\bSyria\b", r"\bDamascus\b"],
    "EG": [r"\bEgypt\b", r"\bCairo\b"],
    "ZA": [r"\bSouth Africa\b", r"\bJohannesburg\b", r"\bCape Town\b"],
    "NG": [r"\bNigeria\b", r"\bAbuja\b", r"\bLagos\b"],
    "KE": [r"\bKenya\b", r"\bNairobi\b"],
    "ET": [r"\bEthiopia\b", r"\bAddis Ababa\b"],
    "SD": [r"\bSudan\b", r"\bKhartoum\b"],
    "DZ": [r"\bAlgeria\b", r"\bAlgiers\b"],
    "MA": [r"\bMorocco\b", r"\bRabat\b"],
    "MX": [r"\bMexico\b", r"\bMexico City\b"],
    "BR": [r"\bBrazil\b", r"\bBrasilia\b", r"\bSão Paulo\b", r"\bSao Paulo\b"],
    "AR": [r"\bArgentina\b", r"\bBuenos Aires\b"],
    "CL": [r"\bChile\b", r"\bSantiago\b"],
    "CO": [r"\bColombia\b", r"\bBogota\b", r"\bBogotá\b"],
    "PE": [r"\bPeru\b", r"\bLima\b"],
    "VE": [r"\bVenezuela\b", r"\bCaracas\b"],
    "CA": [r"\bCanada\b", r"\bOttawa\b", r"\bToronto\b"]
}

COUNTRY_NAMES = {
    "US": "United States", "GB": "United Kingdom", "JP": "Japan", "CN": "China", "KR": "South Korea",
    "KP": "North Korea", "TW": "Taiwan", "IN": "India", "PK": "Pakistan", "BD": "Bangladesh", "ID": "Indonesia",
    "TH": "Thailand", "VN": "Vietnam", "PH": "Philippines", "MY": "Malaysia", "SG": "Singapore", "AU": "Australia",
    "NZ": "New Zealand", "RU": "Russia", "UA": "Ukraine", "FR": "France", "DE": "Germany", "IT": "Italy",
    "ES": "Spain", "PT": "Portugal", "NL": "Netherlands", "BE": "Belgium", "PL": "Poland", "SE": "Sweden",
    "NO": "Norway", "FI": "Finland", "TR": "Turkey", "IL": "Israel", "PS": "Palestine", "SA": "Saudi Arabia",
    "AE": "United Arab Emirates", "IR": "Iran", "IQ": "Iraq", "SY": "Syria", "EG": "Egypt", "ZA": "South Africa",
    "NG": "Nigeria", "KE": "Kenya", "ET": "Ethiopia", "SD": "Sudan", "DZ": "Algeria", "MA": "Morocco",
    "MX": "Mexico", "BR": "Brazil", "AR": "Argentina", "CL": "Chile", "CO": "Colombia", "PE": "Peru",
    "VE": "Venezuela", "CA": "Canada"
}

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def http_get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "world-news-map-bot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode("utf-8", errors="ignore")


def clean_text(value: str) -> str:
    value = unescape(value or "")
    value = HTML_TAG_RE.sub(" ", value)
    value = WHITESPACE_RE.sub(" ", value).strip()
    return value


def parse_pub_date(value: str) -> str:
    if not value:
        return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    try:
        parsed = email.utils.parsedate_to_datetime(value)
        return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except Exception:
        return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def detect_country(text: str) -> str | None:
    for code, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return code
    return None


def build_summary(description: str, title: str) -> str:
    base = clean_text(description) or clean_text(title)
    return base[:140] + ("…" if len(base) > 140 else "")


def parse_rss(source: dict) -> list[dict]:
    xml_text = http_get_text(source["url"])
    root = ET.fromstring(xml_text)
    articles = []

    for item in root.findall(".//item")[:30]:
        title = clean_text(item.findtext("title", default=""))
        link = clean_text(item.findtext("link", default=""))
        description = clean_text(item.findtext("description", default=""))
        pub_date = parse_pub_date(item.findtext("pubDate", default=""))
        body = f"{title} {description}"
        country_code = detect_country(body)
        if not country_code:
            continue

        articles.append({
            "source": source["name"],
            "title": title,
            "url": link,
            "summary": build_summary(description, title),
            "published_at": pub_date,
            "country_code": country_code,
            "country_name": COUNTRY_NAMES[country_code]
        })

    return articles


def dedupe_articles(articles: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for article in sorted(articles, key=lambda x: x["published_at"], reverse=True):
        key = (article["title"].lower(), article["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def main() -> None:
    all_articles = []
    for source in RSS_SOURCES:
        try:
            all_articles.extend(parse_rss(source))
        except Exception as ex:
            print(f"WARN: failed to parse {source['name']}: {ex}")

    articles = dedupe_articles(all_articles)
    counts = Counter(article["country_code"] for article in articles)
    regions = [
        {
            "country_code": code,
            "country_name": COUNTRY_NAMES.get(code, code),
            "news_count": counts[code]
        }
        for code in sorted(counts.keys(), key=lambda c: (-counts[c], c))
    ]

    output = {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "articles": articles,
        "regions": regions
    }

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
