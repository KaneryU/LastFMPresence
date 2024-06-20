# stdlib
import requests
import json
import time
from math import floor
import urllib.parse
import enum

# ext
import discordrp
from PySide6.QtCore import Signal, QTimer, QObject
from PySide6.QtCore import Property as QProperty

# local
import signals
import settings

APIKEY = "cac7f93b7adb2568060f7a5083686233"
APIROOT = "http://ws.audioscrobbler.com/2.0/"

def cleanURL(url: str):
    return urllib.parse.quote_plus(url, safe=":/")

# class lastFMContact(QObject):
    
#     internetConnectionStatusChanged = Signal(bool)
#     lastFMConnectionStatusChanged = Signal(bool)
    
#     def __init__(self):
#         self.internetConnectionStatus = True
#         self.lastFMConnectionStatus = True
    
#     def setICS(self, status: bool):
#         self.internetConnectionStatus = status
    
#     def setLFCS(self, status: bool):
#         self.lastFMConnectionStatus = status
    
#     def getICS(self):
#         return self.internetConnectionStatus

#     def getLFCS(self):
#         return self.lastFMConnectionStatus
    
#     internetConnectionStatus = QProperty(bool, getICS, setICS, notify=internetConnectionStatusChanged)
#     lastFMConnectionStatus = QProperty(bool, getLFCS, setLFCS, notify=lastFMConnectionStatusChanged)
    
#     def checkInternet(self):
#         try:
#             requests.get("https://www.google.com")
#             return True
#         except:
#             return False

#     def checkLastFM(self):
#         try:
#             requests.get(APIROOT)
#             return True
#         except:
#             return False
    
#     def lastFMRequest(self, params: dict, method: str) -> dict:
#         """Make a request to last.fm. This is a low level function that should not be used by the UI. Use the other functions in this class instead.

#         Args:
#             params (dict): Parameters
#             method (str): What method to use

#         Returns:
#             dict: The response from last.fm
#         """
#         if not self.checkInternet():
#             self.internetConnectionStatus = False

#         if not self.checkLastFM():
#             self.internetConnectionStatus = False
        
#         params.update({"api_key": APIKEY, "format": "json", "method": method})
#         response = requests.get(APIROOT, params=params)
#         return json.loads(response.text)

# class discordConnectionStatuses(enum.StrEnum):
#     CONNECTED = "Connected"
#     DISCONNECTED = "Disconnected"
    
#     CONNECTING = "Connecting"
    
#     FAILED = "Failed"
#     RETRYING = "Retrying"
#     RETRYING_SET = "Retrying set"
    
#     NO_PRESENCE_SET = "No presence set"

# class discordConnectionFailedReasons(enum.IntEnum):
#     NONE = -1
#     PRESENCE_CREATION_ERROR = 0
#     PRESENCE_SET_ERROR = 1
#     DISCORD_CLOSED_ERROR = 2
    
#     RETRY_TIMER_ERROR = 3
# class discordRPC(QObject):
#     discordConnectionStatusChanged = Signal(tuple[discordConnectionStatuses, discordConnectionFailedReasons])
    
#     def __init__(self):
#         self.discordConnectionStatus = (discordConnectionStatuses.DISCONNECTED, discordConnectionFailedReasons.NONE)
        
#         self.retryConnectionTimer = QTimer()
#         self.retryConnectionTimer.setInterval(10_000)
#         self.retryConnectionTimer.timeout.connect(self.retry)
        
#         self.retrySetTimer = QTimer()
#         self.retrySetTimer.setInterval(5_000)
#         self.retrySetDict = None
#         self.retrySetTimer.timeout.connect(self.retrySet)
        
#         self.presence = None
        


#     def setDCS(self, status: tuple[discordConnectionStatuses, discordConnectionFailedReasons]):
#         self.discordConnectionStatus = status
    
#     def getDCS(self):
#         return self.discordConnectionStatus

#     discordConnectionStatus = QProperty(tuple[discordConnectionStatuses, discordConnectionFailedReasons], getDCS, setDCS, notify=discordConnectionStatusChanged)
    
#     def retry(self):
#         self.discordConnectionStatus = (discordConnectionStatuses.RETRYING, self.discordConnectionStatus[1])
#         self.connect()
    
#     def connect(self):
#         self.discordConnectionStatus = (discordConnectionStatuses.CONNECTING, discordConnectionFailedReasons.NONE)
        
#         try:
#             self.presence = discordrp.Presence("1221181347071000637")
        
#         except discordrp.ClientIDError:
#             self.discordConnectionStatus = (discordConnectionStatuses.FAILED, discordConnectionFailedReasons.PRESENCE_CREATION_ERROR)
            
