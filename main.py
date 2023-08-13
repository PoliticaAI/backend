import flask

app = flask.Flask()

@app.route("/")
def main():
  return "Basic Stuff"

app.run()
