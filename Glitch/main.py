import speech_recognition as sr #gives computers the ability to interpret, manipulate, and comprehend human language.
import spacy #gives computers the ability to interpret, manipulate, and comprehend human language.
import requests #handles http requests
import os
import time
import wikipediaapi
from gtts import gTTS
from dotenv import load_dotenv
import hidden


#global variables:
recognizer = sr.Recognizer()
nlp = spacy.load('en_core_web_sm') #loads up the english model to process English text. 
running = 1
wiki = wikipediaapi.Wikipedia('english')
load_dotenv()



#AI Tools
def speak_command(text): #Program talking
    text = text.replace("'", "\\")
    language = 'en-in'
    tts = gTTS(text=text, lang='en-in')
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)
    os.system(f'afplay {temp_file}')
    os.remove(temp_file)
    return

def voiceRecorder(): #Deals with Audio Input
    recognizer = sr.Recognizer() #process the audio data and converts it into text for the computer to understand.
    while running == 1:
    #Prepation Audio Step

        with sr.Microphone() as source:  #sets up the microphone to capture audio.
            print("Adjusting for ambient noise...")  
            recognizer.adjust_for_ambient_noise(source, duration=0.5) #gives the recognizer 1 second to listen and understand the background noise ot ignore them
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5) #puts together the previous lines, so the recognizer can officially listen and record audio from mic

        #Processing Audio step

        try:
            text = recognizer.recognize_google(audio) #Takes the audio from the with block and accurately transcribes the speech into text.
            print(f"Glitch thinks you said : {text}")
            process_text(text) #running the process_text() function to break down the spoken text.
        except sr.UnknownValueError: #Raises this Error if the recognizer could not understand the audio.
            print("Sorry, I could not understand the audio.")
            speak_command("Sorry, I could not understand the audio.")
        except sr.RequestError as e: #Raises this Error if there is an issue with the recognition request. ex: network
            print(f"Glitch could not request results; {e}")
            speak_command("Glitch could not request results; {e}")

def process_text(text): #Processes and interprets the given text.
    doc = nlp(text)
    for token in doc:
        tok = (f"Token: {token.text}, POS: {token.pos_}, Dependency: {token.dep_}")
    if "weather" in text.lower():
        city = text.split()[-1]
        get_weather(city)
    elif "news" in text.lower():
        get_news()
    elif "goodbye" in text.lower() or "good bye" in text.lower():
        byebye()
    elif "search wikipedia for" in text.lower():
    # Find the position where 'search wikipedia for' ends
        start_pos = text.lower().find('search wikipedia for') + len('search wikipedia for')
        query = text[start_pos:].strip()  # Extract everything after that
        print(f"Extracted query: '{query}'")
        fetch_wikipedia_summary(query)
    else:
        ai_chat(text)
    
def byebye(): #exits out of the program
    speak_command("Have a great day Boss.")
    global running
    running = 0
#Main Functions
def get_weather(city): #Fetches chosen city's weather conditions
  
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={hidden.weather_api}&units=imperial" #specifies where to get the data from
    response = requests.get(url) #getting information from that url

    if response.status_code == 200: #checks if the request was successful
        data = response.json() #converts json information into a python dictionary
        weather = data['weather'][0]['description'] #extracts the weather's information from the dictionary
        temperature = data['main']['temp'] #extracts the temperature from the dictionary
        print(f"The weather in {city} is {weather} with a temperature of {temperature}°F.")
        speak_command(f"The weather in {city} is {weather} with a temperatuer of {temperature}°F")
    else:
        print("Sorry boss, Glitch was unable to fetch the weather information.")
        speak_command("Sorry boss, Glitch was unable to fetch the weather information.")

