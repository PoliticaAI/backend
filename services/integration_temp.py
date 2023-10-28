npmimport llm
import duckduckgo as ddg
import json
from newspaper import Article

def do_everything(url):
    gpt_response = llm.GPTAnalyzer.analyze_article(url)

    ddg_response = ddg.SearchEngine.get_links(gpt_response['title'])
    ddg_response = ddg.SearchEngine.filter_links(ddg_response, url)

    return {
        'gpt_response': gpt_response,
        'ddg_response': ddg_response
    }

if __name__ == "__main__":
    url = "https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking"
    print(json.dumps(do_everything(url), indent=4))