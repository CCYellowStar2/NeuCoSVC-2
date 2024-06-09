import re, os
import requests
import json
import torch
import time
import urllib.request
#urllib.request.urlretrieve("https://download.openxlab.org.cn/repos/file/Kevin676/NeuCoSVC-2/main?filepath=WavLM-Large.pt&sign=971a42d686a15fcd3aafae29c1c97220&nonce=1715413418821", "ckpt/WavLM-Large.pt")
#urllib.request.urlretrieve("https://cdn-lfs-us-1.huggingface.co/repos/39/6c/396c5940f123f7b55c7446e10b2e81545db6b5ac9e2e9c70818210002923f9f7/e7b1a67aef7d681ba7a85f60e5760e006f1fc4fd834e001f16aad5f3188f98b1?response-content-disposition=attachment%3B+filename*%3DUTF-8%27%27G_150k.pt%3B+filename%3D%22G_150k.pt%22%3B&Expires=1718168200&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTcxODE2ODIwMH19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy11cy0xLmh1Z2dpbmdmYWNlLmNvL3JlcG9zLzM5LzZjLzM5NmM1OTQwZjEyM2Y3YjU1Yzc0NDZlMTBiMmU4MTU0NWRiNmI1YWM5ZTJlOWM3MDgxODIxMDAwMjkyM2Y5ZjcvZTdiMWE2N2FlZjdkNjgxYmE3YTg1ZjYwZTU3NjBlMDA2ZjFmYzRmZDgzNGUwMDFmMTZhYWQ1ZjMxODhmOThiMT9yZXNwb25zZS1jb250ZW50LWRpc3Bvc2l0aW9uPSoifV19&Signature=lGtg0oQ4JcwuSQOy8T65PJTLHDgo4EYKc-Rnyx7-nIMUtxLxQFDw3gxivKpHEdZRGV3AHk8kWYRlWABRKvNi-lii%7Ee39UWuwXQLwfn0jhVidkQzzT8FZyj10BWU2bGDCvHFBixp81iyPUEhlSpK6CMRg4r1oC14QO859pJd5BYUHFsmODMxaLxrls0fhjMy%7ErOrJuBhMPZEML%7EU8M8RooVNd0z0Aw379uuhTH0mArkw7MOGlOGQaAjh2lh2lKVsYhS-jSbDpVJ9UHMAaYt1fIoeQGOjiwc4JotSFP8MAXgTFLbjNlqb8vmdjJJnTaUKBGpr-6JTAD15kv3eUtFDZwQ__&Key-Pair-Id=KCD77M1F0VK2B", "ckpt/G_150k.pt")
#urllib.request.urlretrieve("https://download.openxlab.org.cn/repos/file/Kevin676/NeuCoSVC-v2/main?filepath=speech_XXL_cond.zip&sign=0520b3273355818d1ebee030bce88ee4&nonce=1715413443250", "speech_XXL_cond.zip")
#urllib.request.urlretrieve("https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/5_HP-Karaoke-UVR.pth", "uvr5/uvr_model/5_HP-Karaoke-UVR.pth")
#urllib.request.urlretrieve("https://download.openxlab.org.cn/models/Kevin676/rvc-models/weight/UVR-HP5.pth", "uvr5/uvr_model/UVR-HP5.pth")

def download_file_openxlab(url, destination):
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(destination, 'wb') as f:
                    f.write(response.content)
                print("File downloaded successfully!")
                break
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error occurred: {e}")
        
        print("Retrying in 5 seconds...")
        time.sleep(5)

url_wavlm = "https://modelscope.cn/api/v1/models/Kevin676/neuco2/repo?Revision=master&FilePath=WavLM-Large.pt"
destination_wavlm = "ckpt/WavLM-Large.pt"

url_uvr = "https://modelscope.cn/api/v1/models/CCYellowStar/5_HP-Karaoke-UVR/repo?Revision=master&FilePath=5_HP-Karaoke-UVR.pth"
destination_uvr = "uvr5/uvr_model/5_HP-Karaoke-UVR.pth"

