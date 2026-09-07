"""
A simple GUI app to show Islamic prayer and related times of the day for a given location based on calculations by Institute of Geophysics, University of Tehran.
On the first run you will be asked to provide the location data (city & country).  Submitted location data is verified agianst Nominatim (OpenStreetMap) API and will be saved in location.ini file as the default location.  To change the location, simply delete the location.ini file.

Author: DLord
"""

import sys
import urllib.parse
from datetime import date

import FreeSimpleGUI as sg
import requests
from persiantools.jdatetime import JalaliDate, digits

SCRIPT_VERSION = "5.0"
WINDOW_TITLE = f"Islamic Prayer Times by DLord (v{SCRIPT_VERSION})"


def validate_online_openstreetmap(country, city):
    """Verify that the city exists in the specified country using Nominatim."""

    def normalize_text(value):
        """Normalize text for reliable case-insensitive comparison."""
        if not value:
            return ""

        return " ".join(value.strip().casefold().split())

    def normalize_country(value):
        """Normalize common country-name variations."""
        value = normalize_text(value)

        aliases = {
            # United States
            "usa": "united states",
            "u.s.a.": "united states",
            "u.s.a": "united states",
            "u.s.": "united states",
            "u.s": "united states",
            "us": "united states",
            "united states of america": "united states",
            # United Kingdom
            "uk": "united kingdom",
            "u.k.": "united kingdom",
            "u.k": "united kingdom",
            "great britain": "united kingdom",
            # United Arab Emirates
            "uae": "united arab emirates",
            "u.a.e.": "united arab emirates",
            "u.a.e": "united arab emirates",
            # South Korea
            "republic of korea": "south korea",
            "rok": "south korea",
            # Czech Republic
            "czech republic": "czechia",
            # Iran
            "islamic republic of iran": "iran",
        }

        return aliases.get(value, value)

    headers = {
        "User-Agent": (f"IslamicPrayerTimesApp/{SCRIPT_VERSION} (DLord App Contact)"),
        "Accept-Language": "en",
    }

    api_url = "https://nominatim.openstreetmap.org/search"

    params = {
        "city": city,
        "country": country,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 10,
    }

    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return False

        input_city = normalize_text(city)
        input_country = normalize_country(country)

        for result in results:
            address = result.get("address", {})

            # Nominatim may use different fields for populated places.
            possible_city_names = {
                address.get("city"),
                address.get("town"),
                address.get("village"),
                address.get("municipality"),
                address.get("hamlet"),
                address.get("locality"),
            }

            possible_city_names = {
                normalize_text(name) for name in possible_city_names if name
            }

            osm_country = normalize_country(address.get("country", ""))

            # Exact city + country match.
            if input_city in possible_city_names and input_country == osm_country:
                return True

        return False

    except requests.exceptions.RequestException:
        # If Nominatim cannot be reached, validation has failed.
        return False

    except (ValueError, KeyError, TypeError):
        return False


def get_location():
    """Retrieves saved location from file. If not found, prompts user to enter location data."""
    try:
        with open("location.ini", "r", encoding="utf-8") as file:
            content = [item.strip() for item in file.read().split(",")]

            if len(content) < 2 or not content or not content:
                raise ValueError("Invalid or incomplete location format in file")

    except (FileNotFoundError, ValueError):
        sg.theme("DarkGrey5")
        layout = [
            [
                sg.Text("Enter City:", font=("Arial", 12), size=(12, 1)),
                sg.Input(key="-CITY-", size=(20, 1), font=("Arial Bold", 12)),
            ],
            [
                sg.Text("Enter Country:", font=("Arial", 12), size=(12, 1)),
                sg.Input(key="-COUNTRY-", size=(20, 1), font=("Arial Bold", 12)),
            ],
            [
                sg.Button("Submit", font=("Arial", 12), size=6),
                sg.Button("Cancel", font=("Arial", 12), size=6),
            ],
        ]
        window = sg.Window(
            "Location Input", layout, element_justification="Center", resizable=True
        )

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "Cancel"):
                sg.popup(
                    "No Location data provided, Exiting!",
                    font=("Arial", 12),
                    button_justification="c",
                )
                sys.exit()

            if event == "Submit":
                city = values["-CITY-"].strip().capitalize()
                country = values["-COUNTRY-"].strip().capitalize()

                if not city or not country:
                    sg.popup("Location data not complete!", font=("Arial", 12))
                    continue

                is_valid = validate_online_openstreetmap(country, city)
                if not is_valid:
                    sg.popup_error(
                        "The submitted location data is wrong.\nPlease check your spelling and re-enter.",
                        title="Invalid Location",
                        font=("Arial", 11),
                    )
                    continue

                sg.popup(
                    f"Saved Location:\nCity: {city}\nCountry: {country}",
                    font=("Arial", 12), button_justification="c",
                )
                break

        window.close()

        with open("location.ini", "w", encoding="utf-8") as f:
            f.write(f"{city},{country}")
        content = [city, country]

    return content


