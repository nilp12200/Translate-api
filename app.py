from flask import Flask, request, Response
import requests
import json
import os
from flask_cors import CORS  # Add CORS support

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Try multiple translation services if one fails
TRANSLATION_SERVICES = [
    'https://libretranslate.de',
    'https://translate.astian.org'
]

# Get port from environment variable (Render sets this automatically)
port = int(os.environ.get('PORT', 10000))

@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to check if the service is running"""
    return Response(json.dumps({'status': 'ok', 'message': 'Service is running'}), 
                   mimetype='application/json')

@app.route('/translate', methods=['POST', 'OPTIONS'])
def translate():
    # Handle preflight CORS requests
    if request.method == 'OPTIONS':
        return Response('', 204)
        
    # Process actual translation requests
    try:
        data = request.get_json()
        if not data or 'q' not in data or 'target' not in data:
            return Response(
                json.dumps({'error': 'Missing "q" or "target" in request'}, ensure_ascii=False), 
                mimetype='application/json'
            ), 400
            
        text = data['q']
        src_lang = data.get('source', 'auto')
        dest_lang = data['target']
        
        # Try each translation service until one works
        last_error = None
        for service_url in TRANSLATION_SERVICES:
            try:
                response = requests.post(
                    f'{service_url}/translate',
                    data={
                        'q': text,
                        'source': src_lang,
                        'target': dest_lang,
                        'format': 'text'
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=15  # Increased timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_data = {
                        'translatedText': result['translatedText'],
                        'sourceLanguage': src_lang,
                        'targetLanguage': dest_lang,
                        'service': service_url  # Include which service was used
                    }
                    return Response(json.dumps(response_data, ensure_ascii=False), 
                                   mimetype='application/json')
                else:
                    last_error = f"Service {service_url} returned status {response.status_code}: {response.text}"
            except Exception as e:
                last_error = f"Service {service_url} error: {str(e)}"
                continue  # Try the next service
                
        # If we got here, all services failed
        return Response(
            json.dumps({'error': 'All translation services failed', 'details': last_error}, ensure_ascii=False),
            mimetype='application/json'
        ), 503
            
    except Exception as e:
        return Response(
            json.dumps({'error': 'Request processing error', 'details': str(e)}, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/languages', methods=['GET'])
def get_languages():
    # Try each translation service until one works
    last_error = None
    for service_url in TRANSLATION_SERVICES:
        try:
            response = requests.get(f'{service_url}/languages', timeout=15)
            if response.status_code == 200:
                languages = response.json()
                return Response(json.dumps(languages, ensure_ascii=False), 
                               mimetype='application/json')
            else:
                last_error = f"Service {service_url} returned status {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Service {service_url} error: {str(e)}"
            continue  # Try the next service
            
    # If we got here, all services failed
    return Response(
        json.dumps({'error': 'All language services failed', 'details': last_error}, ensure_ascii=False),
        mimetype='application/json'
    ), 503

if __name__ == '__main__':
    print(f"Starting translation API server on port {port}")
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)