from flask import Flask, render_template, request, jsonify
from frameutils import Bluetooth
import speech_recognition as sr
from openai import OpenAI
import os
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Bluetooth, OpenAI client, and speech recognizer
bluetooth = Bluetooth()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
recognizer = sr.Recognizer()

# Global variable to control recording
is_recording = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording
    is_recording = True
    threading.Thread(target=record_and_process_audio).start()
    return jsonify({"status": "success", "message": "Started recording"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording
    is_recording = False
    return jsonify({"status": "success", "message": "Stopped recording"})

def record_and_process_audio():
    global is_recording
    with sr.Microphone() as source:
        while is_recording:
            print("Listening...")
            audio = recognizer.listen(source, phrase_time_limit=5)
            try:
                text = recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                gpt_response = get_gpt_response(text)
                display_on_frame(gpt_response)
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def get_gpt_response(text):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a waitress at the Mimosa restaurant. You have won the best waitress award twice and you are the most helpful assistant. Respond to the query respectfully, and answer the questions asked in a very amicable way. You're here to help and serve your customers. Limit your answers to just a sentence"},
            {"role": "user", "content": text}
        ]
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

'''your smart AR glasses must be connected to the bluetooth of the device 
you're running this code on, it will raise errors if the glasses aren't connected.
Although, you can view the audio responses on your terminal/console'''

def display_on_frame(text):
    if not bluetooth.is_connected():
        bluetooth.connect()
    
    bluetooth.send_lua(f"frame.display.set_brightness(15)")
    bluetooth.send_lua("frame.display.clear()")
    
    lua_command = f"frame.display.text('{text}', 282, 182, {{color='WHITE', align='center', valign='center'}})"
    bluetooth.send_lua(lua_command)
    
    bluetooth.send_lua("frame.display.show()")

if __name__ == '__main__':
    app.run(debug=True)
