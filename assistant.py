import pyttsx3
import speech_recognition as sr
import webbrowser 
import datetime 
from requests import post, put, get
import base64
import os
import json
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
SCOPEs = ['app-remote-control', 'user-read-playback-state', 'user-modify-playback-state']

voiceMode = 1 # 0 is male and 1 is female

def get_token():
    auth_string = str(client_id) + ":" + str(client_secret)
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer "+ token}

def pauseSong():
    speak("Pausing music")
    global sp
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            sp.pause_playback(device['id'])

def resumeSong():
    speak("Resuming music")
    global sp
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            sp.start_playback(device['id'])

def currentlyPlaying():
    global sp
    title = sp.currently_playing()["item"]["name"]
    artist = sp.currently_playing()["item"]["artists"][0]["name"]
    speak(title + " by " + artist)

def skipSong():
    speak("Skipping song")
    global sp
    sp.next_track()

def previousSong():
    speak("Going to previous song")
    global sp
    sp.previous_track()
def searchForArtist(token, artistName):
    speak("Searching music artist " + artistName)
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artistName}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    print(str(json_result[0]))
    return json_result[0]

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 0.8
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print("the command is printed=", query)
        except Exception as e:
            print(e)
            print("Say that again please")
            return "None"
    return query

def speak(audio):
    engine = pyttsx3.init()
    # getter method(gets the current value
    # of engine property)
    voices = engine.getProperty('voices')
    # setter method .[0]=male voice and
    # [1]=female voice in set Property.
    engine.setProperty('voice', voices[voiceMode].id)
    # Method for the speaking of the assistant
    engine.say(audio) 
    # Blocks while processing all the currently
    # queued commands
    engine.runAndWait()
    
def tellDay():
    # This function is for telling the
    # day of the week
    day = datetime.datetime.today().weekday() + 1
    #this line tells us about the number
    # that will help us in telling the day
    Day_dict = {1: 'Monday', 2: 'Tuesday',
                3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday',
                7: 'Sunday'}
    if day in Day_dict.keys():
        day_of_the_week = Day_dict[day]
        print(day_of_the_week)
        speak("The day is " + day_of_the_week)
 
def tellTime():
    # This method will give the time
    time = str(datetime.datetime.now())
    # the time will be displayed like
    # this "2020-06-05 17:50:14.582630"
    #nd then after slicing we can get time
    print(time)
    hour = time[11:13]
    min = time[14:16]
    speak("The time is " + hour + " hours and " + min + " minutes")  

def searchGoogle(search):
    url = "https://google.com.tr/search?q={}".format(search)
    webbrowser.open_new_tab(url)
    speak("Google searching " + search)

def goToWebsite(url):
    webbrowser.open_new_tab(url)
    speak("Opening " + url)
        
def run_virtual_assistant():
    auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=SCOPEs)
    global sp
    sp = spotipy.Spotify(auth_manager=auth_manager)
    token = get_token()
    print("Virtual assistant is now running!\n")
    print("How can I help you today?")
    while(True):
        query = takeCommand().lower()
        if "hey luna" in query:
            query = query.replace("hey luna", "")
            if "what day is it" in query:
                tellDay()
                continue
            elif "what time is it" in query:
                tellTime()
                continue
            elif "who are you" in query:
                speak("I am your virtual assistant, Luna")
                continue
            elif "google" in query in query:
                query = query.replace("google", "")
                searchGoogle(query)
                continue
            elif "pause music" in query:
                pauseSong()
                continue
            elif "resume music" in query:
                resumeSong()
                continue
            elif "what song is currently playing" in query:
                currentlyPlaying()
                continue
            elif "skip song" in query:
                skipSong()
                continue
            elif "previous song" in query:
                previousSong()
                continue
            elif "search artist" in query:
                query = query.replace("search artist", "")
                result = searchForArtist(token, query)
                continue                       
            else:
                speak("Sorry, I didn't quiet get that.")
        elif "thank you" in query:
            speak("You're welcome!")
        elif "goodbye luna" in query:
            speak("Goodbye Alex!")
            exit()
        else:
            print("Not proper saying")
        
            