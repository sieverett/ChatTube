import streamlit as st
from streamlit_file_browser import st_file_browser
import os
import base64
from utils_file_mgr import get_text_from_docx, page_look
from dotenv import load_dotenv
load_dotenv('etc/.env')
# os.getenv('OPENAI_API_KEY')


def check_file(tag='B'):
    event = st_file_browser(path="Uploads",
                            artifacts_site="http://localhost:1024",
                            show_upload_file=True,
                            show_delete_file=True,
                            show_download_file=False,
                            extentions=['.docx'],
                            show_preview=False,
                            show_choose_file=True,
                            key=tag)
    return event


def delete_set(file_to_delete):
    file_to_del = file_to_delete
    stub = file_to_delete.replace('.docx', '').replace('Uploads/', '')
    output_files = [i for i in os.listdir('Outputs/') if stub in i]
    try:
        os.remove(file_to_del)
    except:
        pass
    for file in output_files:
        try:
            os.remove('Outputs/'+file)
        except:
            pass


def generate_download_button(filename, tag):
    with open('Outputs/'+filename, 'rb') as data:
        st.download_button(f'Download {tag}',
                           data, file_name='Outputs/'+filename)
        st.session_state['download'] = 'True'


st.set_page_config(page_title='Documents Manager',
                   page_icon="💦",
                   initial_sidebar_state="expanded",
                   menu_items={
                       'About': "# This is a beta app. Report errors to your network administrator, Subject: bug report"
                   }
                   )

page_look()

uploaded_file = st.file_uploader(
    "***Upload proposal template doc to start***", accept_multiple_files=False)
event = []

if uploaded_file != None:
    bytes_data = uploaded_file.getvalue()
    filepath = 'Uploads/'+uploaded_file.name
    with open(filepath, 'wb') as f:
        f.write(bytes_data)
    with st.spinner(text="In progress..."):
        get_text_from_docx(filepath)
        st.success(f'File: {uploaded_file.name} Ingested!')
    event = check_file('B')
    uploaded_file = None
else:
    event = check_file('B')

if event:

    if event["type"] == 'CHOOSE_FILE':
        st.write(f"Deleted {event['target'][0]['path']}")

    if event["type"] == 'DELETE_FILE':
        filepath = "Uploads/"+event['target'][0]['path']
        delete_set(filepath)

with st.form("my-form", clear_on_submit=True):
    target_files = [i for i in os.listdir('Outputs') if '.gitkeep' not in i]
    rec_target = st.radio(
        "Documents available for download:",
        target_files)

    submitted = st.form_submit_button("Select")

if submitted:
    if rec_target:
        st.write(f'Document selected **{rec_target}**')
        generate_download_button(filename=rec_target, tag='Document')
