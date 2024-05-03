# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# import sys
# bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
# modpath = os.sep.join(bp + ['Hello'])
# sys.path.insert(0, modpath)
# sys.path.append('/workspaces/hello/')
import os
import streamlit as st
import pandas as pd
from elevenlabs import Voice, play, save
from elevenlabs.client import ElevenLabs
from utils import (list_cloned_voices,
                   create_audio_from_clone)

eleven_client = ElevenLabs(
    api_key=os.getenv("ELEVEN_API_KEY")
)
# @st.cache(allow_output_mutation=True)


def run():
    st.set_page_config(layout="wide")

    st.title('SLT Talks!')

    # response = eleven_client.voices.get_all()

    # st.text([voice.name for voice in response.voices if voice.category == 'cloned'])

    cloned_dict = list_cloned_voices()
    cloned_names = list(cloned_dict.keys())
    # cloned_names_caps=capitalize_names(cloned_names)

    df = pd.read_csv("RI/SLT_playlist_info.csv")
    # Extract names for the dropdown
    names = df.presenter.tolist()

    cloned_names = [n for n in cloned_names if n in names]

    selected_name = st.selectbox("Select SLT Presenter", cloned_names)
    # selected_name_lower = selected_name.lower()
    if selected_name:
        # Replace with your CSV file path
        link_dict = {k: v for k, v in zip(df.presenter, df.link)}
        try:
            video_link = link_dict[selected_name]
            _, container, _ = st.columns([20, 40, 20])
            container.video(video_link)
        except KeyError as e:
            st.write(f"You selected: {selected_name}")
            st.write('No video available.')
            st.write(e)
    # Text input for user's text (up to 100 words)
    st.session_state.input_text = ''
    user_input = st.text_area(
        "Enter your text (up to 100 words)", max_chars=1000)

    # Submit button
    if st.button('Submit Text'):
        # Display the text in bold
        if selected_name == None:
            st.alert('Please select a presenter.')
        else:
            with st.spinner('Generating ...'):
                # v1=Voice.from_id(voice_id) # voice.voice_id
                audio_file_path = create_audio_from_clone(
                    selected_name, user_input)
                # audio=generate(text=user_input, voice=v1, model="eleven_turbo_v2")
                # play(audio)
                st.audio(audio_file_path)
                st.session_state.input_text = ''

            # audio_file_path = 'generated_audio.mp3'
            # save(audio, audio_file_path)

    if st.button('Download Audio'):
        with open(audio_file_path, "rb") as file:
            st.download_button(
                label="Download Audio",
                data=file,
                file_name="generated_audio.mp3",
                mime="audio/mpeg"
            )


if __name__ == "__main__":
    run()
