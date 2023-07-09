import xml.etree.ElementTree as ET
import datetime
import os
import sys
import csv

# ---------------------------------------------
# ------------ Funzioni ausiliarie ------------
# ---------------------------------------------


def get_data():
    name_speech2text_dir_list = []
    entries = os.listdir('./../../data/semantic_textual_similarity')
    for entry in entries:
        if entry.endswith('.csv'):
            name_speech2text_dir_list.append(entry[:-4])
    return name_speech2text_dir_list


def format_seconds(seconds):
    seconds = float(seconds)
    time = datetime.timedelta(seconds=int(seconds))
    hours = time.seconds // 3600
    minutes = (time.seconds // 60) % 60
    seconds = time.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ---------------------------------------------
# ------------------- MAIN --------------------
# ---------------------------------------------

# Acquisizione del percorso fino alla cartella del progetto
pathname = os.path.dirname(sys.argv[0])

print(pathname)   

# name_speech2text_dir_list = get_data()
name_speech2text_dir_list = ["Leg15NumSed33"]

# Itera su tutti i file che sono presenti nel semantic_textual_diarization
for filename in name_speech2text_dir_list:

    num_legislatura = int(filename[3:filename.index("NumSed")])
    num_seduta = int(filename[filename.index("NumSed")+6:])

    with open(pathname + "/../../data/semantic_textual_similarity/" + filename + ".csv", 'r', encoding='utf-8') as file:
        # Crea un oggetto reader per leggere il file CSV
        reader = csv.reader(file, delimiter="~")

        # Salta l'header
        next(reader)

        # Acquisisci il campo desiderato dalla prima riga
        first_row = next(reader)
        current_datetime = first_row[1]

        # Riposiziona il puntatore di lettura al primo record
        file.seek(0)

        # Creazione dell'elemento radice <BGTDOC>
        root = ET.Element("BGTDOC")

        # Creazione dell'elemento <WEBTV> e aggiunta dell'attributo "versione"
        webtv = ET.SubElement(root, "WEBTV", versione="1.1")

        # Creazione dell'elemento <Proprieta>
        proprieta = ET.SubElement(webtv, "Proprieta")

        # Creazione dell'elemento <Protocollo> all'interno di <Proprieta> con gli attributi "idTesto" e "legislatura"
        protocollo = ET.SubElement(proprieta, "Protocollo", idTesto="", legislatura=str(num_legislatura))

        # Creazione dell'elemento <Seduta> all'interno di <Proprieta> con gli attributi "data" e "numero"
        seduta = ET.SubElement(proprieta, "Seduta", data=current_datetime, numero=str(num_seduta))

        # Creazione dell'elemento <InizioSeduta>
        proprieta = ET.SubElement(webtv, "InizioSeduta", id="", videoOffset="00:00:00")

        # Utilizza next() per scartare la prima riga
        next(reader)

        # Imposta inizialmente il topic ad un valore non definito
        current_topic = None
        current_discussion = None

        # Itera su ogni riga nel file CSV
        for row in reader:
            print(row)
            # Acquisizione dei valori necessari
            name_speaker = row[0]
            offset_video = format_seconds(row[2])
            duration = row[3]
            topic = row[4]
            if topic == "":
                intervention = ET.SubElement(webtv, "Intervento", gruppo="", idPolitico="", inIndice=name_speaker, organo="Senato", progrPers="", qualifica="", videoOffset=offset_video)
            elif current_topic == None or topic != current_topic:
                current_topic = topic
                # Creazione dell'elemento <Discussione>
                current_discussion = ET.SubElement(webtv, "Discussione", id="", inIndice=current_topic, videoOffset=offset_video)
                
                # Creazione dell'elemento <Proprieta>
                property = ET.SubElement(current_discussion, "Proprieta")

                # Creazione dell'elemento <Titolo>
                title = ET.SubElement(property, "Titolo")
                title.text = current_topic

                # Creazione dell'elemento <Intervento>
                intervention = ET.SubElement(current_discussion, "Intervento", gruppo="", idPolitico="", inIndice=name_speaker, organo="Senato", progrPers="", qualifica="", videoOffset=offset_video)
            else:
                # Creazione dell'elemento <Intervento>
                intervention = ET.SubElement(current_discussion, "Intervento", gruppo="", idPolitico="", inIndice=name_speaker, organo="Senato", progrPers="", qualifica="", videoOffset=offset_video)
            
        # Creazione dell'albero XML
        tree = ET.ElementTree(root)

        # Salvataggio del documento XML su file
        tree.write(pathname + "/../../data/vtoc_generator/" + str(filename) + ".xml", encoding="utf-8", xml_declaration=False)
