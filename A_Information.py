from pathlib import Path
import streamlit as st
import pandas as pd
from moviepy.editor import *
from streamlit.logger import get_logger
import os
import sys
from dotenv import load_dotenv
# sys.path.append('/workspaces/hello/scripts')
from utils import (clone_voice,
                   convert_txt_2_pdf,
                   get_persona_status,
                   make_file_structure,
                   remove_files,
                   download_transcript,
                   download_audio,
                   extract_samples)
from utils_extension import build_vector_store, get_summary_text
from streamlit_pdf_viewer import pdf_viewer
from io import FileIO
from streamlit_pills import pills
import time
# import asyncio

# loop = asyncio.get_event_loop()

os.environ["APP_ROOT_DIR"] = os.path.dirname(os.path.abspath(__file__))

load_dotenv('.env')

LOGGER = get_logger(__name__)

LOGGER.info(os.getcwd())
cloned_path = ''  # global variable for cloned voice path

if "presenter_dataframe" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.presenter_dataframe = pd.read_csv(
        "RI/SLT_playlist_info.csv")
if "new_name" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.new_name = ""
if "new_link" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.new_link = ""


# def submit():
#     st.session_state.new_name = ""
#     st.session_state.new_link = ""


def run():
    # Display the logo and the title

    st.set_page_config(
        page_title="Chat with the Experts",
        page_icon="🔘",
        layout="wide")

    st.title("Information 📇")

    # Read CSV file
    # if st.button('Click to Extract Information :sparkles:'):
    #     with st.spinner('Wait for it...'):
    #         segments_path = extract_information_from_video(selected_name)
    #         if segments_path:
    #             description = f'{selected_name} is an RI SLT member and has a passionate voice.'
    #             clone_voice(selected_name, description, segments_path)
    #             build_vector_store(selected_name)
    #             st.success(f"{selected_name}'s voice clone complete!")
    #         else:
    #             st.toast(
    #                 f"*Transcript* is absent from {selected_name}'s video.")
    # if st.button('Click to Extract Summary :memo:'):
    #     with st.spinner('Wait for it...'):
    #         summary_text = get_summary_text(selected_name)
    #         convert_txt_2_pdf(selected_name, stub='summary')
    #         st.success(f"{selected_name}'s summary extraction complete!")
    # Read CSV file
    # Replace with your CSV file path
    # df = pd.read_csv("RI/SLT_playlist_info.csv")
    # # Extract names for the dropdown
    # names = df.presenter.tolist()

    # names = [n for n in names if ' And ' not in n]

    with st.sidebar:

        names = st.session_state.presenter_dataframe.presenter.tolist()
        selected_name = st.selectbox("Select Presenter", names)

        # Button to extract and download audio
        video_link = st.session_state.presenter_dataframe[
            st.session_state.presenter_dataframe.presenter == selected_name].link.values[0]

        with st.expander("Add Presenter"):
            # form = st.form("Add")
            # new_name = st.text_input("Presenter Name", key='new_name')
            # new_link = st.text_input(
            #     "Youtube Link", key='new_link')
            # form.submitted = form.form_submit_button("Submit")
            # st.empty()
            # if form.submitted:
            #     st.session_state.presenter_dataframe.loc[-1] = [
            #         new_name, new_link]
            #     st.session_state.presenter_dataframe.reset_index(
            #         drop=True, inplace=True)

            dynamic_table = st.data_editor(
                st.session_state.presenter_dataframe, hide_index=None, num_rows="dynamic")
            dynamic_table.dropna(inplace=True)
            remove_files(dynamic_table)
            st.session_state.presenter_dataframe = dynamic_table
            # st.session_state.presenter_dataframe.dropna(inplace=True)
            st.session_state.presenter_dataframe.to_csv(
                "RI/SLT_playlist_info.csv", index=False)
            st.button("Submit")

    # display video
    # link_dict = {k: v for k, v in zip(
    #    st.session_state.presenter_dataframe.presenter, st.session_state.presenter_dataframe.link)}

    if selected_name:
        status_dict = get_persona_status(selected_name)
        df = st.session_state.presenter_dataframe.copy()
        make_file_structure(selected_name, root_dir='RI')

        with st.expander("Watch Video 📺", expanded=True):
            _, container, _ = st.columns([20, 40, 20])
            if selected_name == 'Craig Redmond':
                container.video(video_link, start_time="2m28s")
            else:
                container.video(video_link)
        # st.video(video_link)  # start_time=start_time

    with st.sidebar:
        if selected_name:
            selected = pills(label="",
                             options=["Extract Transcript",
                                      "Generate Summary", "Clone Voice"],
                             icons=["📑", "📎", "🔊"],
                             index=None,
                             clearable=True,
                             label_visibility="hidden")

            if selected == "Extract Transcript":
                if status_dict.get('transcript', False):
                    st.toast(
                        f"{selected_name}'s transcript already exists.")
                else:
                    with st.spinner('Wait for it...'):
                        if not Path('RI/personas/{selected_name}/transcripts/transcript.txt').is_file():
                            df = st.session_state.presenter_dataframe.copy()
                            try:
                                link = df[df.presenter ==
                                          selected_name].link.values[0]
                                download_transcript(selected_name, link)
                                status_dict = get_persona_status(selected_name)
                            except Exception as e:
                                st.toast(
                                    f"No data found for:{selected_name}\n{e}")

                        if status_dict.get('transcript', False):
                            try:
                                convert_txt_2_pdf(selected_name)
                                st.success(
                                    f"{selected_name}'s transcript extraction complete!")
                                build_vector_store(selected_name)
                                status_dict = get_persona_status(selected_name)
                            except Exception as e:
                                st.error(
                                    f"Transcript conversion and vector store build failed for:{selected_name}")
                        else:
                            st.error(
                                f"Transcript extraction failed for:{selected_name}")

            elif selected == "Generate Summary":
                if status_dict['summary']:
                    st.toast(f"{selected_name}'s summary already exists.")
                else:
                    with st.spinner('Wait for it...'):
                        get_summary_text(selected_name)
                        convert_txt_2_pdf(selected_name, stub='summary')
                        st.success(
                            f"{selected_name}'s summary extraction complete!")
                        status_dict = get_persona_status(selected_name)

            elif selected == "Clone Voice":
                if status_dict.get('cloned', False):
                    st.toast(
                        f"{selected_name}'s voice clone already exists.")
                else:
                    with st.spinner('Wait for it...'):
                        # download audio, get samples, and clone voice
                        link = df[df.presenter == selected_name].link.values[0]
                        audio_file_name = download_audio(selected_name, link)
                        if audio_file_name:
                            st.toast(
                                f"Audio download complete! {audio_file_name}")
                        else:
                            st.error(
                                f"Audio download failed for:{selected_name}({link})")
                        status_dict = get_persona_status(selected_name)
                        if not status_dict.get('segments', False):
                            description = f'{selected_name} has a passionate voice.'
                            extract_samples(
                                selected_name, n_samples=3, sample_length=300)
                            clone_voice(selected_name, description)
                            st.success(
                                f"{selected_name}'s voice clone complete!")
                            status_dict = get_persona_status(selected_name)
                        else:
                            st.error(
                                f"Audio extraction failed for:{selected_name}({link})")
    if selected_name:
        if status_dict.get('transcript', False) or status_dict.get('summary', False):
            with st.expander("View Results"):
                viewables = pills(label="",
                                  options=["View Transcript", "View Summary"],
                                  icons=["📑", "📎"],
                                  index=None,
                                  clearable=True,
                                  label_visibility="hidden")
                if viewables == "View Transcript":
                    if status_dict.get('transcript', False):
                        transcript_filepath = Path(
                            f'RI/personas/{selected_name}/transcripts/transcript.pdf')
                        pdf_viewer(transcript_filepath,
                                   key=f'transcript_{selected_name}')
                        transcript_filepath_pdf = f'RI/personas/{selected_name}/transcripts/transcript.pdf'
                        st.download_button(label="Export Transcript :paperclip:",
                                           data=FileIO(
                                               Path(transcript_filepath_pdf).absolute(), "rb"),
                                           file_name=transcript_filepath_pdf,
                                           mime='application/octet-stream')
                elif viewables == "View Summary":
                    if status_dict.get('summary', False):
                        with open(f'RI/personas/{selected_name}/transcripts/summary.txt', 'r', encoding='cp1252', errors="replace") as f:
                            st.markdown(f.read())
                        summary_filepath_pdf = f'RI/personas/{selected_name}/transcripts/summary.pdf'
                        st.download_button(label="Export Summary :paperclip:",
                                           data=FileIO(
                                               Path(summary_filepath_pdf).absolute(), "rb"),
                                           file_name=summary_filepath_pdf,
                                           mime='application/octet-stream')
                    else:
                        st.error(f"""Summary not available for {selected_name}\n / 
                                                Please *Generate Summary* from sidebar first.""")


if __name__ == "__main__":
    run()
