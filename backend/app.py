from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from pathlib import Path

import subprocess
import sys
import re
import uuid
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session
)

import sqlite3
from functools import wraps
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from datetime import datetime
import time

from dotenv import load_dotenv


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_DIR = PROJECT_ROOT / "src"

FRONTEND_DIR = PROJECT_ROOT / "frontend"
print("ACTUAL INDEX:", FRONTEND_DIR / "index.html")
print("INDEX EXISTS:", (FRONTEND_DIR / "index.html").exists())

PREDICT_SCRIPT = SRC_DIR / "predict.py"

UPLOAD_DIR = (
    PROJECT_ROOT
    / "backend"
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# =========================================================
# GEMINI
# =========================================================

gemini_client = None

if GEMINI_API_KEY:

    try:

        from google import genai

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print(
            "✅ Gemini AI connected."
        )

    except Exception as error:

        print(
            "⚠️ Gemini initialization error:",
            error
        )

else:

    print(
        "⚠️ GEMINI_API_KEY not found."
    )



# =========================================================
# GEMINI CHAT CONFIGURATION / RESILIENCE
# =========================================================

GEMINI_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.8-flash,gemini-3.7-flash,gemini-3.6-flash"
    ).split(",")
    if model.strip()
]

GEMINI_RETRY_COUNT = int(os.getenv("GEMINI_RETRY_COUNT", "2"))
GEMINI_RETRY_DELAY = float(os.getenv("GEMINI_RETRY_DELAY", "1.5"))


def is_retryable_gemini_error(error):
    """Detect temporary Gemini/rate-limit failures."""
    error_text = str(error).lower()
    retry_markers = (
        "503", "unavailable", "high demand",
        "429", "resource exhausted", "rate limit",
        "500", "internal error", "temporarily unavailable",
        "overloaded"
    )
    return any(marker in error_text for marker in retry_markers)


def generate_gemini_answer(prompt):
    """Try multiple Gemini Flash models with retry/backoff."""
    if gemini_client is None:
        raise RuntimeError(
            "Gemini AI is not configured. Check your GEMINI_API_KEY."
        )

    last_error = None

    for model_name in GEMINI_MODELS:
        for attempt in range(GEMINI_RETRY_COUNT + 1):
            try:
                print(
                    f"🤖 Gemini request: {model_name} "
                    f"(attempt {attempt + 1})"
                )

                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                answer = getattr(response, "text", None)

                if answer and answer.strip():
                    print(
                        f"✅ Gemini response received from {model_name}"
                    )
                    return answer.strip()

                raise RuntimeError(
                    f"Gemini model {model_name} returned an empty response."
                )

            except Exception as error:
                last_error = error
                print(
                    f"⚠️ Gemini error on {model_name}, "
                    f"attempt {attempt + 1}: {error}"
                )

                if not is_retryable_gemini_error(error):
                    break

                if attempt < GEMINI_RETRY_COUNT:
                    time.sleep(
                        GEMINI_RETRY_DELAY * (2 ** attempt)
                    )

        print(
            f"➡️ Trying next Gemini model after: {model_name}"
        )

    if last_error:
        raise last_error

    raise RuntimeError("No Gemini model is configured.")


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(

    __name__,

    template_folder=str(
        FRONTEND_DIR
    ),

    static_folder=str(
        FRONTEND_DIR
    ),

    static_url_path="/static"

)

CORS(app)
# =========================================================
# AUTHENTICATION & DATABASE
# =========================================================

DATABASE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "kisan_mitra.db"
)


app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "CHANGE_THIS_SECRET_KEY"
)


