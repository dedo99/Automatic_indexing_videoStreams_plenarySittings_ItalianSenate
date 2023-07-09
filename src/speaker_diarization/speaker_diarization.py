import torch
from pyannote.audio import Pipeline
from pathlib import Path
import os
import ffmpeg


directory = Path('./../../data/setting_video/')  # Specifica il percorso della cartella

# Verifica la disponibilità della GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


for file_path in directory.glob('**/*'):
    if file_path.is_file():

        print(file_path)

        filename = str(file_path).split("/")[-1][:-4]
        print(filename)

        aac_file = "./../../data/setting_video/" + filename + ".acc"
        wav_file = "./../../data/track_audio_wav/" + filename + ".wav"

        print("Inizio conversione wav")
        stream = ffmpeg.input(aac_file)
        stream = ffmpeg.output(stream, wav_file)
        ffmpeg.run(stream)
        print("Conversione wav completata")
        os.remove(aac_file)

        pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token="YOUR TOKEN")
        pipeline=pipeline.to(0)

        diarization = pipeline(wav_file)

        with open("./../../data/file_rttm/" + filename + ".rttm", "w") as rttm:
            diarization.write_rttm(rttm)

        os.remove(wav_file)