from flask import Flask,render_template
import pyaudio
import wave
import json
import os
import webbrowser

from ibm_watson import SpeechToTextV1
from ibm_watson import LanguageTranslatorV3
from ibm_watson import ToneAnalyzerV3
from ibm_watson import TextToSpeechV1



app=Flask(__name__)
@app.route('/')

def home():
    return render_template('home.html')


    



@app.route('/res/') 
def res(): 
    print ('inicia') 
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format = pyaudio.paInt16, channels = 2, rate = 44100, frames_per_buffer = 1024, input = True)
    print('Inicia grabación')
        
    frames = []
    tiempo = 5 #segundos
    for i in range(0, int(44100/1024*tiempo)):
        tmp = stream.read(1024)
        frames.append(tmp)
            
    print('Acaba la captura')
    stream.stop_stream()
    stream.close()
        
    waveFile = wave.open('graba.wav','wb')
    waveFile.setnchannels(2)
    waveFile.setframerate(44100)
    waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    servicio = SpeechToTextV1(iam_apikey ='OOeriH0WxW3wBRZN-yDxnMDVv9psXv-IbUp-sn53rjZ9') 
    with open('graba.wav','rb') as fichero:


        res = json.dumps(servicio.recognize(audio = fichero,timestamps = True,model = 'es-ES_NarrowbandModel', word_confidence = True).get_result(),sort_keys=True ,indent = 2)
        resultado=json.loads(res)
        res=resultado["results"]
        res=res[0]
        res=res["alternatives"]
        res=res[0]
        res=res["transcript"]
             
        print(res)
    audio= res
    #----------------------------------------traduccion----------------------------------------------
    language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey='7cEueFyXfs4saKfm1SfN4xtoxdBgzCIsrO0QFR-9Cbip',
    url='https://gateway.watsonplatform.net/language-translator/api')
    
    translation = language_translator.translate(
    text=res, model_id='es-en').get_result()
    traduccion=json.dumps(translation, indent=2, ensure_ascii=False)
       
    #print(traduccion)
    traduccion=json.loads(traduccion)
    traduccion= traduccion["translations"]
    traduccion= traduccion[0]
    traduccion= traduccion["translation"]
    print(traduccion)
    traduccion1=traduccion
    ##-----------------------------------------------analizador
    tone_analyzer = ToneAnalyzerV3(version = '2017-09-21',iam_apikey = 'lRCEug4lLvSja-Ob6qpnk-to0mAkPu56827xh63SmacD', url = 'https://gateway.watsonplatform.net/tone-analyzer/api'  )
    analizar = tone_analyzer.tone( {'text':traduccion}, content_type='application/json').get_result()
    ton=json.dumps(analizar, indent=2, ensure_ascii=False)
    print(ton)
    #tono=json.loads[tono]
    tono=json.loads(ton)
    tono=tono["document_tone"]
    tono=tono["tones"]
    tono=tono[0]
    tono=tono["tone_name"]
        
    print(tono)

    analizador= tono

    #-------------------------------------------------traduce---------------------------------------
    translation = language_translator.translate(
    text=tono, model_id='en-es').get_result()
    traduccion=json.dumps(translation, indent=2, ensure_ascii=False)
       
    #print(traduccion)
    traduccion=json.loads(traduccion)
    traduccion= traduccion["translations"]
    traduccion= traduccion[0]
    traduccion= traduccion["translation"]
    print(traduccion)
    traduccion2= traduccion
    #-------------------------text to speech
    text_to_speech = TextToSpeechV1(
    iam_apikey='I3L8EDCMNVmp-O-l-PAjBRIvL-5GMvkTVOFdDp26rIuQ',
    url='https://stream.watsonplatform.net/text-to-speech/api'
    )

    #-----------------------------------------------------graba en archivo wav 
    with open('res.wav', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                traduccion,
                voice='es-LA_SofiaVoice',
                accept='audio/wav'        
            ).get_result().content)
    

    

    
    f = open('holamundo.html','w')

    mensaje = """  
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>ProyectoIA</title>

    <link rel="stylesheet" href="static/css/main.css" type = "text/css">


</head>

<body>
    <div id="principal">
    <div id="principal">
    <br>
    <p>Usted dijo: """+audio+"""</p>
    <br>
    <p>traduccion: """+traduccion1+"""</p>
    <br>
    <p>Analizador: """+analizador+"""</p>
    <br>
    <p>Estado de animo: """+traduccion2+"""</p>

    <audio src='res.wav' controls='controls' type='audio/wav' preload='preload'>
    </audio>
    </div>
    
</body>

</html>
    
    """

    f.write(mensaje)
    f.close()

    webbrowser.open_new_tab('holamundo.html')


    #os.system("start Res.wav")
    return traduccion     


if __name__ == '__main__':
    app.run(debug=True)
