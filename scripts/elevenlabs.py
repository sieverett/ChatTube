from elevenlabs import generate, stream
from elevenlabs import set_api_key
from elevenlabs import clone


source_files="/mnt/c/Users/silas/Projects/selfActualize/personas/dalaiLama/"


# First, authenticate with your API key
set_api_key("8737f8758cbddeb6250cb27a29244f1d")


voice = clone(
   name = "Dalai Lama",
   files = [f"{source_files}/sample1.mp3", f"{source_files}/sample2.mp3"] 
)

def text_stream():
    yield "Hi there, I'm Warren Buffet "
    yield "I'm a business magnate and investor "

# Generate the audio stream
audio_stream = generate(
    text=text_stream(),
    voice=voice,
    model="eleven_monolingual_v1",
    stream=True
)



# Save the stream to a file
with open('warren_buffet.mp3', 'wb') as f:
    f.write(audio_stream.read())