url_G_150k = "https://modelscope.cn/api/v1/models/Kevin676/neuco2/repo?Revision=master&FilePath=G_150k.pt"
destination_G_150k = "ckpt/G_150k.pt"

url_speech = "https://modelscope.cn/api/v1/models/Kevin676/neuco2/repo?Revision=master&FilePath=speech_XXL_cond.zip"
destination_speech = "speech_XXL_cond.zip"

download_file_openxlab(url_wavlm, destination_wavlm)
download_file_openxlab(url_uvr, destination_uvr)
download_file_openxlab(url_G_150k, destination_G_150k)
download_file_openxlab(url_speech, destination_speech)

import zipfile
with zipfile.ZipFile("speech_XXL_cond.zip", 'r') as zip_ref:
    zip_ref.extractall("Phoneme_Hallucinator_v2/exp")

device = 'cuda' if torch.cuda.is_available() else 'cpu'

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
pattern = r'//www\.bilibili\.com/video[^"]*'

def get_bilibili_video_id(url):
    match = re.search(r'/video/([a-zA-Z0-9]+)/', url)
    extracted_value = match.group(1)
    return extracted_value

# Get bilibili audio
def find_first_appearance_with_neighborhood(text, pattern):
    match = re.search(pattern, text)

    if match:
        return match.group()
    else:
        return None

def search_bilibili(keyword):
    if keyword.startswith("BV"):
      req = requests.get("https://search.bilibili.com/all?keyword={}&duration=1".format(keyword), headers=headers).text
    else:
      req = requests.get("https://search.bilibili.com/all?keyword={}&duration=1&tids=3&page=1".format(keyword), headers=headers).text
    print(keyword)
    video_link = "https:" + find_first_appearance_with_neighborhood(req, pattern)

    return video_link

def get_response(html_url):
  headers = {
      "referer": "https://www.bilibili.com/",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
  }
  response = requests.get(html_url, headers=headers)
  return response

def get_video_info(html_url):
  response = get_response(html_url)
  html_data = re.findall('<script>window.__playinfo__=(.*?)</script>', response.text)[0]
  json_data = json.loads(html_data)
  if json_data['data']['dash']['audio'][0]['backupUrl']!=None:
    audio_url = json_data['data']['dash']['audio'][0]['backupUrl'][0]
  else:
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
  video_url = json_data['data']['dash']['video'][0]['baseUrl']
  return audio_url, video_url

def save_audio(title, html_url):
  audio_url = get_video_info(html_url)[0]
  #video_url = get_video_info(html_url)[1]

  audio_content = get_response(audio_url).content
  #video_content = get_response(video_url).content

  with open(title + '.mp3', mode='wb') as f:
    f.write(audio_content)
  print("音乐内容保存完成")
  #with open(title + '.mp4', mode='wb') as f:
  #  f.write(video_content)
  #print("视频内容保存完成"

from uvr5.vr import AudioPre
weight_uvr5_root = "uvr5/uvr_model"
uvr5_names = []
for name in os.listdir(weight_uvr5_root):
    if name.endswith(".pth") or "onnx" in name:
        uvr5_names.append(name.replace(".pth", ""))

func = AudioPre
pre_fun_hp2 = func(
  agg=int(10),
  model_path=os.path.join(weight_uvr5_root, "5_HP-Karaoke-UVR.pth"),
  device=device,
  is_half=True,
)

pre_fun_hp5 = func(
  agg=int(10),
  model_path=os.path.join(weight_uvr5_root, "5_HP-Karaoke-UVR.pth"),
  device=device,
  is_half=True,
)

import webrtcvad
from pydub import AudioSegment
from pydub.utils import make_chunks

import os
import librosa
import soundfile
import gradio as gr


