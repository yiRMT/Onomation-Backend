from flask import Flask, request, render_template
import openai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/api/v1/gpt', methods=['POST'])
def gpt():
    if request.method == 'POST':
        text = request.form['text']
        response = requst_gpt(text)
        # ここにresponseを整形する処理を書く
        return response
    else:
        return render_template('index.html')


def requst_gpt(text):
    example_html = ('<!DOCTYPE html><html><head><title>ザーザー Animation</title><link rel="stylesheet" type="text/css" href="styles.css"></head><body><div id="container"><div id="circle"></div></div><script src="script.js"></script></body></html>')
    example_css = ('#container { position: relative; width: 200px; height: 200px; overflow: hidden; } #circle { position: absolute; width: 100%; height: 100%; border-radius: 50%; background-color: blue; } ')
    example_javascript = ('const circle = document.getElementById("circle"); function animateCircle() { circle.style.transform = "scale(2)"; circle.style.transition = "transform 0.5s ease-in-out"; setTimeout(function() { circle.style.transform = "scale(1)"; circle.style.transition = "transform 0.5s ease-in-out"; }, 500); setTimeout(animateCircle, 1000); } animateCircle(); ')
    example_output = '{ "html": "' + example_html + '", "css": "' + example_css + '", "javascript": "' + example_javascript + '" }'
    
    messages = [
        {'role': 'system', 'content': 'You are a website developer. Create an animation using CSS and JavaScript to show the meaning of the Japanese onomatopoeia entered by the user. The output must be a JSON object with three keys: html, css, and javascript.'},
        {'role': 'user', 'content': 'ザーザー'},
        {'role': 'assistant', 'content': example_output},
        {'role': 'user', 'content': text}
    ]
    
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.2,
        n=1
    )
    
    return response


if __name__ == "__main__":
    app.run()
