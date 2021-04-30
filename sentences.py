import csv
# from main import speak
import datetime as datetime
import random

import pyttsx3

import homeassistant.lights
import homeassistant.spotify

sentences = {}


def registerSentences():
    # our csv file and a csv reader (encoded in utf8 for special character compatibility)
    csv_file = open('Sentences.csv', encoding="utf-8")
    csv_reader = csv.reader(csv_file, delimiter='|')

    # column number and id(s)
    column = 0
    sentencesId = csv_file.readline().split("|")

    # for every line in our .csv file
    for lines in csv_reader:

        # for every hotwords in our .csv file (based on first line)
        for sentenceId in sentencesId:

            # if there some empty "fake" column then don't try to register them
            if 'Column' in sentenceId:
                break
            else:
                # fix issue with unicode caracter
                sentenceId = sentenceId.replace('\ufeff', '').replace('\n', '')

                # creating an entry to be able to use .append afterward
                if sentenceId not in sentences:
                    sentences[sentenceId] = []

                # if the entry is not empty then add it to the sentences dict
                if lines[column] != "":
                    sentences[sentenceId].append(lines[column].lower())

            # increment column
            column = column + 1

        # reset column
        column = 0


def answer(sentence_id):
    if getSentencesById(sentence_id):
        speak(random.choice(getSentencesById(sentence_id)))
        print(random.choice(getSentencesById(sentence_id)))
    else:
        speak(random.choice(getSentencesById("dontUnderstand")))


def getSentences():
    return sentences


def getSentencesById(sentence_id):
    return sentences[sentence_id]


def getRandomSentenceFromId(sentence_id):
    return random.choice(getSentencesById(sentence_id))


def recogniseSentence(sentence):
    print(sentence)

    # hey john
    if sentence in getSentencesById('hotwordDetection'):
        answer('yesSir')

    # comment ça va
    elif sentence in getSentencesById('howAreYouDetection'):
        answer('allGoodSir')

    # allume la lumière
    elif sentence in getSentencesById('turnOnLightsDetection'):
        answer('turningOnLights')
        homeassistant.lights.turnOn("light.lumieres_chambre")

    # éteint la lumière
    elif sentence in getSentencesById('turnOffLightsDetection'):
        answer('turningOffLights')
        homeassistant.lights.turnOff("light.lumieres_chambre")

    # allume les leds
    elif sentence in getSentencesById('turnOnLedsDetection'):
        answer('turningOnLights')
        homeassistant.lights.turnOn("light.leds_chambre")

    # éteint les leds
    elif sentence in getSentencesById('turnOffLedsDetection'):
        answer('turningOffLights')
        homeassistant.lights.turnOff("light.leds_chambre")

    # mets le morceau suivant
    elif sentence in getSentencesById('nextTrackDetection'):
        answer('nextTrack')
        homeassistant.spotify.nextTrack("media_player.spotify_mathieu_broillet")

    # mets le morceau précédent
    elif sentence in getSentencesById('previousTrackDetection'):
        answer('previousTrack')
        homeassistant.spotify.previousTrack("media_player.spotify_mathieu_broillet")

    # relance la musique
    elif sentence in getSentencesById('resumeMusicDetection'):
        answer('resumeMusic')
        homeassistant.spotify.play("media_player.spotify_mathieu_broillet")

    # mets la musique sur pause
    elif sentence in getSentencesById('pauseMusicDetection'):
        answer('pauseMusic')
        homeassistant.spotify.pause("media_player.spotify_mathieu_broillet")

    # monte le son
    elif sentence in getSentencesById('turnUpVolumeDetection'):
        answer('turningUpVolume')
        homeassistant.spotify.turnUpVolume("media_player.spotify_mathieu_broillet")

    # baisse le son
    elif sentence in getSentencesById('turnDownVolumeDetection'):
        answer('turningDownVolume')
        homeassistant.spotify.turnDownVolume("media_player.spotify_mathieu_broillet")

    elif sentence in getSentencesById('whatTimeIsIt'):
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(getRandomSentenceFromId('itIsTime') + " " + current_time)
    else:
        answer('dontUnderstand')


def speak(text):
    rate = 100  # Sets the default rate of speech
    engine = pyttsx3.init()  # Initialises the speech engine
    voices = engine.getProperty('voices')  # sets the properties for speech
    engine.setProperty('voice', voices[0])  # Gender and type of voice
    engine.setProperty('rate', rate + 50)  # Adjusts the rate of speech
    engine.say(text)  # tells Python to speak variable 'text'
    engine.runAndWait()  # waits for speech to finish and then continues with program