def get_db():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    connection = get_db()

    cursor = connection.cursor()


    # USERS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            phone TEXT,

            password_hash TEXT NOT NULL,

            is_admin INTEGER DEFAULT 0,

            created_at TEXT NOT NULL,

            last_login TEXT

        )
    """)


    # CROP ANALYSIS HISTORY

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_analysis (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            crop TEXT,

            disease TEXT,

            confidence REAL,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)


    # CHAT HISTORY

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            question TEXT NOT NULL,

            answer TEXT NOT NULL,

            language TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)


    connection.commit()

    connection.close()


init_database()

# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)
    def decorated_function(
        *args,
        **kwargs
    ):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function

# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin_login.html")

    email = (
        request.form
        .get("email", "")
        .strip()
        .lower()
    )

    password = (
        request.form
        .get("password", "")
    )

    connection = get_db()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    connection.close()

    if (
        not user
        or not check_password_hash(
            user["password_hash"],
            password
        )
    ):
        return render_template(
            "admin_login.html",
            error="Invalid admin email or password."
        )

    if not user["is_admin"]:
        return render_template(
            "admin_login.html",
            error="This account does not have admin access."
        )

    session.clear()

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["is_admin"] = True

    return redirect(
        url_for("admin_dashboard")
    )

# =========================================================
# LOAD GUIDANCE ENGINE
# =========================================================

sys.path.insert(
    0,
    str(SRC_DIR)
)

try:

    from kisan_mitra_engine import (
        get_complete_guidance
    )

except Exception as error:

    get_complete_guidance = None

    print(
        "Guidance engine import error:",
        error
    )


# =========================================================
# HOME PAGE
# =========================================================
@app.route("/")
@login_required
def home():

    return render_template(
        "index.html",
        user_name=session.get(
            "user_name",
            "Farmer"
        )
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({

        "success": True,

        "message":
            "Kisan Mitra AI backend is running",

        "gemini":
            gemini_client is not None

    })

# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )


    name = (
        request.form
        .get("name", "")
        .strip()
    )

    email = (
        request.form
        .get("email", "")
        .strip()
        .lower()
    )

    phone = (
        request.form
        .get("phone", "")
        .strip()
    )

    password = (
        request.form
        .get("password", "")
    )


    if not name or not email or not password:

        return render_template(
            "register.html",
            error="Please fill all required fields."
        )


    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters."
        )


    connection = get_db()


    try:

        connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                phone,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                name,
                email,
                phone,
                generate_password_hash(
                    password
                ),
                datetime.now().isoformat()
            )
        )


        connection.commit()


    except sqlite3.IntegrityError:

        connection.close()

        return render_template(
            "register.html",
            error="This email is already registered."
        )


    connection.close()


    return redirect(
        url_for("login")
    )

# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    email = (
        request.form
        .get("email", "")
        .strip()
        .lower()
    )

    password = (
        request.form
        .get("password", "")
    )


    connection = get_db()


    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()


    if (
        not user
        or not check_password_hash(
            user["password_hash"],
            password
        )
    ):

        connection.close()

        return render_template(
            "login.html",
            error="Invalid email or password."
        )


    connection.execute(
        """
        UPDATE users
        SET last_login = ?
        WHERE id = ?
        """,

        (
            datetime.now().isoformat(),
            user["id"]
        )
    )


    connection.commit()

    connection.close()


    session.clear()


    session["user_id"] =user["id"]

    session["user_name"] =user["name"]

    session["is_admin"] =bool(user["is_admin"])


    if user["is_admin"]:
       return redirect(url_for("admin_dashboard"))

    return redirect(url_for("home"))
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

# =========================================================
# ADMIN REQUIRED
# =========================================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # User login check
        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        # Admin check
        if not session.get("is_admin", False):
            return jsonify({
                "success": False,
                "error": "Admin access required."
            }), 403

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    connection = get_db()

    # -----------------------------------------------------
    # TOTAL USERS
    # -----------------------------------------------------

    total_users = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        """
    ).fetchone()["total"]


    # -----------------------------------------------------
    # TOTAL ANALYSES
    # -----------------------------------------------------

    total_analyses = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM crop_analysis
        """
    ).fetchone()["total"]


    # -----------------------------------------------------
    # TOTAL CHATS
    # -----------------------------------------------------

    total_chats = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM chat_history
        """
    ).fetchone()["total"]


    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    users = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            phone,
            created_at,
            last_login
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()


    # -----------------------------------------------------
    # RECENT CROP ANALYSIS
    # -----------------------------------------------------

    analyses = connection.execute(
        """
        SELECT
            crop_analysis.id,
            users.name,
            users.email,
            crop_analysis.crop,
            crop_analysis.disease,
            crop_analysis.confidence,
            crop_analysis.created_at
        FROM crop_analysis
        JOIN users
        ON crop_analysis.user_id = users.id
        ORDER BY crop_analysis.id DESC
        LIMIT 50
        """
    ).fetchall()


    # -----------------------------------------------------
    # RECENT CHAT HISTORY
    # -----------------------------------------------------

    chats = connection.execute(
        """
        SELECT
            chat_history.id,
            users.name,
            users.email,
            chat_history.question,
            chat_history.answer,
            chat_history.language,
            chat_history.created_at
        FROM chat_history
        JOIN users
        ON chat_history.user_id = users.id
        ORDER BY chat_history.id DESC
        LIMIT 50
        """
    ).fetchall()


    connection.close()


    return render_template(
        "admin.html",
        total_users=total_users,
        total_analyses=total_analyses,
        total_chats=total_chats,
        users=users,
        analyses=analyses,
        chats=chats
    )
