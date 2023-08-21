from flask import Flask, jsonify, request
from newspaper import Article
import re
from bardapi import BardCookies
import nltk

nltk.download('punkt')
app = Flask(__name__)

cookie_dict = {
    "__Secure-1PSID": "aAiJWcmnwi6buDGDaqBP2TRCFnUoCoOSPFjfi461UQOLqGEEuA0HfkrsMI4A6FuEk8ahjw.",
    "__Secure-1PSIDTS": "sidts-CjIBSAxbGYZWFpru8bT-tG1Rz4VWBkpZpHQ7W8iWg_PBHepCXx0G9IwbhJRkAMp-VQQ_DRAA",
    "__Secure-1PSIDCC": "APoG2W9GuTzFWCZj7yPTPhkZl0UZGbICdsXa_JQS8dn7284ruq_TQixlv97ax92xopDT4zuwBCA",
}

bard = BardCookies(cookie_dict=cookie_dict)

@app.route('/update_form', methods=['GET'])
def update_form():
    html = """
    <html>
        <body>
            <form action="/update_cookies" method="post">
                __Secure-1PSID: <input type="text" name="__Secure-1PSID"><br><br>
                __Secure-1PSIDTS: <input type="text" name="__Secure-1PSIDTS"><br><br>
                __Secure-1PSIDCC: <input type="text" name="__Secure-1PSIDCC"><br><br>
                <input type="submit" value="Update Cookies">
            </form>
        </body>
    </html>
    """
    return html

@app.route('/update_cookies', methods=['POST'])
def update_cookies():
    global cookie_dict, bard  # make sure you are referencing the global variable

    # Fetching the form data
    __Secure_1PSID = request.form.get('__Secure-1PSID')
    __Secure_1PSIDTS = request.form.get('__Secure-1PSIDTS')
    __Secure_1PSIDCC = request.form.get('__Secure-1PSIDCC')

    if not (__Secure_1PSID and __Secure_1PSIDTS and __Secure_1PSIDCC):
        return jsonify({'message': 'All cookie values are required!'}), 400

    cookie_dict.update({
        "__Secure-1PSID": __Secure_1PSID,
        "__Secure-1PSIDTS": __Secure_1PSIDTS,
        "__Secure-1PSIDCC": __Secure_1PSIDCC
    })

    bard = BardCookies(cookie_dict=cookie_dict)  # Update the BardCookies instance

    return jsonify({'message': 'Cookies updated successfully!'})


@app.route('/get_learning', methods=['GET'])
def get_leaning():
    article = request.args.get('url')
    prompt = str(article) + ': Give an answer and only an answer on a scale of [-10, 10], and make it so that -10 is left leaning, and -10 is right leaning, and 0 is neutral, make sure its an estimate, which is ok, and it is a priority you only give that format for the answer, and that you bold the answer. Bold only the answer, and give the answer in the format of "**[Number]:Neutral/Left/Right**", make sure it is that exact format for the answer'
    response = str(bard.get_answer(prompt)['content']).split('**')[1]
    return jsonify({'rating': response})

# Mock historical ratings data
HISTORICAL_RATINGS = {
    'nbcnews.com': {'political': -5, 'factuality': 7},
    'foxnews.com': {'political': 5, 'factuality': 6},
    'cnn.com': {'political': -4, 'factuality': 7},
    'nytimes.com': {'political': -4, 'factuality': 8},
    'washingtonpost.com': {'political': -3, 'factuality': 8},
    'wsj.com': {'political': 1, 'factuality': 8},
    'thehill.com': {'political': 0, 'factuality': 7},
    'bbc.com': {'political': -1, 'factuality': 8},
    'reuters.com': {'political': 0, 'factuality': 9},
    'apnews.com': {'political': 0, 'factuality': 9},
    'aljazeera.com': {'political': -2, 'factuality': 7},
    'rt.com': {'political': 3, 'factuality': 5},
    'breitbart.com': {'political': 6, 'factuality': 5},
    'msnbc.com': {'political': -6, 'factuality': 6},
    'huffpost.com': {'political': -5, 'factuality': 6},
    'theatlantic.com': {'political': -4, 'factuality': 8},
    'buzzfeednews.com': {'political': -4, 'factuality': 7},
    'dailymail.co.uk': {'political': 4, 'factuality': 5},
    'usatoday.com': {'political': -1, 'factuality': 8},
    'time.com': {'political': -3, 'factuality': 8},
    'abcnews.go.com': {'political': -3, 'factuality': 7},
    'cbsnews.com': {'political': -3, 'factuality': 7},
    'npr.org': {'political': -2, 'factuality': 8},
    'politico.com': {'political': -2, 'factuality': 8},
    'slate.com': {'political': -5, 'factuality': 7},
    'nationalreview.com': {'political': 5, 'factuality': 7},
    'thedailybeast.com': {'political': -5, 'factuality': 7},
    'theintercept.com': {'political': -5, 'factuality': 7},
    'theguardian.com': {'political': -3, 'factuality': 8},
    'voxdotcom': {'political': -6, 'factuality': 7},
    'oann.com': {'political': 7, 'factuality': 5},
    'newsweek.com': {'political': 0, 'factuality': 7},
    'vicenews.com': {'political': -4, 'factuality': 7},
    'reason.com': {'political': 3, 'factuality': 7},
    'zerohedge.com': {'political': 4, 'factuality': 5},
    'thedailywire.com': {'political': 6, 'factuality': 7},
    'thinkprogress.org': {'political': -6, 'factuality': 6},
    'rawstory.com': {'political': -5, 'factuality': 6},
    'financialtimes.com': {'political': -1, 'factuality': 8},
    'economist.com': {'political': 0, 'factuality': 8},
    'newyorker.com': {'political': -4, 'factuality': 8},
    'motherjones.com': {'political': -6, 'factuality': 7},
    'axios.com': {'political': -2, 'factuality': 8},
    'independent.co.uk': {'political': -3, 'factuality': 7},
    'rollingstone.com': {'political': -5, 'factuality': 7},
    'bloomberg.com': {'political': -1, 'factuality': 8},
    'talkingpointsmemo.com': {'political': -5, 'factuality': 7},
    'forbes.com': {'political': 2, 'factuality': 7},
    'spectator.co.uk': {'political': 3, 'factuality': 7},
    'telegraph.co.uk': {'political': 3, 'factuality': 7},
    'express.co.uk': {'political': 4, 'factuality': 6},
    'mirror.co.uk': {'political': -3, 'factuality': 6},
    'infowars.com': {'political': 7, 'factuality': 4},
    'rfa.org': {'political': 0, 'factuality': 8},  # Radio Free Asia

}



@app.route('/historical_ratings', methods=['GET'])
def historical_ratings():
    url = request.args.get('url')
    domain = re.search('(https?://)?(www\d?\.)?(?P<domain>[\w-]*\.\w{2,})', url).group('domain')
    if domain in HISTORICAL_RATINGS:
        return jsonify(HISTORICAL_RATINGS[domain])
    else:
        return jsonify({'message': 'No data available for this publisher.'}), 404

@app.route('/summarize', methods=['GET'])
def summarize():
    url = request.args.get('url')
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    summary = article.summary
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