def vad(audio_name):
  audio = AudioSegment.from_file(audio_name, format="wav")
  # Set the desired sample rate (WebRTC VAD supports only 8000, 16000, 32000, or 48000 Hz)
  audio = audio.set_frame_rate(48000)
  # Set single channel (mono)
  audio = audio.set_channels(1)

  # Initialize VAD
  vad = webrtcvad.Vad()
  # Set aggressiveness mode (an integer between 0 and 3, 3 is the most aggressive)
  vad.set_mode(3)

  # Convert pydub audio to bytes
  frame_duration = 30  # Duration of a frame in ms
  frame_width = int(audio.frame_rate * frame_duration / 1000)  # width of a frame in samples
  frames = make_chunks(audio, frame_duration)

  # Perform voice activity detection
  voiced_frames = []
  for frame in frames:
      if len(frame.raw_data) < frame_width * 2:  # Ensure frame is correct length
          break
      is_speech = vad.is_speech(frame.raw_data, audio.frame_rate)
      if is_speech:
          voiced_frames.append(frame)

  # Combine voiced frames back to an audio segment
  voiced_audio = sum(voiced_frames, AudioSegment.silent(duration=0))

  voiced_audio.export("voiced_audio.wav", format="wav")




def youtube_downloader(
    video_identifier,
    filename,
    split_model,
    start_time
):
    print(video_identifier)
    video_info = get_video_info(video_identifier)[0]
    print(video_info)
    audio_content = get_response(video_info).content
    with open(filename.strip() + ".wav", mode="wb") as f:
        f.write(audio_content)
    audio_path = filename.strip() + ".wav"
    start_ms = start_time * 1000
    end_ms = start_ms + 60000
      # make dir output
    os.makedirs("output", exist_ok=True)

    if split_model=="UVR-HP2":
        pre_fun = pre_fun_hp2
    else:
        pre_fun = pre_fun_hp5

    audio_orig = AudioSegment.from_file(audio_path)
    if len(audio_orig) >= end_ms:

      # Extract the segment
      segment = audio_orig[start_ms:end_ms]
      segment.export(filename.strip() + ".wav", format="wav")
      pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      os.remove(filename.strip()+".wav")
    elif len(audio_orig) >= 60000:
      segment = audio_orig[len(audio_orig)-60000:len(audio_orig)]
      segment.export(filename.strip() + ".wav", format="wav")
      pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      os.remove(filename.strip()+".wav")
    elif len(audio_orig) < 60000:
      segment = audio_orig[0:len(audio_orig)]
      segment.export(filename.strip() + ".wav", format="wav")
      pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      os.remove(filename.strip()+".wav")


    return f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav", f"./output/{split_model}/{filename}/instrument_{filename}.wav_10.wav"