# =========================================================
# EXTRACT PREDICTION
# =========================================================

def extract_prediction(
    output
):

    patterns = [

        r"Prediction\s*:\s*([^\r\n]+)",

        r"Predicted Disease\s*:\s*([^\r\n]+)"

    ]


    for pattern in patterns:

        match = re.search(

            pattern,

            output,

            re.IGNORECASE

        )


        if match:

            return (
                match
                .group(1)
                .strip()
            )


    return None


# =========================================================
# EXTRACT CONFIDENCE
# =========================================================

def extract_confidence(
    output
):

    patterns = [

        r"Confidence\s*:\s*([0-9.]+)%",

        r"confidence\s*:\s*([0-9.]+)%"

    ]


    for pattern in patterns:

        match = re.search(

            pattern,

            output,

            re.IGNORECASE

        )


        if match:

            try:

                return float(
                    match.group(1)
                )

            except ValueError:

                pass


    return None


# =========================================================
# PREDICTION API
# =========================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict():

    if "image" not in request.files:
        

        return jsonify({


            "success": False,

            "error":
                "No image uploaded."

        }), 400


    image = request.files["image"]


    if image.filename == "":

        return jsonify({

            "success": False,

            "error":
                "No image selected."

        }), 400


    allowed_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".webp"

    }


    extension = (

        Path(
            image.filename
        )
        .suffix
        .lower()

    )


    if extension not in allowed_extensions:

        return jsonify({

            "success": False,

            "error":
                "Please upload JPG, JPEG, PNG or WEBP image."

        }), 400


    image_path = (

        UPLOAD_DIR
        /
        f"{uuid.uuid4().hex}{extension}"

    )


    image.save(
        image_path
    )


    try:

        if not PREDICT_SCRIPT.exists():

            return jsonify({

                "success": False,

                "error":
                    f"Prediction script not found: {PREDICT_SCRIPT}"

            }), 500


        process = subprocess.run(

            [

                sys.executable,

                str(
                    PREDICT_SCRIPT
                ),

                str(
                    image_path
                )

            ],

            cwd=str(
                PROJECT_ROOT
            ),

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=300

        )


        output = (
            process.stdout
            or ""
        )


        error_output = (
            process.stderr
            or ""
        )


        if process.returncode != 0:

            print(
                error_output
            )


            return jsonify({

                "success": False,

                "error":
                    "AI prediction failed.",

                "details":
                    error_output[-2000:]

            }), 500


        disease_id = (
            extract_prediction(
                output
            )
        )


        confidence = (
            extract_confidence(
                output
            )
        )


        if not disease_id:

            return jsonify({

                "success": False,

                "error":
                    "Disease prediction could not be extracted."

            }), 500


        if get_complete_guidance is None:

            return jsonify({

                "success": False,

                "error":
                    "Guidance engine is unavailable."

            }), 500


        guidance = (
            get_complete_guidance(
                disease_id
            )
        )


        if not guidance.get(
            "success",
            False
        ):

            return jsonify({

                "success": False,

                "error":
                    guidance.get(
                        "error",
                        "Disease information not found."
                    )

            }), 404


        return jsonify({

            "success": True,

            "prediction": {

                "disease_id":
                    disease_id,

                "confidence":
                    confidence

            },

            "disease":
                guidance["disease"],

            "medicines":
                guidance["medicines"],

            "videos":
                guidance["videos"]

        })


    except subprocess.TimeoutExpired:

        return jsonify({

            "success": False,

            "error":
                "Prediction took too long. Please try again."

        }), 504


    except Exception as error:

        print(
            "Backend Error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


    finally:

        try:

            if image_path.exists():

                image_path.unlink()

        except Exception:

            pass


# =========================================================
# FARMER AI CHAT
# =========================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def farmer_chat():

    if gemini_client is None:

        return jsonify({

            "success": False,

            "error":
                "Gemini AI is not configured. Check your GEMINI_API_KEY."

        }), 500


    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    question = str(
        data.get(
            "question",
            ""
        )
    ).strip()


    language = (
        data.get(
            "language",
            "Hindi"
        )
    )


    history = (
        data.get(
            "history",
            []
        )
    )


    disease_context = (
        data.get(
            "disease_context"
        )
    )

    # Weather context sent by the frontend after the farmer selects a location.
    weather_context = data.get("weather_context")


    if not question:

        return jsonify({

            "success": False,

            "error":
                "Please enter your question."

        }), 400


    language_map = {

        "Hindi":
            "Hindi (हिन्दी)",

        "English":
            "English",

        "Bhojpuri":
            "Bhojpuri (भोजपुरी)"

    }


    selected_language = (
        language_map.get(
            language,
            "Hindi (हिन्दी)"
        )
    )


    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    conversation = ""


    if isinstance(
        history,
        list
    ):

        for message in history[-10:]:

            role = str(
                message.get(
                    "role",
                    "user"
                )
            )


            content = str(
                message.get(
                    "content",
                    ""
                )
            )


            if content:

                conversation += (
                    f"\n{role.upper()}: "
                    f"{content}"
                )


    # -----------------------------------------------------
    # DISEASE CONTEXT
    # -----------------------------------------------------

    disease_text = ""


    if isinstance(
        disease_context,
        dict
    ):

        disease_text = f"""

Current crop-analysis context:

Crop:
{disease_context.get("crop", "Unknown")}

Detected disease:
{disease_context.get("disease", "Unknown")}

Confidence:
{disease_context.get("confidence", "Unknown")}

Use this information only when relevant to the question.
"""


    # -----------------------------------------------------
    # WEATHER CONTEXT
    # -----------------------------------------------------

    weather_text = ""
    if isinstance(weather_context, dict):
        current_weather = weather_context.get("current") or {}
        today_weather = weather_context.get("today") or {}
        next_days = weather_context.get("nextDays") or []
        location_name = weather_context.get("place") or "Selected location"
        timezone_name = weather_context.get("timezone") or "auto"

        if isinstance(current_weather, dict):
            weather_text = f"""
Current weather forecast context (from the Weather Forecast section):
Location: {location_name}
Timezone: {timezone_name}
Current temperature (°C): {current_weather.get("temperature", "Not available")}
Current relative humidity (%): {current_weather.get("relative_humidity", "Not available")}
Current-hour rain probability (%): {current_weather.get("rain_probability", "Not available")}
Current precipitation (mm): {current_weather.get("precipitation", "Not available")}
Wind speed (km/h): {current_weather.get("wind_speed", "Not available")}
Forecast data time: {current_weather.get("time", "Not available")}

Today's forecast:
Date: {today_weather.get("date", "Not available") if isinstance(today_weather, dict) else "Not available"}
Maximum temperature (°C): {today_weather.get("temperature_max", "Not available") if isinstance(today_weather, dict) else "Not available"}
Minimum temperature (°C): {today_weather.get("temperature_min", "Not available") if isinstance(today_weather, dict) else "Not available"}
Maximum rain probability today (%): {today_weather.get("rain_probability", "Not available") if isinstance(today_weather, dict) else "Not available"}
Expected precipitation today (mm): {today_weather.get("precipitation_sum", "Not available") if isinstance(today_weather, dict) else "Not available"}

Next forecast days:
{json.dumps(next_days[:7], ensure_ascii=False)}
"""
    else:
        weather_text = """
No weather forecast context was provided. Do not guess the farmer's location or invent a rain forecast. Ask the farmer to choose/search a location in the Weather Forecast section first, then ask again.
"""

    # -----------------------------------------------------
    # FARMER PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are Kisan Mitra AI, an agricultural assistant
designed for Indian farmers.

Reply in:
{selected_language}

Rules:

- Use simple farmer-friendly language.
- Give practical and understandable answers.
- Avoid unnecessary technical terms.
- If discussing a crop disease, explain likely symptoms,
  causes, prevention and management.
- Never invent pesticide or medicine information.
- Do not give unsafe chemical dosage instructions.
- Tell the farmer to verify the current registered product
  label and local agricultural guidance before using any
  agricultural chemical.
- If you are uncertain, clearly say so.
- Do not pretend to be a human agricultural officer.
- Keep the answer useful and reasonably concise.

{disease_text}

{weather_text}

Weather-answer rules:
- For questions about rain, temperature, or upcoming weather, use the supplied weather context when available.
- Clearly distinguish current-hour rain probability from the maximum rain probability forecast for the whole day.
- Rain probability is a probability, not a guarantee that it will rain.
- If no weather context is supplied, ask the farmer to select/search their location in the Weather Forecast section; do not claim to know their location.

Previous conversation:
{conversation}

Farmer's latest question:
{question}

Answer the farmer now.
"""


    try:

        answer = generate_gemini_answer(prompt)

        # Save successful chats for the admin/history section.
        try:
            if "user_id" in session:
                connection = get_db()
                connection.execute(
                    """
                    INSERT INTO chat_history
                    (
                        user_id,
                        question,
                        answer,
                        language,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        session["user_id"],
                        question,
                        answer,
                        language,
                        datetime.now().isoformat()
                    )
                )
                connection.commit()
                connection.close()
        except Exception as history_error:
            print("⚠️ Chat history save error:", history_error)

        return jsonify({
            "success": True,
            "answer": answer,
            "language": language
        })

    except Exception as error:
        import traceback

        print("=" * 60)
        print("❌ GEMINI CHAT ERROR")
        print("=" * 60)
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", repr(error))
        traceback.print_exc()
        print("=" * 60)

        if is_retryable_gemini_error(error):
            user_message = (
                "AI service is temporarily busy. "
                "Please try again in a few seconds."
            )
            status_code = 503
        else:
            user_message = (
                "AI could not answer right now. "
                "Please try again."
            )
            status_code = 500

        return jsonify({
            "success": False,
            "error": user_message,
            "details": str(error)[-1000:]
        }), status_code


