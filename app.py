from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import openai
import requests
import tempfile
import json 
from transloadit import client
import os
from quran_checker import check_quran_string, translate_quran_string

app = Flask(__name__)
app.secret_key = os.environ.get('4853453845345893485983948593', default='23400234234023849283948284')

tl = client.Transloadit('0d8f65ea184648c69a259928afab7c80', '0b3a3e5b3717429cbf390e2a1885e12bcd505716')


# Set OpenAI API Key's (need to hide)
API_KEY ="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"
openai.api_key = API_KEY

@app.route('/')
def index():
    return render_template('index.html')   

@app.route('/update_url', methods=['POST'])
def update_url():
    global status, original_url
    status = "transcribing"
    session.clear()
    ssl_url = request.json['ssl_url']
    original_url = request.json['original_url']
    url = requests.get(ssl_url)

    # Download audio file from URL and save it as a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp_file:
        tmp_file.write(url.content)
        tmp_file.flush()
        tmp_file.seek(0)  # Set the file position to the beginning

        # Transcribe audio using OpenAI API
        response = openai.Audio.transcribe(
            model='whisper-1',
            file=tmp_file,
            response_format='vtt',
            language='ar',
            prompt='This is an audio recording of a quran recitation'
        )

        translatedResponse = translate_quran_string(response)

        session['get_vtt_string'] = translatedResponse
        return 'OK'
    
    
@app.route('/get_vtt_string')
def get_vtt_string():
   get_vtt_string = session.get('get_vtt_string')
   session.clear()
   if get_vtt_string:
      return {'get_vtt_string': get_vtt_string}
   else:
      return {'get_vtt_string': None}
   


@app.route('/check_with_quran', methods=['POST'])
def check_with_quran():
    session.clear()
    input_string = request.json["input_string"]
    output_quran_string = check_quran_string(input_string)
    session['output_quran_string'] = output_quran_string
    print(output_quran_string)
    return 'OK'


@app.route('/get_quran_string')
def get_quran_string():
   get_quran_string = session.get('output_quran_string')
   session.clear()
   if get_quran_string:
      return {'get_quran_string': get_quran_string}
   else:
      return {'get_quran_string': None}
   

@app.route('/check_with_translation', methods=['POST'])
def check_with_translation():
    global output_translation_string
    output_translation_string = None
    session.clear()
    input_string = request.json["input_string"]
    output_translation_string = translate_quran_string(input_string)
    return 'OK'


@app.route('/get_translation_string')
def get_translation_string():
   session.clear()
   if output_translation_string:
      return {'output_translation_string': output_translation_string}
   else:
      return {'output_translation_string': None}



@app.route('/add_subtitles', methods=['POST'])
def add_subtitles():
   session.clear()
   vtt_string = request.json['updated_vtt_string']
   
   with tempfile.NamedTemporaryFile(suffix='.vtt') as tmp_vtt_file:
            tmp_vtt_file.write(vtt_string.encode())
            tmp_vtt_file.flush()
            tmp_vtt_file.seek(0)

            status = "subtitling"
            assembly = tl.new_assembly({
                'template_id': 'd011d4497b034b9eb759f4e6662417e1',
                'fields': {
                    'video': original_url
                }
                })
            
            assembly.add_file(open(tmp_vtt_file.name, 'rb'))
            assembly_response = assembly.create(retries=5, wait=True)
            subtitled_ssl_url = assembly_response.data.get("results").get("subtitled")[0].get("ssl_url")
            print(subtitled_ssl_url)
            session['subtitled_ssl_url'] = subtitled_ssl_url
            return 'OK' 
   


@app.route('/get_subtitled_ssl_url')
def get_subtitled_ssl_url():
  subtitled_ssl_url = session.get('subtitled_ssl_url')
  session.clear()

  if subtitled_ssl_url:
    return {'subtitled_ssl_url': subtitled_ssl_url}
  else:
    return {'subtitled_ssl_url': None}



if __name__ == '__main__':
    app.run(debug=True)


    