def get_date() -> str:
    """Returns today's Gregorian date as a formatted string."""
    return date.today().strftime("%A %d-%b-%Y")  # noqa: DTZ011


def get_jalali_date() -> str:
    """Returns today's Jalali date mapped into Persian script string."""
    months = {
        1: "فروردین",
        2: "اردیبهشت",
        3: "خرداد",
        4: "تیر",
        5: "مرداد",
        6: "شهریور",
        7: "مهر",
        8: "آبان",
        9: "آذر",
        10: "دی",
        11: "بهمن",
        12: "اسفند",
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

    today = JalaliDate.today()
    j_year = today.year
    j_month = months[today.month]
    j_day = today.day
    j_weekday = days[today.strftime("%A")]

    today_jalali = f"{j_weekday}، {j_day} {j_month} {j_year}"
    return digits.en_to_fa(today_jalali)


def main():
    location_data = get_location()

    city, country = location_data

    try:
        encoded_address = urllib.parse.quote(f"{city}, {country}")
        api_url = f"http://api.aladhan.com/v1/timingsByAddress?address={encoded_address}&method=7&midnightMode=1"

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 200:
            raise ValueError(f"API rejection error code: {data.get('code')}")

        timings = data["data"]["timings"]

        header1_date = f"{get_date()} - {get_jalali_date()}"
        header2_location = f"\nLocation: {city} - {country}"
        body = (
            f"\n\nFajr: {timings['Fajr']}\nSunrise: {timings['Sunrise']}\n"
            f"Dhuhr: {timings['Dhuhr']}\nAsr: {timings['Asr']}\n"
            f"Sunset: {timings['Sunset']}\nMaghrib: {timings['Maghrib']}\n"
            f"Isha: {timings['Isha']}\nMidnight: {timings['Midnight']}\n\n"
        )

        sg.theme("DarkGrey5")
        output_text = header1_date + header2_location + body

        layout = [
            [sg.Text(output_text, font=("Cascadia Code", 12))],
            [sg.Button("Close", size=8)],
        ]

        window = sg.Window(
            WINDOW_TITLE,
            layout,
            element_justification="c",
            text_justification="c",
            location=(10, 10),
        )

        while True:
            event, _values = window.read()
            if event in (sg.WIN_CLOSED, "Close"):
                break
        window.close()

    except requests.exceptions.RequestException as net_err:  # noqa: F841
        sg.theme("DarkGrey5")
        friendly_error = (
            "Network Connection Error!\n\n"
            "The app was unable to reach aladhan API server.\n"
            "Please verify your internet connection or DNS settings and try again."
        )
        sg.Window(
            title="Connection Error",
            layout=[
                [sg.Text(friendly_error, font=("Arial", 11), text_color="orange")],
                # un-comment following code block to debug connection issues
                # [
                #     sg.Text(
                #         f"Technical details: {net_err}",
                #         font=("Cascadia Code", 9),
                #         text_color="gray",
                #     )
                # ],
                [sg.Button("  Exit  ", size=8)],
            ],
            element_justification="c",
            text_justification="c",
        ).read()

    except (ValueError, KeyError) as app_err:
        sg.theme("DarkGrey5")
        sg.Window(
            title="Application/Data Parsing Error",
            layout=[
                [
                    sg.Text(
                        "Application Data Processing Error!",
                        font=("Arial", 11, "bold"),
                        text_color="red",
                    )
                ],
                [
                    sg.Text(
                        "The server responded, but the software failed to read the data correctly.",
                        font=("Arial", 10),
                    )
                ],
                [
                    sg.Text(
                        f"Technical details: {app_err}",
                        font=("Cascadia Code", 9),
                        text_color="yellow",
                    )
                ],
                [sg.Button("  Exit  ", size=8)],
            ],
            element_justification="c",
            text_justification="c",
        ).read()


if __name__ == "__main__":
    main()
