from sentence_transformers import SentenceTransformer, util
import re
import csv
import os
import sys

#############################################################################
############################### COSTANTI ####################################
#############################################################################

THRESHOLD_SINGLE_SENTENCES = 0.80
DISPLACEMENT_THRESHOLD = 0.3

#############################################################################
######################## DEFINIZIONE METODI AUSILIARI########################
#############################################################################

# generano una lista di coppie con indice dell'intervento e una singola frase dell'insieme di frasi presenti all'interno
# di ogni singolo intervento
def cleaning_and_split_sentence_audio_list(sentence_list):
    new_sentence_list = []
    #  (?<!\d\.) rappresenta un negative lookbehind e controlla che il punto non sia preceduto da un numero e un punto,
    #  mentre (?! \d) rappresenta un negative lookahead e controlla che il punto non sia seguito da uno spazio e poi un numero.
    pattern = r"(?<!n\.\s)(?<!\d\.\s)\.(?! \d)"
    for i in range(len(sentence_list)):
        clean_sentence = sentence_list[i][1].replace("\n", " ").lstrip().rstrip()
        splitted_sentence = re.split(pattern, clean_sentence)
        for sentence in splitted_sentence:
            pattern_more_whitespace = r"\s{2,}"  # Rappresenta due o più spazi bianchi adiacenti
            nuova_frase = re.sub(pattern_more_whitespace, " ", sentence)
            new_sentence_list.append([i, nuova_frase])
    return new_sentence_list

# generano una lista di coppie con indice dell'intervento e una singola frase dell'insieme di frasi presenti all'interno
# di ogni singolo intervento
def cleaning_and_split_sentence_text_list(sentence_list):
    new_sentence_list = []
    #  (?<!\d\.) rappresenta un negative lookbehind e controlla che il punto non sia preceduto da un numero e un punto,
    #  mentre (?! \d) rappresenta un negative lookahead e controlla che il punto non sia seguito da uno spazio e poi un numero.
    pattern = r"(?<!n\.\s)(?<!\d\.\s)\.(?! \d)"
    for i in range(len(sentence_list)):
        clean_sentence = sentence_list[i][3].replace("\n", " ").lstrip().rstrip()
        splitted_sentence = re.split(pattern, clean_sentence)
        for sentence in splitted_sentence:
            pattern_more_whitespace = r"\s{2,}"  # Rappresenta due o più spazi bianchi adiacenti
            nuova_frase = re.sub(pattern_more_whitespace, " ", sentence)
            new_sentence_list.append([i, nuova_frase])
    return new_sentence_list

def cleaning_single_sentence(sentence):
    new_sentence = sentence.replace("\n", " ").lstrip().rstrip()
    return new_sentence

def generate_double_sentence_list(sentence_list):
    double_sentences_list = []
    for i in range(len(sentence_list)-1):
        double_sentences = sentence_list[i] + " " + sentence_list[i+1]
        double_sentences_list.append(double_sentences)
    return double_sentences_list


def get_data():
    name_speech2text_dir_list = []
    entries = os.listdir('./../../data/speech2text')
    for entry in entries:
        if entry.endswith('.csv'):
            name_speech2text_dir_list.append(entry[:-4])
    return name_speech2text_dir_list


#############################################################################
################################### MAIN ####################################
#############################################################################

pathname = os.path.dirname(sys.argv[0])

print(pathname)   

# name_speech2text_dir_list = get_data()
name_speech2text_dir_list = ["Leg15NumSed14"]