def get_news():  #Fetches Latest World wide news
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={hidden.news_api}" #specifies where to get the data from

    try:
        response = requests.get(url) #Sends a Get request to gain information from that URL
        response.raise_for_status()  # Checks if the request was successful

        data = response.json() #converts the json format information into python and saves it in a new variable
        articles = data['articles'] #Extracts a list of articles from json data
        top_headlines = [] #an empty list
        for i, article in enumerate(articles[:5]): #loops over the article variable 5 times and extracts 5 articles.
            headline = f"{i + 1}. {article['title']}" #adds the 5 articles in headlines variable alongside the article and its title
            print(headline)
            top_headlines.append(headline) # adds the headline variable to the top_headlines list.

        speak_command("Fetching the latest news for you")
        headlines_text = " ".join(top_headlines) #merges the news in one line, seperated by spaces
        speak_command(headlines_text)

    except requests.exceptions.RequestException as e: #if program deals with any error regarding requests.
        error_message = f"Sorry boss, Glitch was unable to fetch the news. Error: {e}"
        print(error_message)
        speak_command("Sorry boss, Glitch was unable to fetch the news")

def fetch_wikipedia_summary(query):
    speak_command("Working on it Boss. Give me a couple of seconds.")
    try:
        page = wiki.page(query) #fetches a wiki page for the given query.
        if page.exists(): #checks if the page exists
            summary = page.summary[:1000]  # Get the first 1000 characters
            print(summary)
            speak_command(summary)

            time.sleep(1)  # Short pause before asking for continuation

            speak_command("Would you like me to continue reading, Boss? Please say 'continue' to proceed or 'stop' to end.")

            with sr.Microphone() as source: #opens the microphone to listen
                print("Waiting for 'continue' or 'stop' command...") 
                recognizer.adjust_for_ambient_noise(source, duration=0.5) #gives the mic 0.5 seconds to cut out the background noise
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5) #listens for up to 5 seconds or till a phrase of 5 seconds is said

            try:
                response = recognizer.recognize_google(audio) #converts what the user said, to text.
                print(f"User said: {response}")

                if response.lower() == 'continue': #checks if the user said "continue"
                    remaining_summary = page.summary[1000:]  # Get the rest of the summary
                    chunk_size = 1000 #sets the size of each chunk of text, to be read at a time.

                    for i in range(0, len(remaining_summary), chunk_size): #loops through the remaining page in chunks of 1000 characters
                        chunk = remaining_summary[i:i + chunk_size]  # Proper slicing
                        print(chunk)
                        speak_command(chunk)
                        time.sleep(2)  # Small pause between chunks to avoid cutting off speech
                else:
                    speak_command("Got it. Stopping the summary.")
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
                speak_command("Sorry, I could not understand the audio. Stopping the summary.")
            except sr.RequestError as e:
                print(f"Error recognizing command: {e}")
                speak_command("Error recognizing command. Stopping the summary.")
        else:
            print(f"Page for '{query}' does not exist on Wikipedia.")
            speak_command(f"Sorry, Boss. The page for '{query}' was not found.")
    except Exception as e:
        print(f"Error fetching Wikipedia page: {e}")
        speak_command("There was an error fetching information from the Wikipedia page.")
        return

def ai_chat(text): 
    url = "https://api.cohere.ai/generate"
    headers = {
        'Authorization': f'Bearer {hidden.ai_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'command-xlarge-nightly',  # Use the model available to you
        'prompt': text,
        'max_tokens': 500,   # Number of tokens in the generated output
        'temperature': 0.7, # Controls randomness; lower is more deterministic

    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_json = response.json()
        if 'text' in response_json:
            # Parse the generated text from the response
            generated_text = response_json['text']
            print("Generated Text:", generated_text)
            speak_command(generated_text)

        else:
            print("Error: 'text' key is missing in the response.")
            speak_command("Error: 'text' key is missing in the response.")
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__": 
     #Program Running
    voiceRecorder()
    #prevoiceRecorder('/Users/Arsalan/Desktop/AI/Audio_files/output.wav')
   #get_weather("houston")
    #get_news()
    #byebye()
    #fetch_wikipedia_summary("salman khan")
   #ai_chat('tell me a short story')
   
    
    









