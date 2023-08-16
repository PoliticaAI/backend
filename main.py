from flask import Flask, request
import json

from logic import *

app = Flask(__name__)

@app.route("/")
def main():
  return "Basic Stuff"

@app.route("/ai_rating", methods=["GET"])
def leaning():
  url = request.args.get("url")
  if not url:
    return json.dumps({ "message": "Please provide a URL." }), 400
  
  rating = get_ai_rating(url)

  return json.dumps({ "rating": rating }), 200

@app.route("/historical_ratings", methods=["GET"])
def historical_ratings():
  url = request.args.get("url")
  if not url:
    return json.dumps({ "message": "Please provide a URL." }), 400
  
  result = {
    "political": get_political_rating(url),
    "factuality": get_factuality_rating(url),
  }

  return json.dumps(result), 200

@app.route("/summarize", methods=["GET"])
def summarize():
  url = request.args.get("url")
  if not url:
    return json.dumps({ "message": "Please provide a URL." }), 400
  
  summary = get_summary(url)

  return json.dumps({ "summary": summary }), 200

app.run()
