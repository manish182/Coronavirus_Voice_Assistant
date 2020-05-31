import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

api_key = "tt7-NSudZprO"
project_token = "tfv5q1hTLenR"
run_token = "t1s5dyV-xBTw"


class Data:
    def __init__(self, key, token):
        self.key = key
        self.token = token
        self.params = {"api_key": key}
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.token}/last_ready_run/data',
                                params=self.params)
        data = json.loads(response.text)
        return data


    def get_total_cases(self):
        content = self.data['total']
        for name in content:
            if name['name'] == 'Coronavirus Cases:':
                return name['value']

    def get_total_deaths(self):
        content = self.data['total']
        for name in content:
            if name['name'] == 'Deaths:':
                return name['value']
        return "0"

    def get_total_recovered(self):
        content = self.data['total']
        for name in content:
            if name['name'] == 'Recovered:':
                return name['value']
        return "0"

    def get_country_data(self, country):
        content = self.data['country']
        for name in content:
            if name['name'].lower() == country.lower():
                return name
        return "0"

    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())
        return countries

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.token}/run',
                                 params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(20)


        t = threading.Thread(target=poll)
        t.start()




def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()


def main():
    print("Coronavirus voice assistant started")
    end_phrase = "stop"
    data = Data(api_key, project_token)
    country_list = data.get_list_of_countries()
    total_patterns = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ recovered"): data.get_total_recovered,
        re.compile("[\w\s]+ total recovered"): data.get_total_recovered
    }
    country_patterns = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
    }
    update_command = "update"
    while True:
        print("Ask me anything related to COVID 19")
        text = get_audio()
        print(text)
        result = None
        for pattern, func in country_patterns.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in total_patterns.items():
            if pattern.match(text):
                result = func()
                break

        if text == update_command:
            result = "Data is being updated!"
            data.update_data()

        if result:
            print(result)
            speak(result)

        if text.find(end_phrase) != -1:
            print("Exit")
            break


# data = Data(api_key,project_token)
# print(data.get_list_of_countries())
main()