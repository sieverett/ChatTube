from mutagen.flac import FLAC 
import os
from pathlib import Path

persona = "dalaiLama"
source_path = f'/mnt/c/Users/silas/Projects/selfActualize/personas/{persona}'
os.chdir(source_path)



source_paths = sorted(Path(source_path+'/audio-chunks/').iterdir(), key=os.path.getmtime)
print(source_paths)
output_path=f"{persona}/audio_samples"
os.makedirs(output_path, exist_ok=True)

audioJoin=b''
total_length=0

for chunk in source_paths:
    if '.flac' in chunk.name and total_length < 45:
        print(chunk)
        audio = FLAC(chunk) 

        # contains all the metadata about the wavpack file 
        length = int(audio.info.length) 
        print(length)
        # audio = open(chunk, "rb").read()
        # audioJoin += audio 
        # total_length += length

# sample_num=len(os.listdir(output_path))+1
# audioFinal = open(f"{output_path}/sample_{sample_num}.flac", "wb").write(audioJoin)