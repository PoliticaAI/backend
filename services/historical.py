import json
import os

class HistoricalAnalyzer:
    @staticmethod
    def _read_data():
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        print(os.path.join(curr_dir, "articles_data.json"))
        with open(os.path.join(curr_dir, "articles_data.json"), "r") as data:
            return json.load(data)

    @staticmethod
    def get_historical_data(url):
        for article in HistoricalAnalyzer.DATA:
            if article["url"] in url:
                return {"reliability": article["reliability"], "bias": article["bias"]}
        
        return None

HistoricalAnalyzer.DATA = HistoricalAnalyzer._read_data()