#         except discordrp.PresenceError as e:
#             if e.code == 1000: # unknown error
#                 self.discordConnectionStatus = (discordConnectionStatuses.FAILED, discordConnectionFailedReasons.PRESENCE_CREATION_ERROR)

#             self.retryConnectionTimer.start()
            
#         except Exception as e:
#             self.discordConnectionStatus = (discordConnectionStatuses.FAILED, discordConnectionFailedReasons.PRESENCE_CREATION_ERROR)
#             self.retryConnectionTimer.start()

#     def retrySet(self):
#         if self.retrySetDict == None:
#             self.discordConnectionStatus = (discordConnectionStatuses.NO_PRESENCE_SET, discordConnectionFailedReasons.RETRY_TIMER_ERROR)
#             return
        
#         self.discordConnectionStatus = (discordConnectionStatuses.RETRYING_SET, self.discordConnectionStatus[1])
#         self.set(self.retrySetDict)
        
#     def set(self, presence: dict):
#         try:
#             if self.presence == None:
#                 self.connect()
        
#             self.presence.set(presence)
            
#         except discordrp.PresenceError as e:
#             if e.code == 1000:
#                 self.discordConnectionStatus = (discordConnectionStatuses.FAILED, discordConnectionFailedReasons.PRESENCE_SET_ERROR)
            
#             self.retrySetDict = presence
#             self.retrySetTimer.start()
        
#         except Exception as e:
#             self.discordConnectionStatus = (discordConnectionStatuses.FAILED, discordConnectionFailedReasons.PRESENCE_SET_ERROR)
            
#             self.retrySetDict = presence
#             self.retrySetTimer.start()
        
        
#     def close(self):
#         self.presence.close()
#         self.discordConnectionStatus = (discordConnectionStatuses.DISCONNECTED, discordConnectionFailedReasons.NONE)

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



def get_now_playing():
    params = {"user": settings.settings.username}
    response = lastFMRequest(params, "user.getrecenttracks")
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

def get_track_album_title(track: str, artist: str):
    # routes
    # get the album title from the track info
    # or get the album title from the now playing info
    
    def get_album_from_track_info():
        try:
            params = {"track": track, "artist": artist}
            response = lastFMRequest(params, "track.getInfo")
            if not "album" in response["track"]:
                return ""
            return response["track"]["album"]["title"]
        except:
            return ""
    
    def get_album_from_now_playing():
        try:
            nowPlaying = get_now_playing()
            return nowPlaying["album"]["#text"]
        except:
            return ""
    
    try:
        return (get_album_from_now_playing() or get_album_from_track_info())
    except Exception as e:
        print(f"Get album title failed with error: {e}")
        return ""

def get_track_album_link(track: str, artist: str):
    # routes
    # get the album link from the track info
    # or make the album link from the album title and artist
    def link_from_track_info():
        try:
            params = {"track": track, "artist": artist}
            response = lastFMRequest(params, "track.getInfo")
            return response["track"]["album"]["url"]
        except:
            return ""
    
    def link_from_album_title():
        albumTitle = get_track_album_title(track, artist)
        if albumTitle == "":
            return ""
        else:
            url = f"https://www.last.fm/music/{artist}/{albumTitle.replace(' ', '+')}"
            url = cleanURL(url)
            if " " in url:
                return ""
            return url
    
    def link_from_search() -> str:
        try:
            params = {"album": get_track_album_title(track, artist)}
            response = lastFMRequest(params, "album.search")
            
            if len(response["results"]["albummatches"]["album"]) == 0:
                return ""
            
            returnedTitle: str = response["results"]["albummatches"]["album"][0]["name"]
            returnedTitle = returnedTitle.lower()
            if not returnedTitle == get_track_album_title(track, artist).lower():
                return ""
            else:
                return response["results"]["albummatches"]["album"][0]["url"]
        except:
            return ""
    try:
        return (link_from_track_info() or link_from_search() or link_from_album_title())
    
    except Exception as e:
        print(f"Get album link failed with error {e}")
        return ""
        
def get_track_link(track: str, artist: str):
    def get_link_from_track_info():
        try:
            params = {"track": track, "artist": artist}
            response = lastFMRequest(params, "track.getInfo")
            return response["track"]["url"]
        except:
            return ""
    
    def get_link_from_now_playing():
        try:
            nowPlaying = get_now_playing()
            return nowPlaying["url"]
        except:
            return ""
    try:
        return get_link_from_track_info() or get_link_from_now_playing()
    except Exception as e:
        print(f"Fet link failed {e}")
        return ""
    
lastPlayingHash = ""
presence: discordrp.Presence = None
createError: Signal = None
paused: bool = False
running: bool = True

