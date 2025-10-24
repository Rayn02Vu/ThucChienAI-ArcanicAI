from lib import *
import json

class App():
    def __init__(self, name):
        self.name = name
        self.conv = []
        self.idx = get_unique_id()

    def run(self):
        ...

    def save_conv(self):
        with open(f"content/{self.idx}-{self.name}", "w", encoding="utf-8") as f:
            json.dump(self.conv, f, ensure_ascii=False)


class Chat(App):
    def __init__(self):
        super().__init__("chat")
    
    def run(self):
        chat = client.chats.create(model="gemini-2.5-pro")
        while True:
            prompt = get_prompt()
            resp = chat.send_message(prompt)
            print(resp.text)

from google.genai.types import (
    GenerateContentConfig,
    Modality,
    ImageConfig
)

class Image(App):
    def  __init__(self):
        super().__init__("image")

    def run(self):
        prompt = get_prompt()
        image_name = get_prompt("Image Name: ")
        ratio = get_prompt("Ratio: ")
        
        contents = [prompt]

        if image_name: contents.append(Image.open(f"data/{image_name}"))

        resp = client.models.generate_content(
            model = "gemini-2.5-flash-image-preview",
            contents = contents,
            config = GenerateContentConfig(
                response_modalities=[Modality.IMAGE],
                image_config=ImageConfig(
                    aspect_ratio=ratio
                )
            )
        )

        image_parts = [
            part.inline_data.data
            for part in resp.candidates[0].content.parts
            if part.inline_data
        ]

        if image_parts:
            image = Image.open(BytesIO(image_parts[0]))
            image.save(f"data/{self.idx}")
            image.show()


class Video(App):
    def __init__(self):
        super().__init__("video")
        self.ratio = "16:9"
        self.headers = headers
        self.headers['x-goog-api-key'] = api_key

    def create(self, prompt, neg_prompt, image_name, ratio):
        url = base_url + "/gemini/v1beta/models/veo-3.0-generate-001:predictLongRunning"

        data = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": get_base64_data(image_name),
                    "mimeType": "image/png"
                }
            }],
            "parameters": {
                "negativePrompt": neg_prompt,
                "aspectRatio": ratio,
                "resolution": "1080p",
                "personGeneration": "allow_adult"
            }
        }

        resp = requests.post(url, headers=self.headers)

        return resp.json()["name"]
    

    def check(self, opname: str):
        url = base_url + "/gemini/v1beta/" + opname
        resp = requests.get(url, headers=self.headers)
        data = resp.json()
        if "done" in data:
            return True, data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]
        return False, opname
    

    def download(self, file_id):
        url = base_url + f"gemini/download/v1beta/files/{file_id}:download?alt=media"
        resp = requests.get(url, headers=self.headers)

        with open("data/" + self.idx + ".mp4", "wb") as f:
            for chunk in resp.iter_content(chunk_size=8000):
                f.write(chunk)

        print("Video downloaded to ", self.idx)

    
    def run(self):
        prompt = get_prompt()
        neg_prompt = get_prompt("Negative: ")
        image_name = get_prompt("Image Name: ")
        
        opname = self.create(prompt, neg_prompt, image_name, self.ratio)

        obj = None

        while True:
            status, resp = self.check(opname)
            print(resp)
            if status:
                obj = resp
                break
        
        uri: str = obj["uri"]
        file_id = uri.split("/")[-1].split(":")[0]
        self.download(file_id)
