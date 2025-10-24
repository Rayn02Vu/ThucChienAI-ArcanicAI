CHAT:
client.chats
prompt
response.text

IMAGE:
prompt
image
ratio
client.models.generate_content(
    model = "gemini-2.5-flash-image-preview",
    contents = [prompt, image],
    config=GenerateContentConfig(
        response_modalities=[Modality.IMAGE],
        image_config=ImageConfig(aspect_ratio=ratio)
    )
)

SOUND:
prompt
openai
resp = client.autio.speech.create
resp.write_to_file()

VIDEO:
create(prompt, neg_prompt, img, ratio)
post ->

check(opname)
get ->

download(file_id)
get -> resp
open("wb")
for chunk in resp.iter_content(): f.write(chunk)

run()


curl -X POST "https://api.thucchien.ai/gemini/v1beta/models/veo-3.0-generate-001:predictLongRunning" \
-H "Content-Type: application/json" \
-H "x-goog-api-key: <your_api_key>" \
-d '{
  "instances": [{
    "prompt": "A cinematic shot of a baby raccoon wearing a tiny cowboy hat, riding a miniature pony through a field of daisies at sunset.",
    "image": null
  }],
  "parameters": {
    "negativePrompt": "blurry, low quality",
    "aspectRatio": "16:9",
    "resolution": "720p",
    "personGeneration": "allow_all"
  }
}'

