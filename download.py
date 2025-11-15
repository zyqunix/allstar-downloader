import requests
import subprocess
import os

username = str(input("allstar username: "))
count = int(input("amount of clips: "))
concat = str(input("connect all clips (y/n): "))

if concat == "y":
    output_file = str(input("output filename (eg. epic.mp4): "))
    remove_clips = str(input("remove clips after connecting (y/n): "))

API_URL = 'https://api.prod.allstar.dev/graphql'
JSON = {
    "operationName": "getUserClips",
    "variables": {
        "query": username,
        "first": count,
        "sort": "LATEST",
        "orientation": "LANDSCAPE",
        "statuses": [
            "READY",
            "PENDING"
        ],
    },
    "query": "query getUserClips($query: String!, $first: Int!, $sort: ClipSort, $statuses: [ClipStatus!], $orientation: MediaOrientation!) {\n  profile(query: $query) {\n    clips(\n      sort: $sort\n      statuses: $statuses\n      first: $first\n      orientation: $orientation\n    ) {\n      pageInfo {\n        endCursor\n        hasNextPage\n        totalCount\n        startCursor\n        hasPreviousPage\n        __typename\n      }\n      nodes {\n        createdAt\n        game\n        id\n        internalId\n        trackId\n        isPinned\n        previewUrl\n        playerGameIdentifier\n        title\n        shareId\n        status\n        type\n        url(orientation: $orientation)\n        views\n        reactions {\n          count\n          type\n          __typename\n        }\n        moment {\n          id\n          match {\n            outdated\n            __typename\n          }\n          __typename\n        }\n        user {\n          _id\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
}

HEADERS = {
    "origin": "https://allstar.gg",
    "content-type": "application/json"
}

def download(url, name):
    try:
        with requests.get(url=url, stream=True) as response:
            response.raise_for_status()
            with open(name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
    except Exception as e:
        print(e)

def add_clip(clip):
    with open('input.txt', 'a') as input_file:
        input_file.write(f"file '{clip}'\n")

def concat_clips(file, output, delete=False):
    subprocess.call(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"{file}", "-c", "copy", f"{output}"])
    if delete:
        for clip in [c for c in os.listdir() if c.endswith(".mp4") and c != output]:
            os.remove(clip)

req = requests.post(url=API_URL, json=JSON, headers=HEADERS).json()
video_urls = req["data"]["profile"]["clips"]["nodes"]

for video in video_urls:
    video_url = video.get("url")
    if video_url:
        safe_name = f'{video.get("title")} [{video.get("createdAt")}]'.replace(" ", "_").replace("[","").replace("]","")
        print(f"downloading {video.get("title")}")
        download(video_url, f'{safe_name}.mp4')


if concat == "y":
    clips = [c for c in os.listdir('./') if c.endswith(".mp4")]

    open('input.txt', 'w').close()

    for clip in clips:
        print(clip)
        add_clip(clip)

    concat_clips('input.txt', output_file, remove_clips)
