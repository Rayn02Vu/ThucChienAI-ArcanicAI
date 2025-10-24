import os, dotenv, datetime, base64
from io import BytesIO
from PIL import Image
from google import genai

dotenv.load_dotenv()

os.makedirs("data", exist_ok=True)
os.makedirs("content", exist_ok=True)

budget = 50.00

base_url = "https://api.thucchien.ai"

api_key = os.getenv("API_KEY")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_key}"
}

client = genai.Client(
    api_key = api_key,
    http_options = {"base_url": base_url}
)

def get_prompt(label: str = "Prompt: "):
    prompt = input(label)
    if prompt.startswith("content"):
        with open(prompt, "r", encoding="utf-8") as f:
            return f.read()
    return prompt


def get_base64_data(image_name: str):
    image = Image.open(f"data/{image_name}")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")

def get_unique_id():
    return datetime.datetime.now().strftime("%H%M%S")
