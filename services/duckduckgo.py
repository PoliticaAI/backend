import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs

import services.historical as historical


class SearchEngine:
    @staticmethod
    def get_links(query):
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        content = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            },
        ).text
        html = BeautifulSoup(content, "html.parser")

        links_raw = html.find_all("a", {"class": "result__a"})
        thumb_raw = html.find_all("img", {"class": "result__icon__img"})
        desc_raw = html.find_all("a", {"class": "result__snippet"})

        assert len(links_raw) == len(thumb_raw)

        data = []
        for i, link in enumerate(links_raw):
            parsed_href = urlparse(link.get("href"))

            title = link.getText()
            href = parse_qs(parsed_href.query)["uddg"][0]
            thumb = thumb_raw[i].get("src")
            desc = desc_raw[i].getText()

            data.append({"title": title, "href": href, "thumb": thumb, "desc": desc})

        return data

    @staticmethod
    def filter_links(links, url):
        updated_links = []

        for article in links:
            if article["href"] == url:
                continue  # Skip

            for source in historical.HistoricalAnalyzer.DATA:
                if source["url"] in article["href"]:
                    updated_links.append(article)

        return updated_links


if __name__ == "__main__":
    print(SearchEngine.get_links("Latino American Museum News"))