def pad(string: str, length: int):
    return string.ljust(length, " ")

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
    settings.settings.set_username(newUsername)
    
    forceUpdate()
    
def checkerThread(runByUI = False):
    global lastPlayingHash
    lastPlaying = ""
    iteratonsSinceLastSongChange = 0
    createPresence(runByUI)
    while running:
        try:
            if not paused:
                nowPlaying = get_now_playing()

                if not lastPlayingHash == hash(json.dumps(nowPlaying)):
                    # if track changed
                    if nowPlaying:
                        track: str = nowPlaying["name"]
                        artist: str = nowPlaying["artist"]["#text"]
                        album = get_track_album_title(track, artist)
                        
                        # try:
                        #     length = get_track_length(track, artist) / 1000
                        # except:
                        #     length = "Unknown"
                        
                        current = {"track": track,
                                "artist": artist,
                                "album": album,
                                #"length": length,
                                #"human": f"{artist} - {track}{", from " + str(album) if not album == "" else ""}",
                                "link": get_track_link(track, artist),
                                "top": f"{pad(track, 3)}",
                                "bottom": f"By {artist}, From {album}" if not album == "" else f"By {artist}",
                                }
                        
                        cover_link_ = get_song_cover_link(track, artist, nowPlaying)
                        cover_link = "default" if not cover_link_ else cover_link_
                        current.update({"coverInternet": cover_link})
                        current.update({"albumLink": get_track_album_link(track, artist)})
                        
                    else:
                        track = ""
                        artist = ""
                        current = {"track": None, "artist": "Nothing", "album": "Nothing", "length": "Nothing", "human": "Nothing", "link": "", "top": "Nothing", "bottom": "Nothing", "coverInternet": "default", "albumLink": ""}
                        
                    print(f"changed song to {current['top']} \n{current['bottom']}")
                    
                    if runByUI:
                        signals.signals_.updateSignal.emit(current)
                        
                    iteratonsSinceLastSongChange = 0
                    
                    setPresence(current, runByUI)
                
                    lastPlayingHash = hash(json.dumps(nowPlaying))
                    
                iteratonsSinceLastSongChange += 1
                print(f"checked - waiting {min(iteratonsSinceLastSongChange / 2, 5):.2f} seconds")
                if runByUI:
                    signals.signals_.checkedSignal.emit(float(f"{min(iteratonsSinceLastSongChange / 2, 5):.2f}"))
                
                time.sleep(min(iteratonsSinceLastSongChange / 2, 5))
            elif runByUI:
                if (time.time()) // 2 == 0: # every 2ish seconds
                    signals.signals_.pausePulseSignal.emit()
        except Exception as e:
            pass

            
            
def createPresence(runByUi):
    global presence
    try:
        print("Creating new presence")
        presence = discordrp.Presence("1221181347071000637")
    except Exception as e:
        signals.signals_.handleErrorSignal.emit(signals.Errors.presenceCreationError)
        return False
    
    return True

def shortenURL(url: str) -> str:
    API = "https://tinyurl.com/api-create.php?url="
    request = requests.get(API + url)
    return request.text

def pureSetPresence(currentRaw: dict):
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
    
    for i in [i for i in currentRaw.keys() if "link" in i.lower()]:
        print(f"shortening url {i}")
        if len(currentRaw[i]) > 500:
            currentRaw[i] = shortenURL(currentRaw[i])
    
    if not currentRaw["link"] == "":
        pres.update({"buttons": [
            {
                "label": "Song link",
                "url": currentRaw["link"],
            }
        ]})
    
    if not currentRaw["albumLink"] == "":
        if "buttons" in pres:
            pres["buttons"].append({
                "label": "Album link",
                "url": currentRaw["albumLink"],
            })
            
        else:
            pres.update({"buttons": [
                {
                    "label": "Album link",
                    "url": currentRaw["albumLink"],
                }
            ]})
        
    presence.set(pres)
    
def createSetPresence(currentRaw: dict, runByUi):
    global presence, lastPlayingHash
    try:
        print("Creating new presence in csp")
        if not presence == None:
            presence.close()
        presence = discordrp.Presence("1221181347071000637")
        pureSetPresence(currentRaw)
        
    except Exception as e:
        print(str(e))
        print(currentRaw)
        lastPlayingHash = ""

def setPresence(currentRaw, runByUI):
    global presence
    if presence == None:
        createPresence(runByUI)
    try:
        if currentRaw["track"] == None:
            presence.clear()
            return
        
        pureSetPresence(currentRaw)
    except Exception:
        createSetPresence(currentRaw, runByUI)
        
if __name__ == "__main__":
    settings.init_settings()
    if settings.settings.username == "":
        user = input("Enter your last.fm username: ")
        settings.settings.set_username(user)
    
    checkerThread()