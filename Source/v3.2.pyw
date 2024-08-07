"""
A simple GUI app to show Islamic prayer and related times for Tehran (Tajrish), Iran.  You could simply change the Country, City, and Area.  It also shows today weather for the specified city.  DLord
"""

import sys
from datetime import date
from io import BytesIO, StringIO

import certifi
import pycurl
import PySimpleGUI as sg
import requests
from art import tprint
from persiantools.jdatetime import JalaliDate, digits

SCRIPT_VERSION = "3.2"
WINDOW_TITLE = f"Islamic Prayer Times by DLord (v{SCRIPT_VERSION})"

# Here you can change the location info:
Area = "Tajrish"
City = "Tehran"
Country = "Iran"


def get_date() -> str:
    """Get todays date and retuen formated string."""
    today = date.today()
    return today.strftime("%A %d-%b-%y")


def get_jalali_date() -> str:
    """Get todays date based on Jalali Calendar and return formated string."""
    months = {
        "1": "فروردین",
        "2": "اردیبهشت",
        "3": "خرداد",
        "4": "تیر",
        "5": "مرداد",
        "6": "شهریور",
        "7": "مهر",
        "8": "آبان",
        "9": "آذر",
        "10": "دی",
        "11": "بهمن",
        "12": "اسفند",
    }
    days = {
        "Shanbeh": "شنبه",
        "Yekshanbeh": "یکشنبه",
        "Doshanbeh": "دوشنبه",
        "Seshanbeh": "سه شنبه",
        "Chaharshanbeh": "چهارشنبه",
        "Panjshanbeh": "پنج شنبه",
        "Jomeh": "جمعه",
    }
    jdate = str([JalaliDate.today()])[12:-2]
    jlist = jdate.replace(" ", "").split(",")
    todayJ = days[jlist[3]] + ", " + jlist[2] + " " + months[jlist[1]] + ", " + jlist[0]
    return digits.en_to_fa(todayJ)


def ascii_art() -> None:
    """Print an ascii art with random font of author's name."""
    author = "DLord"
    tprint("\n\n" + author, font="random")


def get_weather(loc) -> str:
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"https://wttr.in/{loc}?format=1")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    try:
        c.perform()
        c.close()
        body = (buffer.getvalue()).decode("utf-8")
    except pycurl.error:
        body = "Weather data not available!"
    return body


if __name__ == "__main__":
    try:
        tmp = sys.stdout
        my_result = StringIO()
        sys.stdout = my_result
        response = requests.get(
            f"http://api.aladhan.com/v1/timingsByAddress?address={Area}%2C+{City}%2C+{Country}&method=7&midnightMode=1",
            timeout=10,
        )
        response.raise_for_status()
        timings = response.json()["data"]["timings"]
        print("Azan times for: ", get_date(), "-", get_jalali_date())
        print(f"Location: {City} ({Area}) - {Country}")
        print(get_weather(City))
        print(
            f"\nAzan Sobh: {timings['Fajr']}\nSunrise: {timings['Sunrise']}\nAzan Zohr: {timings['Dhuhr']}\nAzan Asr: {timings['Asr']}\nSunset: {timings['Sunset']}\nAzan Maghreb: {timings['Maghrib']}\nAzan Ashaa: {timings['Isha']}\nMidnight: {timings['Midnight']}"
        )
        ascii_art()
        sys.stdout = tmp
        sg.theme("DarkGrey5")
        layout = [
            [sg.Text(my_result.getvalue(), font=("Cascadia Code", 12))],
            [sg.Button("Close")],
        ]
        window = sg.Window(
            WINDOW_TITLE, layout, element_justification="c", text_justification="c"
        )
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Close":
                break
        window.close()
    except (requests.exceptions.RequestException, ValueError) as e:
        sg.theme("DarkGrey5")
        sg.Window(
            title="Error",
            layout=[
                [sg.Text(("Connenction error...!"), font=("Cascadia Code", 12))],
                [sg.Button("  Exit  ")],
            ],
            element_justification="c",
            text_justification="c",
        ).read()
