# AI Kahani Ghar (Gemini)

Topic likho -> Gemini kahani likhta hai aur uski tasveer bhi banata hai.

## Setup (Windows + VS Code)
1. Gemini API key lo: https://aistudio.google.com/apikey
2. VS Code me is folder ko kholo, Terminal kholo:

       python -m venv venv
       venv\Scripts\activate
       pip install -r requirements.txt

3. `.env.example` ko copy karke `.env` naam do, aur usme `GEMINI_API_KEY=` ke aage apni key paste karo.
4. Chalao:

       python app.py

5. Browser me kholo: http://127.0.0.1:5000

## Problems
- "GEMINI_API_KEY set nahi hai": .env file ka naam aur key check karo.
- Kahani ya tasveer me "404 / model not found": .env me GEMINI_TEXT_MODEL ya GEMINI_IMAGE_MODEL ka naam
  https://ai.google.dev/gemini-api/docs/models se dekh kar badlo.
- Tasveer me quota / billing error: image models ke liye Google account me billing ya paid tier chahiye ho sakta hai.
  Tab bhi kahani aa jayegi, sirf tasveer nahi aayegi.

## Online publish karna
Is app ko Render / Railway / PythonAnywhere par chala sakte ho. Wahan GEMINI_API_KEY ko
environment variable me daalo (.env file upload mat karo), aur start command: `gunicorn app:app`
(requirements.txt me `gunicorn` jod do).
