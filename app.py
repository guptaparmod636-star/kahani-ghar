import os
import re
import base64

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")

client = genai.Client(api_key=API_KEY) if API_KEY else None
app = Flask(__name__, static_folder="static")

LENGTHS = {"short": "150-200", "medium": "350-450", "long": "700-900"}


@app.get("/")
def home():
    return send_from_directory("static", "index.html")


def make_story(topic, language, genre, length):
    prompt = f"""You are a creative story writer.
Topic: {topic}
Style: {genre}
Language: {language} (Hinglish means Hindi written in Roman script)
Length: about {LENGTHS.get(length, LENGTHS['medium'])} words.

Reply in EXACTLY this format and nothing else:
TITLE: <story title>
STORY:
<the full story with a beginning, middle and end>
IMAGE_PROMPT: <one English sentence describing the key scene as a colourful illustration, no text in the image>"""
    resp = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
    text = (resp.text or "").strip()

    title = re.search(r"TITLE:\s*(.+)", text)
    story = re.search(r"STORY:\s*(.*?)(?:\nIMAGE_PROMPT:|$)", text, re.S)
    img = re.search(r"IMAGE_PROMPT:\s*(.+)", text)
    return {
        "title": title.group(1).strip() if title else topic,
        "story": story.group(1).strip() if story else text,
        "image_prompt": img.group(1).strip() if img else f"Colourful illustration of: {topic}",
    }


def make_image(image_prompt):
    resp = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=f"Create a colourful, child-friendly storybook illustration, no text or letters. Scene: {image_prompt}",
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )
    for cand in resp.candidates or []:
        parts = cand.content.parts if cand.content else []
        for part in parts or []:
            data = getattr(part, "inline_data", None)
            if data and data.data:
                raw = data.data
                if isinstance(raw, str):
                    raw = raw.encode()
                    b64 = raw.decode()
                else:
                    b64 = base64.b64encode(raw).decode()
                return f"data:{data.mime_type or 'image/png'};base64,{b64}"
    raise RuntimeError("Model ne image wapas nahi di")


@app.post("/api/generate")
def generate():
    if client is None:
        return jsonify(error="GEMINI_API_KEY set nahi hai. .env file check karo."), 500

    body = request.get_json(silent=True) or {}
    topic = (body.get("topic") or "").strip()[:200]
    if not topic:
        return jsonify(error="Topic likho."), 400

    try:
        result = make_story(
            topic,
            body.get("language", "Hinglish"),
            body.get("genre", "Bacchon ki kahani"),
            body.get("length", "medium"),
        )
    except Exception as e:
        return jsonify(error=f"Kahani nahi ban payi: {e}"), 502

    try:
        result["image"] = make_image(result["image_prompt"])
    except Exception as e:
        result["image"] = None
        result["image_error"] = str(e)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
