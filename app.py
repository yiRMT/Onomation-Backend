from fastapi import FastAPI
from pydantic import BaseModel
import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI()


class GPTResponseModel(BaseModel):
    html: str
    css: str
    javascript: str


@app.get("/")
async def hello_world():
    return {"message": "Hello World"}


@app.post("/api/v1/gpt")
async def gpt(text: str) -> GPTResponseModel:
    response = requst_gpt(text)
    html_str, css_str, js_str = format_gpt_response(response)

    return GPTResponseModel(html=html_str, css=css_str, javascript=js_str)


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
        model='gpt-4',
        messages=messages,
        temperature=0.2,
        n=1
    )

    return response

def format_gpt_response(res):
    """response format
    {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
            "role": "assistant",
            "content": "{ \"html\": \"<!DOCTYPE html><html><head><title>\u30b6\u30fc\u30b6\u30fc Animation</title><link rel=\"stylesheet\" type=\"text/css\" href=\"styles.css\"></head><body><div id=\"container\"><div id=\"circle\"></div></div><script src=\"script.js\"></script></body></html>\", \"css\": \"#container { position: relative; width: 200px; height: 200px; overflow: hidden; } #circle { position: absolute; width: 100%; height: 100%; border-radius: 50%; background-color: blue; } \", \"javascript\": \"const circle = document.getElementById(\"circle\"); function animateCircle() { circle.style.transform = \"scale(2)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; setTimeout(function() { circle.style.transform = \"scale(1)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; }, 500); setTimeout(animateCircle, 1000); } animateCircle(); \" }"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
    """
    # GPTのresponseからcontentのみを取得
    content = res.choices[0].message.content

    # html, css, jsをパース
    html_str = content.split('\"html\": \"')[1].split('\", \"css\": \"')[0]
    css_str = content.split('\", \"css\": \"')[1].split('\", \"javascript\": \"')[0]
    js_str = content.split('\", \"javascript\": \"')[1].split('\" }')[0]

    response = (html_str, css_str, js_str)
    print(response)

    return response

if __name__ == "__main__":
    app.run()