# =========================================================
# RUN SERVER
# =========================================================
# ============================================================
# KISAN MITRA AI - WEATHER FORECASTING BACKEND
# Provider: Open-Meteo
# API key: Not required for basic weather data
# ============================================================

import json
import urllib.parse
import urllib.request

from urllib.error import HTTPError, URLError
from datetime import datetime


# ------------------------------------------------------------
# COMMON API REQUEST FUNCTION
# ------------------------------------------------------------

def weather_api_request(url):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "KisanMitraAI/1.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=15
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


# ------------------------------------------------------------
# FARMING ADVICE
# ------------------------------------------------------------

def get_weather_farming_advice(
    temperature,
    humidity,
    rain_probability,
    wind_speed
):

    advice = []

    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = None

    try:
        humidity = float(humidity)
    except (TypeError, ValueError):
        humidity = None

    try:
        rain_probability = float(rain_probability)
    except (TypeError, ValueError):
        rain_probability = None

    try:
        wind_speed = float(wind_speed)
    except (TypeError, ValueError):
        wind_speed = None


    # Rain advice

    if (
        rain_probability is not None
        and rain_probability >= 60
    ):

        advice.append(
            "Rain probability is high. "
            "Check the local forecast before irrigation "
            "and protect harvested crops from rain."
        )

    elif (
        rain_probability is not None
        and rain_probability < 20
    ):

        advice.append(
            "Rain probability is low. "
            "Check soil moisture and crop water "
            "requirements before planning irrigation."
        )


    # Temperature advice

    if (
        temperature is not None
        and temperature >= 35
    ):

        advice.append(
            "High temperatures may cause heat stress. "
            "Monitor crop moisture and avoid unnecessary "
            "field work during the hottest hours."
        )

    elif (
        temperature is not None
        and temperature <= 10
    ):

        advice.append(
            "Low temperatures may affect sensitive crops. "
            "Monitor local cold-weather advisories "
            "and take crop-specific precautions."
        )


    # Humidity advice

    if (
        humidity is not None
        and humidity >= 80
    ):

        advice.append(
            "Humidity is high. Monitor crops for signs "
            "of fungal disease and ensure appropriate "
            "field ventilation where applicable."
        )


    # Wind advice

    if (
        wind_speed is not None
        and wind_speed >= 25
    ):

        advice.append(
            "Wind speeds are relatively high. "
            "Check crop supports and avoid spraying "
            "agricultural chemicals in unsuitable "
            "wind conditions."
        )


    if not advice:

        advice.append(
            "Continue regular crop monitoring. "
            "Plan irrigation and other farm activities "
            "according to crop requirements, soil moisture "
            "and the local weather forecast."
        )


    return advice


