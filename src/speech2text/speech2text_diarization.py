import speech_recognition as sr
from deepmultilingualpunctuation import PunctuationModel
import csv
import os
import sys


pathname = os.path.dirname(sys.argv[0])

# if os.path.exists("./../../../../../data/senato_project/data/speech2text/" + filename + ".txt"):
#     continue
filename = "Leg15NumSed18"

wav_file = pathname + "/../../data/track_audio_wav/" + filename + ".wav"

# initialize the recognizer
r = sr.Recognizer()

# mettere la punteggiatura al testo estratto
model = PunctuationModel()

chunk_size = 120 # 2 minutes in seconds

audio_file = sr.AudioFile(wav_file)


f_text_speakers = open(pathname + '/../../data/speech2text/' + filename + '.csv', 'w')
writer_text_speakers = csv.writer(f_text_speakers, lineterminator='\n')
writer_text_speakers.writerow(["id_speaker", "text", "offset_video", "duration"])

print("Inizio: " + filename)
with audio_file as source:
    print(source.DURATION)
    duration_audio = source.DURATION
    with open(pathname + '../../data/convert_rttm_to_csv/' + filename + '.csv', 'r') as file:
        reader = csv.reader(file)
        num_total_speech_speaker = sum(1 for _ in reader) - 1
        print(num_total_speech_speaker)
        file.seek(0)
        next(reader)  # Salta la prima riga (nomi delle colonne)
        count_speech_speaker = 1
        for row in reader:
            whole_text_speaker = ""
            id_speaker = row[0]
            start_speaker_offset = float(row[1]) - 2
            duration_speech_speaker = float(row[2])
            if start_speaker_offset < 0:
                start_speaker_offset = 0
            print(id_speaker + " " + str(start_speaker_offset) + " " + str(duration_speech_speaker))
            end_speaker_offset = start_speaker_offset + duration_speech_speaker
            if duration_audio > end_speaker_offset + 1:
                end_speaker_offset = end_speaker_offset + 1
            else:
                end_speaker_offset = duration_audio
            for i in range(int(start_speaker_offset), int(end_speaker_offset), chunk_size):
                start = i
                end = min(i + chunk_size, end_speaker_offset)
                source = sr.AudioFile(wav_file)
                with source as s:
                    r.adjust_for_ambient_noise(s)
                    try:
                        audio_data = r.record(s, duration=end-start, offset=start)
                        text = r.recognize_google(audio_data, language='it-IT')
                        whole_text_speaker += " " + text
                        print(whole_text_speaker)
                    except Exception as e:
                        print("-- Error")
                        print(e)
            print("-- Speech_speaker_" + str(count_speech_speaker) +"/ Speech_speaker_" + str(num_total_speech_speaker) + " completato")
            count_speech_speaker += 1
            try:
                result_text_punctuation = model.restore_punctuation(whole_text_speaker)
                writer_text_speakers.writerow([id_speaker, result_text_punctuation, start_speaker_offset, duration_speech_speaker])
            except Exception as e:
                pass



# scrivere il risultato dell'inserimento della punteggiatura su file
# os.remove(wav_file)
f_text_speakers.close()
print("Terminato: " + filename)

print("Execution complete!")
