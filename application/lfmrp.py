import requests
import json
import time
import discordrp
import signals
from PySide6.QtCore import Signal
from math import floor

username = "kaneryu"
APIKEY = "cac7f93b7adb2568060f7a5083686233"
APIROOT = "http://ws.audioscrobbler.com/2.0/"
METHOD = "user.getrecenttracks"

def lastFMRequest(params: dict, method: str):
    try:
        params.update({"api_key": APIKEY, "format": "json", "method": method})
        response = requests.get(APIROOT, params=params)
        return json.loads(response.text)
    except Exception as e:
        print("Threw error " + str(e))
        createError("An error has occured", str(e))
        pause()


def get_song_cover_link(track: str, artist: str, nowPlaying: dict = {None: None}):
    if type(nowPlaying) == dict:
        if not None in nowPlaying.keys():
            imageDict: dict
            possibleURLs: list = []
            for imageDict in nowPlaying["image"]:
                if not imageDict["#text"] == "":
                    possibleURLs.append(imageDict["#text"])
            
            if len(possibleURLs) > 0:
                return possibleURLs[-1]
         
    
    params = {"track": track, "artist": artist}
    response = lastFMRequest(params, "track.getInfo")
    try:
        return response["track"]["album"]["image"][-1]["#text"]
    except:
        print("Get song cover link failed completely")
        return ""


def convert_ms_to_min_sec(milliseconds):
    seconds=(milliseconds/1000)%60
    seconds = int(seconds)
    minutes=(milliseconds/(1000*60))%60
    minutes = int(minutes)

    return f"{minutes}:{seconds:02d}"




def get_now_playing(user: str):
    params = {"user": user}
    response = lastFMRequest(params, METHOD)
    lastPlayed = response["recenttracks"]["track"][0]
    if "@attr" in lastPlayed:
        if lastPlayed["@attr"]["nowplaying"] == "true":
            return lastPlayed
        else:
            return None
    else:
        return None

def get_MBID(track: str, artist: str):
    try:
        params = {"track": track, "artist": artist}
        response = lastFMRequest(params, "track.getInfo")
        if "mbid" in response["track"]:
            return response["track"]["mbid"]
        else:
            return None
    except:
        return ""
    
def get_track_length(track: str, artist: str):
    try:
        params = {"track": track, "artist": artist}
        response = lastFMRequest(params, "track.getInfo")
        return int(response["track"]["duration"])
    except:
        print("Get track length failed")
        return 0

def get_track_album(track: str, artist: str):
    try:
        params = {"track": track, "artist": artist}
        response = lastFMRequest(params, "track.getInfo")
        if "album" not in response["track"]:
            return ""
        return response["track"]["album"]["title"]
    except:
        print("Get album failed")
        return ""
        
def get_track_link(track: str, artist: str):
    try:
        params = {"track": track, "artist": artist}
        response = lastFMRequest(params, "track.getInfo")
        return response["track"]["url"]
    except:
        print("get lenth failed")
        return ""
    
lastPlayingHash = ""
presence: discordrp.Presence = None
createError: Signal = None
paused: bool = False

def forceUpdate():
    global lastPlayingHash
    lastPlayingHash = ""

def pause():
    global paused
    paused = True
    if presence == None:
        return
    presence.clear()

def resume():
    global paused
    paused = False
    forceUpdate()
    
def changeUser(newUsername: str):
    global username
    username = newUsername
    forceUpdate()
    
def checkerThread(runByUI = False):
    global lastPlayingHash
    lastPlaying = ""
    iteratonsSinceLastSongChange = 0
    createPresence(runByUI)
    while True:
        try:
            if not paused:
                nowPlaying = get_now_playing(username)
                if nowPlaying:
                    track = nowPlaying["name"]
                    artist = nowPlaying["artist"]["#text"]
                    album = get_track_album(track, artist)
                    try:
                        length = get_track_length(track, artist) / 1000
                    except:
                        length = "Unknown"
                    current = {"track": track,
                            "artist": artist,
                            "album": album,
                            "length": length,
                            #"human": f"{artist} - {track}{", from " + str(album) if not album == "" else ""}",
                            "link": get_track_link(track, artist),
                            "top": f"{track}",
                            "bottom": f"By {artist}, From {album}" if not album == "" else f"By {artist}",
                            }

                else:
                    track = ""
                    artist = ""
                    current = {"track": None, "artist": "Nothing", "album": "Nothing", "length": "Nothing", "human": "Nothing", "link": "https://example.com", "top": "Nothing", "bottom": "Nothing"}
                
                cover_link_ = get_song_cover_link(track, artist, nowPlaying)
                cover_link = "default" if not cover_link_ else cover_link_
                current.update({"coverInternet": cover_link})
                if not lastPlayingHash == hash(json.dumps(current)):
                    # if track changed

                    print(f"changed song to {current['top']} \n{current['bottom']}")
                    if runByUI:
                        signals.signals_.updateSignal.emit(current)
                    iteratonsSinceLastSongChange = 0
                    
                    setPresence(current, runByUI)
                
                lastPlayingHash = hash(json.dumps(current))
                iteratonsSinceLastSongChange += 1
                print(f"checked - waiting {min(iteratonsSinceLastSongChange / 2, 10):.2f} seconds")
                if runByUI:
                    signals.signals_.checkedSignal.emit(float(f"{min(iteratonsSinceLastSongChange / 2, 10):.2f}"))
                
                time.sleep(min(iteratonsSinceLastSongChange / 2, 10))
            elif runByUI:
                if (time.time()) % 2 == 0: # every 2ish seconds
                    signals.signals_.pauseSignal.emit()
        except Exception as e:
            if runByUI:
                print("Throwing error " + str(e))
                createError("An error has occured", str(e))
            else:
                raise e

            
            
def createPresence(runByUi):
    global presence
    
    try:
        presence = discordrp.Presence("1221181347071000637")
    except Exception as e:
        signals.signals_.handleErrorSignal.emit(signals.Errors.presenceCreationError)
        return False
    
    return True

def createSetPresence(currentRaw, runByUi):
    global presence
    try:
        presence = discordrp.Presence("1221181347071000637")
        pres = {
                "state": currentRaw["bottom"],
                "details": currentRaw["top"],
                "timestamps": {
                    "start": int(time.time()),
                },
                "assets": {
                    "large_image": currentRaw["coverInternet"], 
                    "large_text": "Song cover",
                }
        }
        
        if not currentRaw["link"] == "":
            pres.update({"buttons": [
                {
                    "label": "Link",
                    "url": currentRaw["link"],
                }
            ]})
            
        presence.set(pres)
        
    except Exception as e:
        if runByUi:
            print("Throwing error " + str(e))
            createError("There was an error creating the rich prescence", "There was an error creating the rich prescence. The application will now exit")
        else:
            raise e

def setPresence(currentRaw, runByUI):
    global presence
    if presence == None:
        createPresence(runByUI)
    try:
        if currentRaw["track"] == None:
            presence.clear()
            return
        
        pres = {
                "state": currentRaw["bottom"],
                "details": currentRaw["top"],
                "timestamps": {
                    "start": int(time.time()),
                },
                "assets": {
                    "large_image": currentRaw["coverInternet"], 
                    "large_text": "Song cover",
                }
        }
        
        if not currentRaw["link"] == "":
            pres.update({"buttons": [
                {
                    "label": "Link",
                    "url": currentRaw["link"],
                }
            ]})
            
        presence.set(pres)
        
    except Exception:
        createSetPresence(currentRaw, runByUI)
        
if __name__ == "__main__":
    checkerThread()