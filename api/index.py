from flask import Flask, jsonify, request
from flask_cors import CORS

import re
import json

from newspaper import Article
from bardapi import BardCookies
import nltk

nltk.download("punkt")

app = Flask(__name__)
CORS(app, resources={"/*": {"origins": "*"}})

cookie_dict = {
    "__Secure-1PSID": "Zwg9wJMxJpO06uMMIerPQI6YpAYaLxu-pWvfF9ED8UsK7gIUDwMxZiS7rZaBjq-PhWG7WQ.",
    "__Secure-1PSIDTS": "sidts-CjIBSAxbGY8BbICXL4SkiW7z1I5D3O2iQzzeixmzsu7XGTAe4A9w_Cc89esc7r3Ajz2OehAA",
    "__Secure-1PSIDCC": "APoG2W8xR1JEy_-H7tTxWf5X0JgKEqVcBqHJ9HsdngSvxIGD1qELBDa6itoe41bv7t4wVM-6Aw",
}

bard = BardCookies(cookie_dict=cookie_dict)

with open("historical_ratings.json", "r") as fin:
    # Mock historical ratings data
    HISTORICAL_RATINGS = json.load(fin)


@app.route("/update_form", methods=["GET"])
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


@app.route("/update_cookies", methods=["POST"])
def update_cookies():
    global cookie_dict, bard  # make sure you are referencing the global variable

    # Fetching the form data
    __Secure_1PSID = request.form.get("__Secure-1PSID")
    __Secure_1PSIDTS = request.form.get("__Secure-1PSIDTS")
    __Secure_1PSIDCC = request.form.get("__Secure-1PSIDCC")

    if not (__Secure_1PSID and __Secure_1PSIDTS and __Secure_1PSIDCC):
        return jsonify({"message": "All cookie values are required!"}), 400

    cookie_dict.update(
        {
            "__Secure-1PSID": __Secure_1PSID,
            "__Secure-1PSIDTS": __Secure_1PSIDTS,
            "__Secure-1PSIDCC": __Secure_1PSIDCC,
        }
    )

    bard = BardCookies(cookie_dict=cookie_dict)  # Update the BardCookies instance

    return jsonify({"message": "Cookies updated successfully!"})


@app.route("/get_leaning", methods=["GET"])
def get_leaning():
    article = request.args.get("url")

    prompt = (
        f"{str(article)}: Give an answer and only an answer on a scale of [-10, 10], and make it so that -10 "
        "is left leaning, and -10 is right leaning, and 0 is neutral, make sure its an estimate,"
        "which is ok, and it is a priority you only give that format for the answer, and that you"
        " bold the answer. Bold only the answer, and give the answer in the format of "
        '"**[Number]:Neutral/Left/Right**", make sure it is that exact format for the answer'
    )

    raw_response = str(bard.get_answer(prompt)["content"])

    try:
        rating = raw_response.split("**")[1]
    except IndexError as e:
        return (
            jsonify(
                {
                    "message": "Could not get rating of article.",
                    "bard_response": raw_response,
                }
            ),
            500,
        )

    return jsonify({"rating": rating})


@app.route("/historical_ratings", methods=["GET"])
def historical_ratings():
    url = request.args.get("url")
    domain = re.search("(https?://)?(www\d?\.)?(?P<domain>[\w-]*\.\w{2,})", url).group(
        "domain"
    )
    if domain in HISTORICAL_RATINGS:
        return jsonify(HISTORICAL_RATINGS[domain])
    else:
        return jsonify({"message": "No data available for this publisher."}), 404


@app.route("/summarize", methods=["GET"])
def summarize():
    url = request.args.get("url")

    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    summary = article.summary

    return jsonify({"summary": summary}), 200


def run():
    app.run(debug=True)


if __name__ == "__main__":
    run()
