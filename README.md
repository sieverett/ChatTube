# SelfActualize.AI & TED

![alt text](imgs/sa_small.png) 
![alt text](imgs/and_small.png) 
![alt text](imgs/TED_small.png)


## Description  
This project creates voice and chat AI likenesses of TED's most watched heros, coaches, and presenters.  The implementation is to be extensible to other personas.

*Note:  This project is in early stage development and the code can be run in the jupyter notebook [playground](imgs/playground.ipynb).*  


> Target functionality  
1. User selects a TED persona.
2. User can then text and voice chat with the persona.

> Data stores
1. Base data store: contains links to TED top 100 most watched videos by presenter.
2. Persona data store: contains transcripts, audio files, segmented audio files, and transcripts of TED personas.

## Instructions
- clone repo --> ```git clone https://github.com/sieverett/selfActualize.AI.git```
- install dependencies --> ```"pip install -r requirements.txt"```
- load base data for TED by running --> ```"python3 TED_base_data_collector.py"```
- add environment variables --> `.env-template` and change file name to only `.env`.
- for command line testing run --> ```"python3 TED_persona_clone_tool.py --presenter 'al gore' --text 'let's make the climate great again!"```
- for notebook, run --> `jupyer playground.ipynb`  

## Code  
**Base data store**  
`TED_base_data_from_channel_id()` generates **TED_playlist_info.csv**.  

**Persona data build flow**  
Building data profile for single persona, requires:  
```python
build_persona(presenter,link)
```

*Explanation*  
`build_persona(presenter,link)` takes presenter and executes the following functions:   
- `make_file_structure(presenter,root_dir='TED')` builds the directory structure for the persona.  
- `get_youtube_video_transcripts(presenter, link, transcripts_path)` grabs the YouTube transcripts of the TED presentation.  
- `download_audio(link)` downloads the audio from the presentation.  
- `extract_samples(n_samples = 1, sample_length = 300)` clips the audio for use for voice cloning.  
- `clone_voice(presenter,description,segments_path)` clones the voice from the audio segment.
- `build_chat_bot(presenter)` builds chat bot from persona transcript(s) (tbd). 

Now, to build data profiles for top n personas by view count:     
```python
build_top_n_ted_personas(top_n=3)
```

<br>

To use the cloned voice, example:  
```python
presenter='ian bremmer'
text="who's gonna have a showdown with me at the ok corral?"
create_audio(presenter,text,play_=False)
```

To start chat with a persona (tbd):  
```python
presenter='ian bremmer'
start_chat(presenter,with_voice=False)  
```  

## To do:     
1. Build and deploy [streamlit](https://streamlit.io/) interface for simple testing. Input = presenter,text --> Output = cloned voice representation.    
2. Complete the start_chat functionality. Will use RAG framework.  
3. Down the road...implementation for generic persona will require diarization of audio.  

Contributors  
Silas Everett @https://github.com/sieverett
