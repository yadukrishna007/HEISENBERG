import subprocess
import os
import webbrowser
import pyautogui
import requests
from bs4 import BeautifulSoup
import wikipedia

def open_app(app_path: str):
    try:
        os.startfile(app_path)
    except Exception:
        subprocess.Popen(app_path)

def open_folder(folder: str):
    os.startfile(folder)

def get_installed_apps():
    apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "cmd": "cmd.exe",
        "spotify": "spotify:"
    }
    directories = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")
    ]
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    apps[name] = os.path.join(root, file)
    return apps

def open_website(query_or_url: str):
    if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
        url = query_or_url
    elif "." in query_or_url and " " not in query_or_url:
        url = f"https://{query_or_url}"
    else:
        url = f"https://www.google.com/search?q={query_or_url.replace(' ', '+')}"
    webbrowser.open(url)

def browser_control(action: str):
    if action == "play_pause":
        pyautogui.press('space')
    elif action == "rewind":
        pyautogui.press('left')
    elif action == "forward":
        pyautogui.press('right')

def fetch_info(query: str):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Query is too broad. Did you mean {', '.join(e.options[:3])}?"
    except wikipedia.exceptions.PageError:
        try:
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            result = soup.find('a', class_='result__snippet')
            if result:
                return result.text
            return "I couldn't find specific information on the web about that."
        except Exception:
            return "I couldn't fetch information from the web right now."
    except Exception:
        return "An error occurred while fetching information."