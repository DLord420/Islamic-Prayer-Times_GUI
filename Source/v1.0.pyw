"""A simple script to show Islamic prayer and related times for Tehran (Tajrish), Iran.  DLord"""

import sys
from datetime import date
import tkinter as tk
import requests
from persiantools.jdatetime import JalaliDate

SCRIPT_VERSION = '1.0'
WINDOW_TITLE = f"Islamic Prayer Times by DLord (version {SCRIPT_VERSION})"


def get_date() -> str:
    """Get todays date and retuen formated string."""
    today = date.today()
    return today.strftime("%A %d-%b-%y")


def get_jalali_date() -> str:
    """Get todays date based on Jalali Calendar and return formated string."""
    months = {
        '1': 'Farvardin',
        '2': 'Ordibehesht',
        '3': 'Khordad',
        '4': 'Tir',
        '5': 'Mordad',
        '6': 'Shahrivar',
        '7': 'Mehr',
        '8': 'Aban',
        '9': 'Azar',
        '10': 'Day',
        '11': 'Bahman',
        '12': 'Esfand',
    }
    jdate = str([JalaliDate.today()])[12:-2]
    jlist = jdate.replace(' ', '').split(',')
    todayJ = jlist[3] + ', ' + jlist[2] + \
        ' ' + months[jlist[1]] + ', ' + jlist[0]
    return todayJ


if __name__ == '__main__':

    try:
        root = tk.Tk()
        root.title(WINDOW_TITLE)
        response = requests.get(
            "http://api.aladhan.com/v1/timingsByAddress?address=Tajrish%2C+Tehran%2C+Iran&method=7&midnightMode=1", timeout=10)
        response.raise_for_status()
        timings = response.json()['data']['timings']

        header = 'Azan times for: ' + get_date() + '  -  ' + get_jalali_date()
        message1 = tk.Label(root, text=header, font='firacode 14 bold',
                            fg="blue", bd=15, relief='raised', padx=5)
        message1.pack()

        body = f"\nAzan Sobh: {timings['Fajr']}\nSunrise: {timings['Sunrise']}\nAzan Zohr: {timings['Dhuhr']}\nAzan Asr: {timings['Asr']}\nSunset: {timings['Sunset']}\nAzan Maghreb: {timings['Maghrib']}\nAzan Ashaa: {timings['Isha']}\nMidnight: {timings['Midnight']}"
        message2 = tk.Label(root, text=body, font='firacode 12 bold',
                            relief='raised', bd=10, padx=5, fg='coral')
        message2.pack()

        root.mainloop()
    except (requests.exceptions.RequestException, ValueError) as e:
        sys.exit(f"An error occurred: {e}")
    except KeyboardInterrupt:
        sys.exit("\nScript terminated by user.")
