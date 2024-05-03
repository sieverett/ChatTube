import os
import shutil
import streamlit as st
from pathlib import Path
from datetime import datetime
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from mutagen.mp3 import MP3
from tqdm import tqdm
from dotenv import load_dotenv
from elevenlabs import Voice
from elevenlabs import save, VoiceSettings
from youtubesearchpython import *
from tqdm import tqdm
import pandas as pd
from typing import List
import csv
import json
from pathlib import Path
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
from openai import AzureOpenAI
# from elevenlabs import set_api_key
# pip install youtube-search-python
from youtubesearchpython import VideosSearch
# from langchain_openai import AzureChatOpenAI
# pip install youtube-transcript-api
from youtube_transcript_api import YouTubeTranscriptApi
# from utils_extension import list_cloned_voices
import uuid
import openai
# from docx import Document
# import docx2pdf
from fpdf import FPDF
from PyPDF2 import PdfMerger
from dotenv import load_dotenv
load_dotenv('.env')

global eleven_client

eleven_client = ElevenLabs(
    api_key=os.getenv("ELEVEN_API_KEY")
)


def capitalize_names(names):
    names = [" ".join([i.capitalize() for i in g.split(" ")])
             for g in names if g != 'na']
    return names


def get_youtube_video_ids(keyword: str, limit: int = 10) -> List[str]:
    """
    Returns list of video ids we find for the given 'keyword'
    """
    video_search = VideosSearch(keyword, limit=limit)
    results = video_search.result()['result']
    return [r['id'] for r in results]


def get_persona_status(presenter):
    content = []
    status = {}
    root = f'RI/personas/{presenter}'
    for path, subdirs, files in os.walk(root):
        for name in files:
            # print(os.path.join(path, name))
            content.append(os.path.join(path, name))
    content = [Path(c).as_posix() for c in content]
    # status["transcript"] = f'./RI/personas/{presenter}\\transcripts\\transcript.pdf' in content
    # status["summary"] = f'./RI/personas/{presenter}\\transcripts\\summary.pdf' in content
    # status["segments"] = f'./RI/personas/{presenter}\\audio\\segments\\sample_0_0.mp3' in content
    # status["cloned"] =  presenter in list_cloned_voices().keys()
    # status["vector_store"] = f'./RI/personas/{presenter}\\vector_store\\index.faiss' in content
    status["transcript"] = (Path('./RI') / 'personas' / presenter /
                            'transcripts' / 'transcript.pdf').as_posix() in content
    status["summary"] = (Path('./RI') / 'personas' / presenter /
                         'transcripts' / 'summary.pdf').as_posix() in content
    status["segments"] = (Path('./RI/personas/') / presenter /
                          'audio' / 'segments/' / 'sample_0_0.mp3').as_posix() in content
    status["cloned"] = presenter in list_cloned_voices().keys()
    status["vector_store"] = (Path('./RI/personas') / presenter /
                              'vector_store' / 'index.faiss').as_posix() in content
    return status


def make_file_structure(coach, root_dir='.') -> None:
    coach_dir = f'{root_dir}/personas/{coach}'
    os.makedirs(coach_dir, exist_ok=True)
    # for transcripts
    transcripts_path = coach_dir + '/transcripts/'
    os.makedirs(transcripts_path, exist_ok=True)
    # for audio
    audio_path = coach_dir + '/audio/'
    os.makedirs(audio_path, exist_ok=True)
    # for audio segments
    segments_path = coach_dir+'/audio/segments'
    os.makedirs(segments_path, exist_ok=True)
    # for cloned speech audio
    cloned_path = coach_dir + '/cloned/'
    os.makedirs(cloned_path, exist_ok=True)
    # for vectors
    vector_path = coach_dir + '/cloned/'
    os.makedirs(vector_path, exist_ok=True)


def remove_files(df2):
    """df2 is the dynamic table output"""
    df1 = pd.read_csv('RI/SLT_playlist_info.csv')
    presenters = df1[~df1.apply(tuple, 1).isin(
        df2.apply(tuple, 1))].presenter.values.tolist()
    for presenter in presenters:
        folder = f'RI/personas/{presenter}'
        if Path(folder).is_dir():
            st.write('Here is the folder:', folder)
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    st.error('Failed to delete %s. Reason: %s' %
                             (file_path, e))
            try:
                Path.rmdir(folder)
                st.toast(f'{folder} removed.')
            except Exception as e:
                st.error('Failed to delete %s. Reason: %s' % (folder, e))


