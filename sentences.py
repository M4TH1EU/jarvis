import datetime as datetime

import spacy
from nltk.corpus import stopwords

import chatbot.chat
import homeassistant.homeassistant
import homeassistant.lights
import homeassistant.meteo
import homeassistant.spotify
import homeassistant.switch
import plugins.alarms
import plugins.shazam
from plugins import wiki, spotipy

sentences = {}
last_answer = ""
nlp = spacy.load("fr_core_news_sm")


def recogniseSentence(sentence):
    tag = chatbot.chat.get_tag_for_sentence(sentence)

    # hey jarvis
    if tag == 'jarvis':
        return chatbot.chat.get_response_for_tag('yesSir')

    # comment ça va
    elif is_tag(tag, 'greeting'):
        return chatbot.chat.get_response_for_tag('greeting')

    # allume la lumière
    elif is_tag(tag, 'lights_on'):
        homeassistant.lights.turn_on("light.lumieres_chambre")
        return chatbot.chat.get_response_for_tag('lights_on')

    # éteint la lumière
    elif is_tag(tag, 'lights_off'):
        homeassistant.lights.turn_off("light.lumieres_chambre")
        return chatbot.chat.get_response_for_tag('lights_off')

    # allume les leds
    elif is_tag(tag, 'leds_on'):
        homeassistant.lights.turn_on("light.leds_chambre")
        return chatbot.chat.get_response_for_tag('leds_on')

    # éteint les leds
    elif is_tag(tag, 'leds_off'):
        homeassistant.lights.turn_off("light.leds_chambre")
        return chatbot.chat.get_response_for_tag('leds_off')

    # mets le morceau suivant
    elif is_tag(tag, 'next_track'):
        homeassistant.spotify.next_track("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('next_track')

    # mets le morceau précédent
    elif is_tag(tag, 'previous_track'):
        homeassistant.spotify.previous_track("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('previous_track')

    # relance la musique
    elif is_tag(tag, 'resume_music'):
        homeassistant.spotify.play("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('resume_music')

    # mets la musique sur pause
    elif is_tag(tag, 'pause_music'):
        homeassistant.spotify.pause("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('pause_music')

    # monte le son
    elif is_tag(tag, 'turn_up_volume'):
        homeassistant.spotify.turn_up_volume("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('turn_up_volume')

    # baisse le son
    elif is_tag(tag, 'turn_down_volume'):
        homeassistant.spotify.turn_down_volume("media_player.spotify_mathieu_broillet")
        return chatbot.chat.get_response_for_tag('turn_down_volume')

    # il est quelle heure
    elif is_tag(tag, 'what_time_is_it'):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_time = current_time.replace('00:', 'minuit ')
        current_time = current_time.replace('12:', 'midi ')

        return chatbot.chat.get_response_for_tag('what_time_is_it') + " " + current_time

    # non rien finalement
    elif is_tag(tag, 'nothingDetection'):
        # TODO: find a way to replace the beepy sound
        return "Okay"

    # allume l'imprimante 3d
    elif is_tag(tag, 'turn_on_3d_printer'):
        homeassistant.switch.turn_on('switch.bfd9b202b8140c15780fpe')
        return chatbot.chat.get_response_for_tag('turn_on_3d_printer')

    # éteint l'imprimante 3d
    elif is_tag(tag, 'turn_off_3d_printer'):
        homeassistant.switch.turn_off('switch.bfd9b202b8140c15780fpe')
        return chatbot.chat.get_response_for_tag('turn_off_3d_printer')

    # allume le pc
    elif is_tag(tag, 'turn_on_pc'):
        homeassistant.switch.turn_on('switch.wake_on_lan_pc_tour')
        return chatbot.chat.get_response_for_tag('turn_on_pc')

    # éteint le pc
    elif is_tag(tag, 'turn_off_pc'):
        homeassistant.switch.turn_off('switch.wake_on_lan_pc_tour')
        return chatbot.chat.get_response_for_tag('turn_off_pc')

    # mets le pc en veille
    elif is_tag(tag, 'sleep_pc'):
        homeassistant.homeassistant.call_service('', 'shell_command/sleep_tour_mathieu')
        return chatbot.chat.get_response_for_tag('sleep_pc')

    # allume la tablette
    elif is_tag(tag, 'turn_on_wall_tablet'):
        homeassistant.lights.turn_on('light.mi_pad_screen')
        return chatbot.chat.get_response_for_tag('turn_on_wall_tablet')

    # éteint la tablette
    elif is_tag(tag, 'turn_off_wall_tablet'):
        homeassistant.lights.turn_off('light.mi_pad_screen')
        return chatbot.chat.get_response_for_tag('turn_off_wall_tablet')

    # c'est quoi le titre de cette chanson
    elif is_tag(tag, 'song_detection'):

        title = ""
        singer = ""

        if homeassistant.spotify.is_music_playing('media_player.spotify_mathieu_broillet'):
            song_info = homeassistant.spotify.get_infos_playing_song('media_player.spotify_mathieu_broillet')
            title = song_info[0]
            singer = song_info[1]
        else:
            song = plugins.shazam.recognise_song()
            if len(song) > 0:
                title = song[0]
                singer = song[1]
                # track_id = song[2]
            else:
                return chatbot.chat.get_response_for_tag('songNotFound')

        answer_sentence = chatbot.chat.get_response_for_tag('song_detection')
        answer_sentence = answer_sentence.replace("%title", title)
        answer_sentence = answer_sentence.replace("%singer", singer)
        return answer_sentence

    else:

        # cherche XYZ sur wikipédia
        if tag == 'wikipedia_search':
            sentence = sentence[0].lower() + sentence[1:]

            person_name = get_person_in_sentence(sentence)
            if person_name != "none":
                print("Search : ", person_name)
                return wiki.get_description(person_name)
            else:
                filtered_sentence = get_sentence_without_stopwords(sentence)
                sentence_without_patterns_words = get_sentence_without_patterns_words(filtered_sentence, 'wikipedia')

                print("Search : ", sentence_without_patterns_words)
                return wiki.get_description(sentence_without_patterns_words)

        # mets le réveil à 6h45
        elif is_tag(tag, 'alarm'):
            spoke_time = "7h30"
            # TODO: get the day and the hour in the sentence
            spoke_time = spoke_time.replace("demain", "").replace("matin", "").replace(" ", "")

            hours = spoke_time.split("h")[0]
            minutes = spoke_time.split("h")[1]

            spoke_time = datetime.time(hour=int(hours), minute=int(minutes))
            plugins.alarms.add_alarm(spoke_time.strftime("%H:%M"))

        # quel temps fait il
        elif is_tag(tag, 'weather'):
            homeassistant_weather_entity_id = 'weather.bussigny_sur_oron'
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            today_hour = datetime.datetime.now().hour

            sera = "est"
            faire = "fait"

            if today_hour <= 10:
                sera = "sera"
                faire = "fera"

            sentence_meteo = chatbot.chat.get_response_for_tag('weather')
            sentence_meteo = sentence_meteo.replace('&sera', sera)
            sentence_meteo = sentence_meteo.replace('&faire', faire)
            sentence_meteo = sentence_meteo.replace('%condition',
                                                    homeassistant.meteo.get_condition(homeassistant_weather_entity_id))
            sentence_meteo = sentence_meteo.replace('%temperature',
                                                    homeassistant.meteo.get_temperature(
                                                        homeassistant_weather_entity_id))
            sentence_meteo = sentence_meteo.replace('%lowtemp', homeassistant.meteo.get_temperature_low(
                homeassistant_weather_entity_id))
            sentence_meteo = sentence_meteo.replace('%wind_speed',
                                                    homeassistant.meteo.get_wind_speed(homeassistant_weather_entity_id))

            # TODO : add different types of wind speed
            sentence_meteo = sentence_meteo.replace('%wind_words', "faible")

            return sentence_meteo

        # joue i'm still standing de elton john
        elif is_tag(tag, 'play_song'):
            singer = get_person_in_sentence(sentence)
            print(singer)

            song_name = get_sentence_without_patterns_words(sentence, 'play_song').replace(singer, '')
            print(song_name)

            if singer != 'none' and song_name:
                return spotipy.play_song(singer, song_name)
            elif singer != 'none' and not song_name:
                return spotipy.play_artist(singer)
            elif singer == 'none' and song_name:
                return spotipy.play_song_without_artist(song_name)
        else:
            return chatbot.chat.get_response_for_tag_custom('dont_understand')


def is_tag(tag, name):
    return tag == name


def get_sentence_without_stopwords(sentence):
    stop_words_french = set(stopwords.words('french'))
    filtered_sentence = [w for w in sentence.lower().split() if w not in stop_words_french]
    filtered_sentence = " ".join(filtered_sentence)
    return filtered_sentence


def get_sentence_without_patterns_words(sentence, tag):
    patterns = chatbot.chat.get_all_patterns_for_tag(tag)
    patterns_stop_words = " ".join(patterns).lower().split()

    sentence_without_patterns_words = ' '.join(
        filter(lambda x: x.lower() not in patterns_stop_words, sentence.split()))

    return sentence_without_patterns_words


def get_person_in_sentence(sentence):
    doc = nlp(sentence)

    for word in doc:
        # print(word.text, word.pos_) # prints every words from the sentence with their types

        de_words = ['de ', 'd\'', 'des']

        # support for lowercase name with spotify (play_song)
        for de_word in de_words:
            if word.text == de_word.replace(' ', '') and (str(word.pos_) == 'ADP' or str(word.pos_) == 'DET'):
                person = sentence.split(" ".join([de_word]))[1]
                return person

    for ent in doc.ents:
        if ent.label_ == 'PER':
            return ent.text

    return "none"