def youtube_downloader_100s(
    video_identifier,
    filename,
    split_model
):
    print(video_identifier)
    video_info = get_video_info(video_identifier)[0]
    print(video_info)
    audio_content = get_response(video_info).content
    with open(filename.strip() + ".wav", mode="wb") as f:
        f.write(audio_content)
    audio_path = filename.strip() + ".wav"
    if split_model=="UVR-HP2":
        pre_fun = pre_fun_hp2
    else:
        pre_fun = pre_fun_hp5

    os.makedirs("output", exist_ok=True)
    audio_orig = AudioSegment.from_file(audio_path)

    if len(audio_orig) > 200000:
      start_ms = 30000
      end_ms = start_ms + 170000

      # Extract the segment

      segment = audio_orig[start_ms:end_ms]

      segment.export(filename.strip() + ".wav", format="wav")
      if os.path.exists(f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav"):
        audio_orig1 = AudioSegment.from_file(f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav")
        audio_orig = AudioSegment.from_file(audio_path)
        if len(audio_orig1)+1000 < len(audio_orig):
          pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      else:
        pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      os.remove(filename.strip()+".wav")
    else:
      if os.path.exists(f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav"):
        audio_orig1 = AudioSegment.from_file(f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav")
        if len(audio_orig1)+1000 < len(audio_orig):
          pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      else:
        pre_fun._path_audio_(filename.strip() + ".wav", f"./output/{split_model}/{filename}/", f"./output/{split_model}/{filename}/", "wav")
      os.remove(filename.strip()+".wav")

    return f"./output/{split_model}/{filename}/vocal_{filename}.wav_10.wav", f"./output/{split_model}/{filename}/instrument_{filename}.wav_10.wav"


def convert(start_time, song_name_src, song_name_ref, src_audio, ref_audio, check_song, auto_key, key_shift, vocal_vol, inst_vol):
  split_model = "UVR-HP5"
  #song_name_ref = song_name_ref.strip().replace(" ", "")
  #video_identifier = search_bilibili(song_name_ref)
  #song_id = get_bilibili_video_id(video_identifier)
  if src_audio is None:
      song_name_src = song_name_src.strip().replace(" ", "")
      video_identifier_src = search_bilibili(song_name_src)
      song_id_src = get_bilibili_video_id(video_identifier_src)
      audio_src, sr_src = librosa.load(youtube_downloader(video_identifier_src, song_id_src, split_model, start_time)[0], sr=24000, mono=True)
      soundfile.write("audio_src.wav", audio_src, sr_src)
  else:
      src_audio_orig = AudioSegment.from_file(src_audio)
      if len(src_audio_orig) > 45000:
          segment = src_audio_orig[0:45000]
          segment.export("segment.wav", format="wav")
          multi_channel_audio = AudioSegment.from_file("segment.wav", format="wav")
          mono_audio = multi_channel_audio.set_channels(1)
          mono_audio.export("audio_src.wav", format="wav")
      else:
          multi_channel_audio = AudioSegment.from_file(src_audio, format="wav")
          mono_audio = multi_channel_audio.set_channels(1)
          mono_audio.export("audio_src.wav", format="wav")

  if ref_audio is None:
      song_name_ref = song_name_ref.strip().replace(" ", "")
      video_identifier = search_bilibili(song_name_ref)
      song_id = get_bilibili_video_id(video_identifier)
      if os.path.isdir(f"./output/{split_model}/{song_id}")==False:
        audio, sr = librosa.load(youtube_downloader_100s(video_identifier, song_id, split_model)[0], sr=24000, mono=True)
        soundfile.write("audio_ref.wav", audio, sr)
      else:
        audio_orig = AudioSegment.from_file(f"./output/{split_model}/{song_id}/vocal_{song_id}.wav_10.wav")
        if len(audio_orig) > 60000:
          audio, sr = librosa.load(f"./output/{split_model}/{song_id}/vocal_{song_id}.wav_10.wav", sr=24000, mono=True)
          soundfile.write("audio_ref.wav", audio, sr)
        else:
          audio, sr = librosa.load(youtube_downloader_100s(video_identifier, song_id, split_model)[0], sr=24000, mono=True)
          soundfile.write("audio_ref.wav", audio, sr)
    
      vad("audio_ref.wav")
  else:   
      vad(ref_audio)



  #if os.path.isdir(f"./output/{split_model}/{song_id_src}")==False:
  #audio_src, sr_src = librosa.load(youtube_downloader(video_identifier_src, song_id_src, split_model, start_time)[0], sr=24000, mono=True)
  #soundfile.write("audio_src.wav", audio_src, sr_src)
  #else:
  #  audio_src, sr_src = librosa.load(f"./output/{split_model}/{song_id_src}/vocal_{song_id_src}.wav_10.wav", sr=24000, mono=True)
  #  soundfile.write("audio_src.wav", audio_src, sr_src)
  if os.path.isfile("output_svc/NeuCoSVCv2.wav"):
    os.remove("output_svc/NeuCoSVCv2.wav")

  if check_song == True:
      if auto_key == True:
          os.system(f"python inference.py --src_wav_path audio_src.wav --ref_wav_path voiced_audio.wav --key_shift 100")
      else:
          os.system(f"python inference.py --src_wav_path audio_src.wav --ref_wav_path voiced_audio.wav --key_shift {key_shift}")
 
  else:
      if auto_key == True:
          os.system(f"python inference.py --src_wav_path audio_src.wav --ref_wav_path voiced_audio.wav --speech_enroll --key_shift 100")
      else:
          os.system(f"python inference.py --src_wav_path audio_src.wav --ref_wav_path voiced_audio.wav --key_shift {key_shift} --speech_enroll")

  if src_audio is None:
      audio_vocal = AudioSegment.from_file("output_svc/NeuCoSVCv2.wav", format="wav")
    
      # Load the second audio file
      audio_inst = AudioSegment.from_file(f"output/{split_model}/{song_id_src}/instrument_{song_id_src}.wav_10.wav", format="wav")
    
      audio_vocal = audio_vocal + vocal_vol  # Increase volume of the first audio by 5 dB
      audio_inst = audio_inst + inst_vol  # Decrease volume of the second audio by 5 dB
    
      # Concatenate audio files
      combined_audio = audio_vocal.overlay(audio_inst)
    
      # Export the concatenated audio to a new file
      combined_audio.export(f"{song_name_src}-AI翻唱.mp3", format="MP3")
    
      return f"{song_name_src}-AI翻唱.mp3"
  else:
      return "output_svc/NeuCoSVCv2.wav"



app = gr.Blocks()


with app:
  gr.Markdown("# <center>🥳💕🎶 NeuCoSVC v2 AI歌手全明星，无需训练、一键翻唱、重磅更新！</center>")
  gr.Markdown("## <center>🌟 只需 1 个歌曲名，一键翻唱任意歌手的任意歌曲，支持说话语音翻唱，随时随地，听你想听！</center>")
  gr.Markdown("### <center>🌊 [NeuCoSVC v2](https://github.com/thuhcsi/NeuCoSVC) 先享版 Powered by Tencent ARC Lab & Tsinghua University 💕</center>")
  with gr.Row():
    with gr.Column():
      with gr.Row():
        inp1 = gr.Textbox(label="请填写想要AI翻唱的歌曲或BV号", placeholder="七里香 周杰伦", info="直接填写BV号的得到的歌曲最匹配，也可以选择填写“歌曲名+歌手名”")
        inp2 = gr.Textbox(label="请填写含有目标音色的歌曲或BV号", placeholder="遇见 孙燕姿", info="例如您希望使用AI周杰伦的音色，就在此处填写周杰伦的任意一首歌")
      with gr.Row():
        inp0 = gr.Number(value=0, label="起始时间 (秒)", info="此程序将自动从起始时间开始提取45秒的翻唱歌曲")
        inp3 = gr.Checkbox(label="参考音频是否为歌曲演唱，默认为是", info="如果参考音频为正常说话语音，请取消打勾", value=True)
        inp4 = gr.Checkbox(label="是否自动预测歌曲人声升降调，默认为是", info="如果需要手动调节歌曲人声升降调，请取消打勾", value=True)
      with gr.Row():
        inp5 = gr.Slider(minimum=-12, maximum=12, value=0, step=1, label="歌曲人声升降调", info="默认为0，+2为升高2个key，以此类推")
        inp6 = gr.Slider(minimum=-3, maximum=3, value=0, step=1, label="调节人声音量，默认为0")
        inp7 = gr.Slider(minimum=-3, maximum=3, value=0, step=1, label="调节伴奏音量，默认为0")
      btn = gr.Button("一键开启AI翻唱之旅吧💕", variant="primary")
    with gr.Column():
      with gr.Row():
        src_audio = gr.Audio(label="从本地上传一段想要AI翻唱的音频。需要为去除伴奏后的音频，此程序将自动提取前45秒的音频；如果您希望通过歌曲名搜索在线音频，请勿在此上传音频文件", type="filepath", interactive=True)
        ref_audio = gr.Audio(label="从本地上传一段音色参考音频。需要为去除伴奏后的音频，建议上传长度为60~90s左右的.wav文件；如果您希望通过歌曲名搜索在线音频，请勿在此上传音频文件", type="filepath", interactive=True)
      out = gr.Audio(label="AI歌手为您倾情演唱的歌曲🎶", type="filepath", interactive=False)

  btn.click(convert, [inp0, inp1, inp2, src_audio, ref_audio, inp3, inp4, inp5, inp6, inp7], out)

  gr.Markdown("### <center>注意❗：请不要生成会对个人以及组织造成侵害的内容，此程序仅供科研、学习及个人娱乐使用。</center>")
  gr.HTML('''
      <div class="footer">
                  <p>🌊🏞️🎶 - 江水东流急，滔滔无尽声。 明·顾璘
                  </p>
      </div>
  ''')

#app.queue(max_size=40, api_open=False)
app.launch(share=True, show_error=True)
