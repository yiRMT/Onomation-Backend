from flask import Flask, request


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test", methods=["GET", "POST"])
def test_post():
    if request.method == "POST":
        data = request.form["data"]
        return data
    else:
        return "GET"


if __name__ == "__main__":
    app.run()