# ------------------------------------------------------------
# WEATHER LOCATION SEARCH
# Endpoint: /api/weather/search?q=Lucknow
# ------------------------------------------------------------

@app.route(
    "/api/weather/search",
    methods=["GET"]
)

def search_weather_location():

    query = request.args.get(
        "q",
        ""
    ).strip()


    if not query:

        return jsonify({
            "success": False,
            "results": [],
            "error": "Please enter a city or district name."
        }), 400


    try:

        parameters = urllib.parse.urlencode({

            "name": query,
            "count": 10,
            "language": "en",
            "format": "json"

        })


        url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + parameters
        )


        data = weather_api_request(url)


        results = []


        for location in data.get(
            "results",
            []
        ):

            results.append({

                "name": location.get(
                    "name",
                    "Unknown"
                ),

                "latitude": location.get(
                    "latitude"
                ),

                "longitude": location.get(
                    "longitude"
                ),

                "country": location.get(
                    "country",
                    ""
                ),

                "admin1": location.get(
                    "admin1",
                    ""
                ),

                "timezone": location.get(
                    "timezone",
                    "auto"
                )

            })


        return jsonify({

            "success": True,
            "results": results

        })


    except (HTTPError, URLError, TimeoutError) as error:

        app.logger.warning(
            "Weather location API error: %s",
            error
        )

        return jsonify({

            "success": False,
            "results": [],
            "error": (
                "Location service is temporarily unavailable."
            )

        }), 503


    except Exception:

        app.logger.exception(
            "Unexpected location search error"
        )

        return jsonify({

            "success": False,
            "results": [],
            "error": "Unable to search for this location."

        }), 500


