from lib import *
import json, requests, time

class App:
    def __init__(self, name):
        self.idx = get_unique_id()
        self.conv = []
        self.name = name

    def run(self):
        ...

    def save_conv(self):
        with open(f"content/{self.idx}-{self.name}.json", "w", encoding="utf-8") as f:
            json.dump(self.conv, f, ensure_ascii=False)

class ChatGen(App):
    def __init__(self):
        super().__init__("chat")

    def run(self):
        chat = client.chats.create(model="gemini-2.5-pro")
        try:
            while True:
                prompt = get_prompt()
                self.conv.append({"role": "user", "content": prompt})
                resp = chat.send_message(prompt)
                prompt("Answer: ", resp.text)
                self.conv.append({"role": "assistant", "content": resp.text})
        except:
            self.save_conv()

from google.genai.types import (
    GenerateContentConfig,
    Modality,
    ImageConfig
)

class ImageGen(App):
    def __init__(self):
        super().__init__("image")
        self.ratio = "16:9"

    def run(self):
        prompt = get_prompt()
        image_name = get_prompt("Image Name: ")
        contents = [prompt]
        self.conv.append({"role": "user", "content": prompt})
        if image_name: contents.append(Image.open(f"data/{image_name}"))

        resp = client.models.generate_content(
            model = "gemini-2.5-flash-image-preview",
            contents = contents,
            config = GenerateContentConfig(
                response_modalities=[Modality.IMAGE],
                image_config=ImageConfig(
                    aspect_ratio=self.ratio
                )
            )
        )
        self.conv.append({"role": "assistant", "content": resp.text})

        image_parts = [
            part.inline_data.data
            for part in resp.candidates[0].content.parts
            if part.inline_data
        ]
        if image_parts:
            image = Image.open(BytesIO(image_parts[0]))
            image_path = f"data/{self.idx}.png"
            image.save(image_path)
            image.show()
        
        self.save_conv()


class VideoGen(App):
    def __init__(self):
        super().__init__("video")
        self.ratio = "16:9"
        self.headers = headers
        self.headers["x-goog-api-key"] = api_key

    def create(self, prompt, neg_prompt, image_name):
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
                "aspectRatio": "16:9",
                "resolution": "1080p",
                "personGeneration": "allow_adult"
            }
        }
        try:
            resp = requests.post(url, headers=self.headers, json=data)
            resp.raise_for_status()
            print("Operation: ", resp.json())
        except Exception as e:
            print(e)
        
        return resp.json()["name"]
    

    def check(self, opname: str):
        url = base_url + "/gemini/v1beta/" + opname
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        data = resp.json()
        if "done" in data:
            return True, data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]
        return False, data
    
    def download(self, file_id: str):
        url = base_url + f"/gemini/download/v1beta/files/{file_id}:download?alt=media"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        with open(f"data/{self.idx}.mp4", "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        print("Video saved to ", self.idx)

    
    def run(self):
        prompt = get_prompt()
        neg_prompt = get_prompt("Negative: ")
        image_name = get_prompt("Image: ")
        self.conv.append({"role": "user", "content": prompt})
        opname = self.create(prompt, neg_prompt, image_name)
        obj = None
        while True:
            time.sleep(10)
            status, obj = self.check(opname)
            if status: break

        uri: str = obj["uri"]
        file_id = uri.split("/")[-1].split(":")[0]
        self.download(file_id)
        self.save_conv()


        