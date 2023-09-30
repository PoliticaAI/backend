import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs

def get_links(query):
  url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

  content = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
  }).text
  html = BeautifulSoup(content, 'html.parser')

  links_raw = html.find_all("a", {"class": "result__a"})
  thumb_raw = html.find_all("img", {"class": "result__icon__img"})

  assert len(links_raw) == len(thumb_raw)

  data = []
  for i in range(len(links_raw)):
    parsed_href = urlparse(links_raw[i].get("href"))

    title = links_raw[i].getText()
    href = parse_qs(parsed_href.query)["uddg"][0]
    thumb = thumb_raw[i].get("src")

    data.append({
      "title": title,
      "href": href,
      "thumb": thumb
    })

  return data

print(get_links("Latino American Museum News"))
