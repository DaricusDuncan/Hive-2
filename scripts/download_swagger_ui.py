import os
import requests

def download_swagger_ui_files():
    # Create directories if they don't exist
    os.makedirs('static/swagger-ui', exist_ok=True)
    
    # Swagger UI files to download
    files = {
        'swagger-ui-bundle.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js',
        'swagger-ui-standalone-preset.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js',
        'swagger-ui.css': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css'
    }
    
    print("Downloading Swagger UI files...")
    
    # Download each file
    for filename, url in files.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with open(f'static/swagger-ui/{filename}', 'wb') as f:
                f.write(response.content)
            print(f'Successfully downloaded {filename}')
        except Exception as e:
            print(f'Failed to download {filename}: {str(e)}')
            return False
    
    return True

if __name__ == '__main__':
    download_swagger_ui_files()