for name in name_speech2text_dir_list:

    audio_list = []
    text_list = []

    # conteggio righe seduta audio
    num_row_audio = 0

    # conteggio righe seduta resoconto
    num_row_text = 0

    with open(pathname + "/../../data/speech2text/" + name + ".csv", 'r', encoding='utf-8') as file:
        # Crea un oggetto reader per leggere il file CSV
        reader = csv.reader(file)

        # Utilizza next() per scartare la prima riga
        next(reader)

        # Itera su ogni riga nel file CSV
        for row in reader:
            print(row)
            # Aggiungi il valore dell'attributo alla lista
            # id_speaker,text,offset_video,duration
            id_speaker = row[0]
            text = row[1]
            offset_video = row[2]
            duration = row[3]
            num_row_audio +=1
            audio_list.append([id_speaker, text, offset_video, duration])


    with open(pathname + "/../../data/setting_report/" + name + ".csv", 'r', encoding='utf-8') as file:
        # Crea un oggetto reader per leggere il file CSV
        reader = csv.reader(file)

        # Utilizza next() per scartare la prima riga
        next(reader)

        # Itera su ogni riga nel file CSV
        for row in reader:
            print(row)
            # Aggiungi il valore dell'attributo alla lista
            # id_speaker,text,offset_video,duration
            name_speaker = row[0]
            datetime = row[1]
            topic = row[2]
            text = row[3]
            num_row_text += 1
            text_list.append([name_speaker, datetime, topic, text])

    print(len(audio_list))
    print(len(text_list))

    #rimozione spazi bianchi e ritorni a capo
    sentence_audio_list = cleaning_and_split_sentence_audio_list(audio_list)
    sentence_text_list = cleaning_and_split_sentence_text_list(text_list)

    print(len(sentence_audio_list))
    print(len(sentence_text_list))
        
    # istanza del modello SBERT
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # embeddings delle frasi
    only_sentence_audio_list = [lista[1] for lista in sentence_audio_list]
    only_sentence_text_list = [lista[1] for lista in sentence_text_list]
    sentence_embeddings_audio = model.encode(only_sentence_audio_list)
    sentence_embeddings_text = model.encode(only_sentence_text_list)


    print("----------------------------------------------------------------------------------------------------")
    print("----------------------------------------------CONFRONTI---------------------------------------------")
    print("----------------------------------------------------------------------------------------------------")

    list_match_sentences = []

    num_sentences_audio = 0

    for i in range(len(sentence_embeddings_audio)):
        sentence_best_match = None
        sentence_best_score = None
        if sentence_audio_list[i][1] == "" or sentence_audio_list[i][1] == " ":
            continue
        num_sentences_audio += 1
        num_sentences_report = 0
        for j in range(len(sentence_embeddings_text)):
            if sentence_text_list[j][1] == "" or sentence_text_list[j][1] == " ":
                continue
            num_sentences_report += 1
            # print(str(i) + ": " + sentence_audio_list[i])
            # print(str(j) + ": " + sentence_text_list[j])
            cos_sim = util.cos_sim(sentence_embeddings_audio[i], sentence_embeddings_text[j])
            if sentence_text_list[j][0]/num_row_text < sentence_audio_list[i][0]/num_row_audio + DISPLACEMENT_THRESHOLD and sentence_text_list[j][0]/num_row_text > sentence_audio_list[i][0]/num_row_audio - DISPLACEMENT_THRESHOLD:
                if sentence_best_score == None or sentence_best_score < cos_sim:
                    sentence_best_match = sentence_text_list[j][1]
                    index_best_match = sentence_text_list[j][0]
                    sentence_best_score = cos_sim
            # print("Cosine-Similarity: " + str(float(cos_sim[0][0])))
            # print('\n')
        # scrittura su file del miglior risultato ottenuto con la frase estratta dall'audio
        if float(sentence_best_score[0][0]) > THRESHOLD_SINGLE_SENTENCES:
            list_match_sentences.append((sentence_audio_list[i][0], sentence_audio_list[i][1], index_best_match, sentence_best_match, float(sentence_best_score[0][0])))

    print("Number sentences audio:" + str(num_sentences_audio))
    print("Number sentences report:" + str(num_sentences_report))

    print(list_match_sentences)
    print(len(list_match_sentences))

    print("----------------------------------------------------------------------------------------------------")
    print("--------------------------------MATCH TRA ID SPEAKER E NOME SPEAKER---------------------------------")
    print("----------------------------------------------------------------------------------------------------")

    idSpeaker2nameSpeaker = {}

    for ind_audio, sent_audio, ind_text, sent_text, score in list_match_sentences:
        idSpeaker = audio_list[ind_audio][0]
        if idSpeaker not in idSpeaker2nameSpeaker:
            nameSpeaker_score = (text_list[ind_text][0], score)
            idSpeaker2nameSpeaker[idSpeaker] = nameSpeaker_score
        else:
            nameSpeaker, current_score = idSpeaker2nameSpeaker.get(idSpeaker)
            if score > current_score:
                nameSpeaker_score = (text_list[ind_text][0], score)
                idSpeaker2nameSpeaker[idSpeaker] = nameSpeaker_score


    print(idSpeaker2nameSpeaker)


    print("----------------------------------------------------------------------------------------------------")
    print("--------------------------------MATCH PER IL TOPIC DI OGNI INTERVENTO-------------------------------")
    print("----------------------------------------------------------------------------------------------------")

    vtoc_list = []
    current_topic = None
    # la data è in tutti i record di text_list quindi basta prendere il primo record
    current_datetime = text_list[0][1]

    # si itera su tutti i record ottenuti ottenuti dallo speech2text
    for i in range(len(audio_list)):
        temp_score = 0
        name_speaker = None
        # si verifica pre ogni record dello speech2text se ha match semantico con una o più frase del resoconto
        for tup in list_match_sentences:
            if i == tup[0] and tup[4]>temp_score:
                # aggiorno lo score migliore trovato per un specifico indice dell'audio
                temp_score = tup[4]
                # si acquisisce l'indice del record estratto dal resoconto
                index_text_list = tup[2]
                # acquisisce il topic corrente se ha fatto match semantico con sbert
                current_topic = text_list[index_text_list][2]
                if audio_list[i][0] not in idSpeaker2nameSpeaker:
                    name_speaker = audio_list[i][0]
                else:    
                    name_speaker = idSpeaker2nameSpeaker[audio_list[i][0]][0]
                offset_video = audio_list[i][2]
                duration = audio_list[i][3]
                text = audio_list[i][1]
        if name_speaker != None:
            vtoc_list.append((name_speaker, current_datetime, offset_video, duration, current_topic, text))


    print("----------------------------------------------------------------------------------------------------")
    print("-------------------------------SALVATAGGIO SU FILE DEI MATCH MIGLIORI-------------------------------")
    print("----------------------------------------------------------------------------------------------------")

    print("Iniziato!")

    # creazione file per salvataggio match
    f_similarity = open(pathname + "/../../data/semantic_textual_similarity/" + name + ".csv", 'w', encoding='utf-8')
    writer_similarity = csv.writer(f_similarity, delimiter="~", lineterminator='\n')
    # writer_similarity.writerow(["idSpeaker", "audio_offset", "duration", "nameSpeaker", "topic", "text_resoconto"])
    writer_similarity.writerow(["nameSpeaker", "datetime", "offsetVideo", "duration", "topic", "text"])

    # # scrittura dei match su file csv
    # for (ind_audio, sent_audio, ind_text, sent_text, score) in list_match_sentences:
    #     writer_similarity.writerow([ind_audio, sent_audio, ind_text, sent_text, score])


    for (name_speaker, current_datetime, offset_video, duration, current_topic, text) in vtoc_list:
        writer_similarity.writerow([name_speaker, current_datetime, offset_video, duration, current_topic, text])
  

    # chiusura file
    f_similarity.close()

    print("Completato:" + name)