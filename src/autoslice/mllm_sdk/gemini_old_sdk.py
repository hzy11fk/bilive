import google.generativeai as genai
from src.config import GEMINI_API_KEY, SLICE_PROMPT
from src.log.logger import scan_log
import time

# the new gemini sdk has the conflicts pydantic version in project, so we use the old one
# https://github.com/google-gemini/deprecated-generative-ai-python

def gemini_generate_title(video_path, artist):

    genai.configure(api_key=GEMINI_API_KEY)

    # 2GB in size, 20GB in total
    # https://github.com/google-gemini/cookbook/blob/28fc33fbc2189a30a682148165ea6049ffa93db0/quickstarts/Video.ipynb
    video_file = genai.upload_file(path=video_path)

    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    # Create the prompt.
    prompt = SLICE_PROMPT

    # Set the model to Gemini Flash.
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    response = model.generate_content([prompt, video_file],
                                    request_options={"timeout": 600})
    # delete the video file
    genai.delete_file(video_file.name)
    scan_log.info("使用 Gemini-2.0-flash 生成切片标题")
    scan_log.info(f"Prompt: {SLICE_PROMPT}")
    scan_log.info(f"生成的切片标题为: {response.text}")
    return response.text