# ------------------------------------------------------------
# CURRENT WEATHER + 7-DAY FORECAST
# Endpoint: /api/weather?lat=26.8467&lon=80.9462
# ------------------------------------------------------------

@app.route(
    "/api/weather",
    methods=["GET"]
)

def get_weather():

    latitude = request.args.get(
        "lat"
    )

    longitude = request.args.get(
        "lon"
    )


    if latitude is None or longitude is None:

        return jsonify({

            "success": False,
            "error": "Latitude and longitude are required."

        }), 400


    try:

        latitude = float(latitude)
        longitude = float(longitude)


        if not (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):

            return jsonify({

                "success": False,
                "error": "Invalid latitude or longitude."

            }), 400


    except (TypeError, ValueError):

        return jsonify({

            "success": False,
            "error": "Latitude and longitude must be numbers."

        }), 400


    try:

        parameters = urllib.parse.urlencode({

            "latitude": latitude,
            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "wind_speed_10m"
            ),

            "hourly": (
                "precipitation_probability"
            ),

            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "precipitation_sum,"
                "wind_speed_10m_max"
            ),

            "forecast_days": 7,
            "timezone": "auto"

        })


        url = (
            "https://api.open-meteo.com/v1/forecast?"
            + parameters
        )


        data = weather_api_request(url)


        current_data = data.get(
            "current",
            {}
        )


        hourly_data = data.get(
            "hourly",
            {}
        )


        daily_data = data.get(
            "daily",
            {}
        )


        # ----------------------------------------------------
        # CURRENT RAIN PROBABILITY
        # ----------------------------------------------------

        rain_probability = None

        hourly_times = hourly_data.get(
            "time",
            []
        )

        rain_values = hourly_data.get(
            "precipitation_probability",
            []
        )


        current_time = current_data.get(
            "time",
            ""
        )


        if hourly_times and rain_values:
            # The hourly forecast timestamps may not exactly match the
            # current observation timestamp. Prefer exact match, otherwise
            # use the forecast hour closest to the current local time.
            matching_indices = [
                index
                for index, time_value in enumerate(hourly_times)
                if time_value == current_time
            ] if current_time else []

            if matching_indices:
                index = matching_indices[0]
            else:
                index = 0
                if current_time:
                    try:
                        current_dt = datetime.fromisoformat(current_time)
                        valid_times = []
                        for i, time_value in enumerate(hourly_times):
                            try:
                                forecast_dt = datetime.fromisoformat(time_value)
                                valid_times.append((abs((forecast_dt - current_dt).total_seconds()), i))
                            except (TypeError, ValueError):
                                continue
                        if valid_times:
                            index = min(valid_times)[1]
                    except (TypeError, ValueError):
                        index = 0

            if index < len(rain_values):
                rain_probability = rain_values[index]


        # ----------------------------------------------------
        # CURRENT WEATHER OBJECT
        # Compatible with the existing frontend
        # ----------------------------------------------------

        current_weather = {

            "temperature": current_data.get(
                "temperature_2m"
            ),

            "relative_humidity": current_data.get(
                "relative_humidity_2m"
            ),

            "rain_probability": rain_probability,

            "precipitation": current_data.get(
                "precipitation"
            ),

            "wind_speed": current_data.get(
                "wind_speed_10m"
            ),

            "time": current_time

        }


        # ----------------------------------------------------
        # WEATHER-BASED FARMING ADVICE
        # ----------------------------------------------------

        farming_advice = get_weather_farming_advice(

            current_weather["temperature"],

            current_weather["relative_humidity"],

            current_weather["rain_probability"],

            current_weather["wind_speed"]

        )


        # ----------------------------------------------------
        # BUILD DAILY FORECAST
        # ----------------------------------------------------

        daily_forecast = []


        dates = daily_data.get(
            "time",
            []
        )


        for index, forecast_date in enumerate(
            dates
        ):

            def get_daily_value(key):

                values = daily_data.get(
                    key,
                    []
                )

                if index < len(values):

                    return values[index]

                return None


            daily_forecast.append({

                "date": forecast_date,

                "weather_code": get_daily_value(
                    "weather_code"
                ),

                "temperature_max": get_daily_value(
                    "temperature_2m_max"
                ),

                "temperature_min": get_daily_value(
                    "temperature_2m_min"
                ),

                "rain_probability": get_daily_value(
                    "precipitation_probability_max"
                ),

                "precipitation_sum": get_daily_value(
                    "precipitation_sum"
                ),

                "wind_speed_max": get_daily_value(
                    "wind_speed_10m_max"
                )

            })


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "location": {

                "latitude": data.get(
                    "latitude"
                ),

                "longitude": data.get(
                    "longitude"
                ),

                "timezone": data.get(
                    "timezone",
                    "auto"
                )

            },

            "current": current_weather,

            "daily_forecast": daily_forecast,

            "farming_advice": farming_advice

        })


    except (HTTPError, URLError, TimeoutError) as error:

        app.logger.warning(
            "Weather forecast API error: %s",
            error
        )

        return jsonify({

            "success": False,
            "error": (
                "Weather service is temporarily unavailable. "
                "Please try again later."
            )

        }), 503


    except Exception:

        app.logger.exception(
            "Unexpected weather forecast error"
        )

        return jsonify({

            "success": False,
            "error": "Unable to retrieve weather information."

        }), 500

if __name__ == "__main__":

    print()

    print("=" * 60)

    print("KISAN MITRA AI - WEB SERVER")

    print("=" * 60)

    print()

    print("🚀 Server starting...")

    print("🌐 Open: http://127.0.0.1:5000")

    print(
        "Gemini:",
        "Connected"
        if gemini_client
        else "Not configured"
    )

    if gemini_client:
        print("🧠 Gemini models:", ", ".join(GEMINI_MODELS))
        print("🔁 Retry count:", GEMINI_RETRY_COUNT)

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )

