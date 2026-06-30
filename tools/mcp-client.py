#!/usr/bin/env python3
"""
MiroFish — MCP Adapter: Cari data real-time dari web
Menggunakan DuckDuckGo, RSS, dan wttr.in (semua gratis, tanpa API key).
MiroFish agents bisa cari info terbaru buat simulasi lebih akurat.
"""

import os
import sys
import json
import re
import urllib.parse
from pathlib import Path


def search_web(query: str, max_results: int = 5) -> dict:
    """Cari di web via Google News RSS + scraping (free, tanpa API key)."""
    results = []
    
    # Metode 1: Google News RSS
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
        
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=id&gl=ID"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode('utf-8', errors='ignore')
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        for item in items[:max_results]:
            results.append({
                "title": item.findtext('title', ''),
                "link": item.findtext('link', ''),
                "snippet": item.findtext('description', '')[:300],
                "date": item.findtext('pubDate', '')[:16],
                "source": "Google News"
            })
    except:
        pass
    
    if results:
        return {
            "success": True, "query": query,
            "results": results, "count": len(results),
            "source": "Google News RSS"
        }
    
    # Metode 2: DuckDuckGo (jika terinstal)
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get('title', ''),
                    "link": r.get('href', ''),
                    "snippet": r.get('body', '')[:300],
                    "source": "DuckDuckGo"
                })
    except:
        pass
    
    return {
        "success": bool(results),
        "query": query,
        "results": results,
        "count": len(results),
        "source": "Mixed sources"
    }