def get_youtube_video_transcript(video_id: str) -> str:
    """"
    Returns transcript of the given 'video_id'
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en-US', 'en']
        )
        utterances = [p['text'] for p in transcript]
        return ' '.join(utterances)

    except Exception as e:
        pass


# def get_youtube_video_transcripts(coach, links, transcripts_path):
#     # video_ids=get_youtube_video_ids(coach+' gives advice and coaching', limit = 10)
#     links = [links] if type(links) == str else links
#     video_ids = [i.split('v=')[1] for i in links]
#     transcripts = [get_youtube_video_transcript(id) for id in video_ids]
#     if transcripts is not None:
#         save_transcripts(transcripts, coach, Path(
#             transcripts_path+f'transcript.txt'))

def download_transcript(presenter, link):
    if 'v=' in link:
        video_id = link.split('v=')[1]
    else:
        video_id = link.split('/')[-1]
    transcript = get_youtube_video_transcript(video_id)
    if transcript:
        transcript = f"{presenter} presents the following: {transcript}"
        with open(f'RI/personas/{presenter}/transcripts/transcript.txt', 'w') as f:
            f.write(transcript)
        return True
    else:
        status_dict = get_persona_status(presenter)
        st.toast("Transcript not available for download. Trying Whisper...")
        st.spinner("This could take a few minutes")
        link = st.session_state.presenter_dataframe[
            st.session_state.presenter_dataframe.presenter == presenter].link.values[0]
        if not status_dict.get("segments", True):
            audio_file = download_audio(presenter, link)
            # clip_audio(presenter,audio_file)
            extract_samples(presenter)
        transcript = get_transcription_with_whisper(presenter)


def get_transcription_with_whisper(presenter):
    """
    get_transcription: when captions not in video, 
                    transcribe an audio file using Azure OpenAI
    audio_test_file: path to the audio file
    """
    audio_dir = f'RI/personas/{presenter}/audio/'
    audio_file = sorted([file for file in os.listdir(
        audio_dir) if 'audio_sample' in file])[0]
    audio_file_path = os.path.join(audio_dir, audio_file)
    # audio_test_file = f'RI/personas/{presenter}/audio/audio_sample_{datetime.now().strftime("%Y%m%d")}.mp3'
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_WHISPER_API_KEY"),
        api_version=os.getenv("AZURE_WHISPER_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_WHISPER_ENDPOINT")
    )
    deployment_id = "whisper"
    # This will correspond to the custom name you chose for your deployment when you deployed a model."
    speech = AudioSegment.from_mp3(audio_file_path)
    duration = speech.duration_seconds
    end = 30*60*1000
    start_buffer = 4 * 1000
    chunk_size = 3*60*1000
    l = []
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for i in range(start_buffer, end, chunk_size):
        my_bar.progress(int(i/(duration*1000)), text=progress_text)
        speech[i:i+3*60*1000].export("tmp.mp3", format="mp3")
        result = client.audio.transcriptions.create(
            file=open("tmp.mp3", "rb"),
            model=deployment_id
        )
        l.append(result)
    my_bar.empty()
    transcript = " ".join([text.text for text in l])
    with open(f'RI/personas/{presenter}/transcripts/transcript.txt', 'w') as f:
        f.write(transcript)


def whisper_2_text(audio_file_path):
    speech = AudioSegment.from_mp3(audio_file_path)
    end = speech.duration_seconds
    end = 30*60*1000
    start_buffer = 4 * 1000
    chunk_size = 3*60*1000
    l = []
    for i in range(start_buffer, end, chunk_size):
        print(i)
        speech[i:i+3*60*1000].export("tmp.mp3", format="mp3")
        res = get_transcription_("tmp.mp3")
        l.append(res)
    transcript = " ".join([text.text for text in l])
    with open('RI/personas/Najia Hyder/transcripts/transcript.txt', 'w') as f:
        f.write(transcript)


def save_transcripts(transcripts: List[str], keyword: str, path: Path):
    """
    Stores locally in file the transcripts with associated keyword
    """
    output = [{'keyword': keyword, 'text': t}
              for t in transcripts if t is not None]

    # check if path points to a csv or a json file
    if path.suffix == '.csv':
        # save as csv
        keys = output[0].keys()
        with open(path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(output)

    else:
        # save as json
        with open(path, 'w') as output_file:
            json.dump(output, output_file)


def download_audio(presenter, link):
    """
    link: a youtube url
    """
    datetime_str = datetime.now().strftime("%Y%m%d")
    mp3_file = f"audio_sample_{datetime_str}"
    ydl_opts = {
        'outtmpl': f'RI/personas/{presenter}/audio/{mp3_file}',
        'format': 'bestaudio/best',
        'map': '0:a',
        'no-playlist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '1200',
        }],
    }
    try:

        print('full link:', link)
        print('shortened link:', link.split('&list=')[0])
        link = link.split('&list=')[0]
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            return mp3_file + '.mp3'
    except Exception as e:
        print('Error:', e)

# def clip_audio(presenter,audio_file):
#     start_padding = 4 * 1000 # 4 secods * 1000 milliseconds
#     max_length = 30*60*1000    # 30 minutes * 60 seconds * 1000 milliseconds
#     audio_file_path = os.path.join(f'RI/personas/{presenter}/audio', audio_file)
#     speech = AudioSegment.from_mp3(audio_file_path)
#     st.info(audio_file_path)
#     speech[start_padding:max_length].export(audio_file_path, format="mp3")


def extract_samples(presenter, n_samples=3, sample_length=45):
    """
    given a path to an audio file, extract n_samples of length sample_length
    """
    root = f'RI/personas/{presenter}/audio'
    audio_file_paths = sorted([os.path.join(root, name)
                              for name in os.listdir(root) if '.mp3' in name])
    print(audio_file_paths)
    for sample_number, audio_file_path in enumerate(audio_file_paths):
        print(audio_file_path)
        # Load the mp3 file
        audio = MP3(audio_file_path)
        # Get the length in seconds
        length_in_milliseconds = audio.info.length * 1000
        print(f"Length of the audio file in seconds: {length_in_milliseconds}")
        # Load the audio file with pydub
        audio = AudioSegment.from_mp3(audio_file_path)
        increment = sample_length*1000  # seconds to milliseconds
        start_time = length_in_milliseconds / 2
        l = []
        for i in range(n_samples):
            end_time = start_time+increment
            l.append((start_time, end_time))
            start_time = end_time
        for i, (start_time, end_time) in tqdm(enumerate(l)):
            # Extract the segment
            segment = audio[start_time:end_time]
            # Save the segment
            segment.export(
                f"RI/personas/{presenter}/audio/segments/sample_{sample_number}_{i}.mp3", format="mp3")


# def convert_text_to_docx_pdf(presenter, stub='transcript'):
#     text_filepath = f'RI/personas/{presenter}/transcripts/{stub}.txt'
#     docx_filepath = text_filepath.replace('.txt', '.docx')

#     with open(text_filepath) as f:
#         text = f.read()

    # document = Document()
    # document.add_heading(presenter+' video transcript', level=1)
    # document.add_paragraph(text)
    # document.save(docx_filepath)
    # docx2pdf.convert(docx_filepath)

def convert_txt_2_pdf(presenter, stub='transcript'):
    transcript_file = f'RI/personas/{presenter}/transcripts/{stub}.txt'
    pdf = FPDF()
    with open(transcript_file, 'r') as f:
        text = f.read()
    pdf.add_page()
    pdf.set_font('Arial', size=11)
    pdf.write(5, text)
    pdf.output(str(transcript_file).replace(".txt", ".pdf"))

# def build_persona(presenter, link):
#     make_file_structure(presenter, root_dir='RI')
#     download_transcript(presenter, link)
#     convert_text_to_docx_pdf(presenter)
#     download_audio(link)
#     segments_path = extract_samples(n_samples=1, sample_length=300)
#     return segments_path


# def extract_information_from_video(presenter):
#     segments_path = None
#     df = pd.read_csv('RI/SLT_playlist_info.csv')
#     link = df[df.presenter == presenter].link.values[0]
#     make_file_structure(presenter, root_dir='RI')
#     result = download_transcript(presenter, link)
#     if result:
#         convert_txt_2_pdf(presenter)
#         if download_audio(presenter, link):
#             segments_path = extract_samples(presenter, n_samples=1, sample_length=300)
#     return segments_path


def build_top_n_ted_personas(top_n=3):
    RI_sub = pd.DataFrame(pd.read_csv('RI/SLT_playlist_info.csv'))
    for i in RI_sub.head(top_n)[['presenter', 'link']].iterrows():
        presenter = i[1]['presenter']
        link = [i[1]['link'].split('&list')[0]]
        print('Building persona data for', presenter)
        build_persona(presenter, link)


def list_personas(list_n):
    df = pd.read_csv('RI/SLT_playlist_text.csv')
    dict_ = {p: l for p, l in zip(df.presenter[:list_n], df.link[:list_n])}
    return dict_


def clone_voice(presenter, description):
    voice = eleven_client.clone(
        name=presenter,
        description=description,
        files=[f"RI/personas/{presenter}/audio/segments/sample_0_0.mp3"]
    )
    sub = pd.read_csv('RI/SLT_playlist_info.csv')
    sub.loc[sub[sub.presenter == presenter].index,
            'elevenlabs_voice_id'] = voice.voice_id
    return voice


def list_cloned_voices():
    # set_api_key(os.getenv("ELEVEN_API_KEY"))
    # eleven_client = ElevenLabs()
    result = eleven_client.voices.get_all()
    voice_dict = {i.name: i.voice_id for i in [
        v for v in result.voices] if i.category == 'cloned'}
    return voice_dict


def speak(presenter, text):
    voice_dict = list_cloned_voices()
    voice_id = voice_dict[presenter]
    audio = eleven_client.generate(
        text=text,
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(
                stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
        )
    )
    cloned_audio_save_path = f'RI/personas/{presenter}/cloned/audio_cloned_{uuid.uuid4().hex}.wav'
    save(audio, cloned_audio_save_path)
    return cloned_audio_save_path


def create_audio_from_clone(presenter, text):
    voice_dict = list_cloned_voices()
    voice_id = voice_dict[presenter]
    # v1 = Voice.from_id(voice_id)  # voice.voice_id
    audio = eleven_client.generate(text=text,
                                   voice=Voice(
                                       voice_id=voice_id,
                                       settings=VoiceSettings(
                                           stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
                                   ))
    # audio = generate(text=text, voice=v1, model="eleven_turbo_v2")
    datetime_str = datetime.now().strftime("%Y%m%d")
    cloned_audio_save_path = f'RI/personas/{presenter}/cloned/audio_cloned_{datetime_str}.wav'
    save(audio, cloned_audio_save_path)
    return cloned_audio_save_path

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--list_personas", help="List TED presenters? - True or False")
#     parser.add_argument("--list_cloned_voices", help="List cloned voices? - True or False")
#     parser.add_argument("--presenter", help="Name of TED presenter to clone - First and Last Name lower case")
#     parser.add_argument("--text", help="A sentence to be spoken by cloned voice")
#     args = parser.parse_args()

#     if args.list_personas=='True':
#         personas=list_personas(list_n=99)
#         [print(p) for p in personas.keys() if p!='na']
#         sys.exit()

#     if args.list_cloned_voices=='True':
#         list_cloned_voices()
#         sys.exit()

#     if args.presenter is None:
#         print('ERROR: Please enter a presenter name.')
#         sys.exit()
#     elif args.text is None:
#         print(f'ERROR: text needed.  Add some text for {args.presenter} to utter.')
#         sys.exit()
#     else:
#         presenter=args.presenter
#         personas=list_personas(list_n=20)
#         list_cloned_voices() # updates voice_dict
#         link=personas[presenter]
#         build_persona(presenter,link)
#         description=f'{presenter} is a TED speaker and has a lot of views on YouTube.'
#         clone_voice(presenter,description,segments_path)
#         create_audio_from_clone(presenter,args.text,play_=True)
