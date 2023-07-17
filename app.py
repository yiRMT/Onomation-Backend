from fastapi import FastAPI, Request, Response, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore_async, auth
from datetime import datetime

load_dotenv()

app = FastAPI()

# CORSの許可
origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://onomation.yiwashita.com",
    "https://onomation.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OpenAIAuth(BaseModel):
    openai_api_key: str


class OnomationResponse(BaseModel):
    html: str
    css: str
    javascript: str


class AccessControll(BaseModel):
    firebaseIdToken: str


class Post(BaseModel):
    animation: OnomationResponse
    comment: str
    originalText: str
    postDate: datetime
    uid: str
    displayName: str


@app.post("/api/v1/gpt", tags=['Generate Onomation'])
async def gpt(text: str, openai_auth: OpenAIAuth) -> OnomationResponse:
    openai.api_key = openai_auth.openai_api_key
    response = requst_gpt(text)
    html_str, css_str, js_str = format_gpt_response(response)
    return OnomationResponse(html=html_str, css=css_str, javascript=js_str)


def requst_gpt(text: str):
    """GPT-3.5にリクエストを送信する関数

    Arg:
        text: str
            オノマトペのテキスト
    Returns:
        {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "{ \"html\": \"<!DOCTYPE html><html><head><title>\u30b6\u30fc\u30b6\u30fc Animation</title><link rel=\"stylesheet\" type=\"text/css\" ></head><body><div id=\"container\"><div id=\"circle\"></div></div><script src=\"script.js\"></script></body></html>\", \"css\": \"#container { position: relative; width: 200px; height: 200px; overflow: hidden; } #circle { position: absolute; width: 100%; height: 100%; border-radius: 50%; background-color: blue; } \", \"javascript\": \"const circle = document.getElementById(\"circle\"); function animateCircle() { circle.style.transform = \"scale(2)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; setTimeout(function() { circle.style.transform = \"scale(1)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; }, 500); setTimeout(animateCircle, 1000); } animateCircle(); \" }"
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

    messages = [
        {'role': 'system', 'content': 'あなたは素晴らしいWebデザイナーです。'},
        {'role': 'user', 'content': f'\
            「{text}」を表すアニメーションを作成してください (HTML, CSS, JavaScriptを使用) \
            - 注意: idはハッシュ関数を用いて生成し、ユニークなものにしてください \
        '},
    ]

    schema = {
        'type': 'object',
        'properties': {
            'html': {
                'type': 'string'
            },
            'css': {
                'type': 'string'
            },
            'javascript': {
                'type': 'string'
            }
        },
        'required': ['html', 'css', 'javascript'],
        'additionalProperties': False
    }

    functions = [
        {'name': 'set_definition', 'parameters': schema},
    ]

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k',
        messages=messages,
        functions=functions,
        function_call={'name': 'set_definition'},
        temperature=0.8,
        n=1
    )

    return response


def format_gpt_response(res):
    """GPT-3.5からのレスポンスを整形する関数

    Returns:
        {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "{ \"html\": \"<!DOCTYPE html><html><head><title>\u30b6\u30fc\u30b6\u30fc Animation</title><link rel=\"stylesheet\" type=\"text/css\" ></head><body><div id=\"container\"><div id=\"circle\"></div></div><script src=\"script.js\"></script></body></html>\", \"css\": \"#container { position: relative; width: 200px; height: 200px; overflow: hidden; } #circle { position: absolute; width: 100%; height: 100%; border-radius: 50%; background-color: blue; } \", \"javascript\": \"const circle = document.getElementById(\"circle\"); function animateCircle() { circle.style.transform = \"scale(2)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; setTimeout(function() { circle.style.transform = \"scale(1)\"; circle.style.transition = \"transform 0.5s ease-in-out\"; }, 500); setTimeout(animateCircle, 1000); } animateCircle(); \" }"
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
    content = res.choices[0].message.function_call.arguments

    # json形式の文字列を辞書型に変換
    html_str = json.loads(content)['html'] if json.loads(content)['html'] else ''
    css_str = json.loads(content)['css'] if json.loads(content)['css'] else ''
    js_str = json.loads(content)['javascript'] if json.loads(content)['javascript'] else ''

    response = (html_str, css_str, js_str)
    print(response)

    return response


@app.post("/api/v1/posts", tags=['Posts'])
async def store_posts_to_firestore(data: Post, authData: AccessControll):
    """Firestoreに投稿を保存するためのエンドポイント

    Args:
        data (Post): 投稿データ
        authData (AccessControll): 認証データ

    Returns:
        data (Post): 投稿データ
    """
    # Firebaseに接続するためのコード
    if (not firebase_admin._apps):
        cred = credentials.Certificate("./ServiceAccountKey.json")
        firebase_admin.initialize_app(cred)
    db = firestore_async.client()

    # Firebaseの認証を行うコード
    auth.verify_id_token(authData.firebaseIdToken)

    # Firebaseにデータを保存するコード
    await db.collection("posts").add(data.model_dump())

    return data


@app.get("/api/v1/posts", tags=['Posts'])
async def get_posts_from_firestore(uid: str = None):
    """投稿を取得するためのエンドポイント

    Returns:
        - クエリパラメータにuidがある場合: ユーザーの投稿を返す (詳細は `get_all_user_posts()` を参照)
        - クエリパラメータがない場合: 全ユーザーの投稿を返す (詳細は `get_posts_by_uid()`を参照)
    """
    if uid:
        return await get_posts_by_uid(uid)
    else:
        return await get_all_user_posts()


async def get_all_user_posts():
    """全ユーザの投稿を取得する関数

    Returns:
        [
            {
                animation: {
                    html: str
                    css: str
                    javascript: str
                },
                comment: str
                originalText: str
                postDate: datetime
                uid: str
                displayName: str
            },
            ...
        ]
    """
    # Firebaseに接続するためのコード
    if (not firebase_admin._apps):
        cred = credentials.Certificate("./ServiceAccountKey.json")
        firebase_admin.initialize_app(cred)
    db = firestore_async.client()

    docs = db.collection("posts").stream()

    results = []
    async for doc in docs:
        print(f"{doc.id} => {doc.to_dict()}")
        results.append(doc.to_dict())

    return results


async def get_posts_by_uid(uid: str):
    """指定されたユーザの投稿を取得する関数

    Returns:
        [
            {
                animation: {
                    html: str
                    css: str
                    javascript: str
                },
                comment: str
                originalText: str
                postDate: datetime
                uid: str
                displayName: str
            },
            ...
        ]
    """
    # Firebaseに接続するためのコード
    if (not firebase_admin._apps):
        cred = credentials.Certificate("./ServiceAccountKey.json")
        firebase_admin.initialize_app(cred)
    db = firestore_async.client()

    docs = db.collection("posts").where("uid", "==", uid).stream()

    results = []
    async for doc in docs:
        print(f"{doc.id} => {doc.to_dict()}")
        results.append(doc.to_dict())

    return results


if __name__ == "__main__":
    app.run()