def search_news(query: str, max_results: int = 5) -> dict:
    """Cari berita terbaru via DuckDuckGo News (free)."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = []
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": r.get('title', ''),
                    "link": r.get('url', ''),
                    "snippet": r.get('body', r.get('description', ''))[:300],
                    "date": r.get('date', ''),
                    "source": r.get('source', '')
                })
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "source": "DuckDuckGo News"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_weather(location: str) -> dict:
    """Dapatkan cuaca via wttr.in (free, no API key)."""
    import urllib.request
    import json as _json
    
    try:
        url = f"https://wttr.in/{location}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
            
        current = data.get('current_condition', [{}])[0]
        area = data.get('nearest_area', [{}])[0]
        
        return {
            "success": True,
            "location": location,
            "area": area.get('areaName', [{}])[0].get('value', location),
            "country": area.get('country', [{}])[0].get('value', ''),
            "temperature": current.get('temp_C', '?'),
            "feels_like": current.get('FeelsLikeC', '?'),
            "humidity": current.get('humidity', '?'),
            "wind_speed": current.get('windspeedKmph', '?'),
            "weather_desc": current.get('weatherDesc', [{}])[0].get('value', ''),
            "source": "wttr.in"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "location": location}


def get_country_info(country: str) -> dict:
    """Dapatkan informasi negara (ekonomi, populasi, dll)."""
    import urllib.request
    import json as _json
    
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
            
        if not data:
            return {"success": False, "error": "Negara tidak ditemukan"}
        
        c = data[0]
        return {
            "success": True,
            "country": c.get('name', {}).get('common', country),
            "official_name": c.get('name', {}).get('official', ''),
            "capital": c.get('capital', ['?'])[0],
            "region": c.get('region', ''),
            "subregion": c.get('subregion', ''),
            "population": c.get('population', 0),
            "area_km2": c.get('area', 0),
            "currency": list(c.get('currencies', {}).keys())[0] if c.get('currencies') else '?',
            "languages": list(c.get('languages', {}).values()),
            "timezone": c.get('timezones', ['?'])[0],
            "continents": c.get('continents', []),
            "flag": c.get('flag', ''),
            "source": "REST Countries API"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "country": country}


def fetch_url(url: str) -> dict:
    """Fetch konten dari URL (buat referensi simulasi)."""
    import urllib.request
    from bs4 import BeautifulSoup
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [l for l in text.split('\n') if l.strip()]
        clean_text = '\n'.join(lines[:200])  # max 200 lines
        
        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": clean_text[:8000],
            "content_length": len(clean_text)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}


def get_news_headlines(topic: str = "indonesia", max_results: int = 10) -> dict:
    """Cari berita terkini dari RSS feeds (free)."""
    import urllib.request
    import xml.etree.ElementTree as ET
    
    # RSS feeds gratis
    feeds = {
        "indonesia": "https://news.google.com/rss/search?q=indonesia&hl=id&gl=ID",
        "world": "https://news.google.com/rss/search?q=world+news&hl=en&gl=US",
        "technology": "https://news.google.com/rss/search?q=technology&hl=en&gl=US",
        "business": "https://news.google.com/rss/search?q=business&hl=en&gl=US",
        "sports": "https://news.google.com/rss/search?q=sports&hl=en&gl=US"
    }
    
    url = feeds.get(topic, feeds["indonesia"])
    if topic not in feeds:
        url = f"https://news.google.com/rss/search?q={topic}&hl=id&gl=ID"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode('utf-8', errors='ignore')
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        results = []
        for item in items[:max_results]:
            results.append({
                "title": item.findtext('title', ''),
                "link": item.findtext('link', ''),
                "description": item.findtext('description', '')[:300],
                "pub_date": item.findtext('pubDate', ''),
                "source": item.findtext('source', 'Google News')
            })
        
        return {
            "success": True,
            "topic": topic,
            "results": results,
            "count": len(results),
            "source": "Google News RSS"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "country": country}


def get_exchange_rate(base="USD", target="IDR") -> dict:
    """Dapatkan kurs mata uang (free, no API key)."""
    import urllib.request
    import json as _json
    
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
        
        if data.get('result') == 'success':
            rates = data.get('rates', {})
            return {
                "success": True,
                "base": base,
                "target": target,
                "rate": rates.get(target, '?'),
                "all_rates": {k: v for k, v in list(rates.items())[:10]},
                "updated": data.get('time_last_update_utc', ''),
                "source": "Exchange Rate API"
            }
        return {"success": False, "error": "API gagal"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_crypto_price(coin="bitcoin") -> dict:
    """Dapatkan harga crypto (free, no API key)."""
    import urllib.request
    import json as _json
    
    coin_map = {
        "bitcoin": "bitcoin", "btc": "bitcoin",
        "ethereum": "ethereum", "eth": "ethereum",
        "solana": "solana", "sol": "solana",
        "bnb": "binancecoin", "binance": "binancecoin",
        "xrp": "ripple", "ripple": "ripple",
        "dogecoin": "dogecoin", "doge": "dogecoin"
    }
    
    coin_id = coin_map.get(coin.lower(), coin.lower())
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,idr&include_24hr_change=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
        
        coin_data = data.get(coin_id, {})
        return {
            "success": True,
            "coin": coin,
            "price_usd": coin_data.get('usd', '?'),
            "price_idr": coin_data.get('idr', '?'),
            "change_24h": coin_data.get('usd_24h_change', '?'),
            "source": "CoinGecko"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "coin": coin}


def get_gold_price() -> dict:
    """Dapatkan harga emas (free)."""
    import urllib.request
    import json as _json
    
    try:
        url = "https://www.gold-api.com/api/XAU/USD"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
        return {
            "success": True,
            "price_usd_per_oz": data.get('price', '?'),
            "change": data.get('change', '?'),
            "source": "Gold API"
        }
    except:
        # Fallback: ambil dari web
        return {"success": False, "source": "Gold API tidak tersedia"}


def get_stock_index(index="IHSG") -> dict:
    """Cari data indeks saham (via Google News + web scraping)."""
    import urllib.request
    import xml.etree.ElementTree as ET
    
    try:
        # Google News RSS (paling stabil)
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(index + ' saham')}&hl=id&gl=ID"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode('utf-8', errors='ignore')
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        headlines = []
        for item in items[:10]:
            headlines.append({
                "title": item.findtext('title', ''),
                "date": item.findtext('pubDate', '')[:16]
            })
        
        return {
            "success": True,
            "index": index,
            "headlines": headlines,
            "count": len(headlines),
            "source": "Google News"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "index": index}


def get_economic_indicators(country="Indonesia") -> dict:
    """Cari indikator ekonomi (via berita terbaru)."""
    import urllib.request
    import xml.etree.ElementTree as ET
    
    indicators = ["inflasi", "suku bunga", "PDB", "pertumbuhan ekonomi", "cadangan devisa"]
    results = {}
    
    for ind in indicators:
        try:
            query = f"{country} {ind} 2026"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=id&gl=ID"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            if items:
                results[ind] = items[0].findtext('title', '')[:150]
        except:
            results[ind] = "Data tidak tersedia"
    
    return {
        "success": True,
        "country": country,
        "indicators": results,
        "source": "Google News"
    }


def search_wikipedia(query: str) -> dict:
    """Cari informasi dari Wikipedia (free)."""
    import urllib.request
    import json as _json
    import xml.etree.ElementTree as ET
    
    try:
        api_url = f"https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'MiroFish/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
        
        results = []
        for r in data.get('query', {}).get('search', [])[:5]:
            results.append({
                "title": r.get('title', ''),
                "snippet": r.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')[:200],
                "page_id": r.get('pageid', '')
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "source": "Wikipedia (ID)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# =========================================================================
# MiroFish MCP Agent — Query real-time data dari agent
# =========================================================================
def query_real_time(query: str) -> dict:
    """
    Cari data real-time berdasarkan query.
    Otomatis deteksi jenis query.
    """
    query_lower = query.lower()
    
    # Deteksi crypto
    if any(kw in query_lower for kw in ['bitcoin', 'btc', 'eth', 'ethereum', 'crypto', 'harga bitcoin', 'harga eth']):
        for kw in ['harga ', 'price ']:
            if kw in query_lower:
                coin = query.split(kw, 1)[-1].strip().split()[0]
                return get_crypto_price(coin)
        return get_crypto_price("bitcoin")
    
    # Deteksi kurs
    if any(kw in query_lower for kw in ['kurs', 'exchange rate', 'usd ke idr', 'dollar ke rupiah', 'mata uang']):
        pairs = re.findall(r'(\w+)\s*(?:ke|to|/)\s*(\w+)', query)
        if pairs:
            return get_exchange_rate(pairs[0][0].upper(), pairs[0][1].upper())
        return get_exchange_rate("USD", "IDR")
    
    # Deteksi emas
    if any(kw in query_lower for kw in ['emas', 'gold', 'logam mulia']):
        return get_gold_price()
    
    # Deteksi indeks saham
    if any(kw in query_lower for kw in ['ihsg', 'saham', 'indeks', 'bursa', 'stock market']):
        for idx in ['IHSG', 'KOSPI', 'STI', 'KLSE', 'PSEi', 'Nikkei']:
            if idx.lower() in query_lower:
                return get_stock_index(idx)
        return get_stock_index("IHSG")
    
    # Deteksi cuaca
    if any(kw in query_lower for kw in ['cuaca', 'weather', 'suhu', 'hujan', 'angin']):
        for kw in ['di ', 'lokasi ']:
            if kw in query_lower:
                location = query.split(kw, 1)[-1].strip()
                return get_weather(location)
        return get_weather("jakarta")
    
    # Deteksi negara
    if any(kw in query_lower for kw in ['negara', 'country', 'informasi negara', 'profil negara']):
        for kw in ['negara ', 'country ', 'tentang ']:
            if kw in query_lower:
                country = query.split(kw, 1)[-1].strip()
                return get_country_info(country)
        return get_country_info(query)
    
    # Deteksi berita
    if any(kw in query_lower for kw in ['berita', 'news', 'kabar', 'headline']):
        for kw in ['berita ', 'news ', 'tentang ']:
            if kw in query_lower:
                topic = query.split(kw, 1)[-1].strip()
                return search_news(topic)
        return get_news_headlines("indonesia")
    
    # Deteksi Wikipedia
    if any(kw in query_lower for kw in ['apa itu', 'siapa itu', 'wikipedia', 'definisi', 'pengertian']):
        return search_wikipedia(query)
    
    # Deteksi indikator ekonomi
    if any(kw in query_lower for kw in ['ekonomi', 'inflasi', 'pdb', 'suku bunga', 'cadangan devisa']):
        for kw in ['ekonomi ', 'indikator ekonomi ']:
            if kw in query_lower:
                country = query.split(kw, 1)[-1].strip()
                return get_economic_indicators(country)
        return get_economic_indicators("Indonesia")
    
    # Default: web search
    return search_web(query)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🐟 MiroFish MCP Data Agent")
        print()
        print("Perintah:")
        print("  search <q>          — Cari di web")
        print("  news <q>            — Cari berita")
        print("  weather <lokasi>    — Cek cuaca")
        print("  country <negara>    — Info negara")
        print("  fetch <url>         — Ambil halaman web")
        print("  kurs [USD/IDR]      — Kurs mata uang")
        print("  crypto <coin>       — Harga crypto")
        print("  emas                — Harga emas")
        print("  saham <indeks>      — Berita indeks saham")
        print("  ekonomi <negara>    — Indikator ekonomi")
        print("  wiki <query>        — Cari Wikipedia")
        print("  auto <query>        — Auto-detect jenis")
        print()
        print("Contoh:")
        print("  python3 mcp-client.py kurs USD/IDR")
        print("  python3 mcp-client.py crypto bitcoin")
        print("  python3 mcp-client.py saham IHSG")
        print("  python3 mcp-client.py emas")
        print("  python3 mcp-client.py ekonomi Indonesia")
        print("  python3 mcp-client.py auto 'berapa harga bitcoin?'")
        sys.exit(1)

    cmd = sys.argv[1]
    query = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''

    commands = {
        'search': lambda q: search_web(q),
        'news': lambda q: search_news(q) if q else get_news_headlines(),
        'weather': lambda q: get_weather(q or "jakarta"),
        'country': lambda q: get_country_info(q or "indonesia"),
        'fetch': lambda q: fetch_url(q),
        'kurs': lambda q: get_exchange_rate(*(q.split('/') if '/' in q else ['USD', 'IDR'])),
        'crypto': lambda q: get_crypto_price(q or "bitcoin"),
        'emas': lambda q: get_gold_price(),
        'saham': lambda q: get_stock_index(q or "IHSG"),
        'ekonomi': lambda q: get_economic_indicators(q or "Indonesia"),
        'wiki': lambda q: search_wikipedia(q),
        'auto': lambda q: query_real_time(q),
    }

    result = commands.get(cmd, lambda q: {"error": f"Perintah tidak dikenal: {cmd}"})(query)
    print(json.dumps(result, indent=2, ensure_ascii=False))
