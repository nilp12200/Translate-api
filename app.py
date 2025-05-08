from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

LIBRETRANSLATE_URL = 'https://libretranslate.de'  # Public instance

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()

    if not data or 'q' not in data or 'target' not in data:
        return Response(json.dumps({'error': 'Missing "q" or "target" in request'}, ensure_ascii=False), mimetype='application/json'), 400

    text = data['q']
    src_lang = data.get('source', 'auto')
    dest_lang = data['target']

    try:
        response = requests.post(
            f'{LIBRETRANSLATE_URL}/translate',
            data={
                'q': text,
                'source': src_lang,
                'target': dest_lang,
                'format': 'text'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        if response.status_code != 200:
            return Response(json.dumps({'error': 'Translation failed', 'details': response.text}, ensure_ascii=False), mimetype='application/json'), 500

        result = response.json()
        response_data = {
            'translatedText': result['translatedText'],
            'sourceLanguage': src_lang,
            'targetLanguage': dest_lang
        }
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), mimetype='application/json'), 500


@app.route('/languages', methods=['GET'])
def get_languages():
    try:
        response = requests.get(f'{LIBRETRANSLATE_URL}/languages')
        languages = response.json()
        return Response(json.dumps(languages, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), mimetype='application/json'), 500


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)
