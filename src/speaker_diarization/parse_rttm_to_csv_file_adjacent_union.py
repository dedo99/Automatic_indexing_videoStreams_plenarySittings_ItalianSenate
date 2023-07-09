import csv
from pathlib import Path
import os
import sys


pathname = os.path.dirname(sys.argv[0])

print(pathname)

file_path = pathname + "/../../data/file_rttm/" + "Leg15NumSed33.rttm"

# si ottiene solamente il nome del file senza estensione e percorso
filename = str(file_path).split("/")[-1][:-5]
print(filename)
file_path = Path(file_path)
# si controlla se il file è nella directory esaminata
if file_path.is_file():
    print(file_path)
    # si inizializza il file csv che conterrà le informazioni
    f_info_video = open(pathname + '/../../data/convert_rttm_to_csv/' + filename + '.csv', 'w')
    writer_info_video = csv.writer(f_info_video, lineterminator='\n')
    writer_info_video.writerow(["id_speaker", "offset_video", "duration"])
    # si apre il file rttm in lettura
    with open(file_path, 'r') as file:
        # si itera su ciascuna linea del file
        previous_id_speaker = None
        previous_offset_video = None
        previous_duration = None
        for line in file:
            print(line)
            # si splittano i campi sullo spazio e si prendono quelli di interesse
            # id_speaker, offset_video, duration
            line_splitted = line.split(" ")
            offset_video = float(line_splitted[3])
            duration = float(line_splitted[4])
            id_speaker = line_splitted[7]
            # # si uniscono record adiacenti dello stesso utente solo le tra la fine dell'intervento precedente 
            # # e l'inizio del successivo c'è un gap più piccolo di THRESHOLD_INTERVALTIME_SAMESPAKER
            # if id_speaker == previous_id_speaker and previous_offset_video + previous_duration + THRESHOLD_INTERVALTIME_SAMESPAKER > offset_video:
            if id_speaker == previous_id_speaker:
                previous_duration = offset_video + duration - previous_offset_video
            elif previous_id_speaker == None:
                previous_id_speaker = id_speaker
                previous_offset_video = offset_video
                previous_duration = duration
            else:
                writer_info_video.writerow([previous_id_speaker, float(previous_offset_video), float(previous_duration)])
                previous_id_speaker = id_speaker
                previous_offset_video = offset_video
                previous_duration = duration
        writer_info_video.writerow([previous_id_speaker, float(previous_offset_video), float(previous_duration)])
    f_info_video.close()
print("Terminato: " + filename)
