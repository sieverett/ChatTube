import sys 
import os
sys.path.append(os.path.abspath(f'/mnt/c/Users/silas/Projects/selfActualize/scripts'))
from youtube2text import Youtube2Text

persona = "dalaiLama"
url="https://www.youtube.com/watch?v=IUEkDc_LfKQ"
persona_source=f'/mnt/c/Users/silas/Projects/selfActualize/personas/{persona}'

converter = Youtube2Text(persona_source)

converter.url2text(url)