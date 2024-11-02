import os
import requests
import shutil

def setup_swagger_ui():
    # Create necessary directories
    os.makedirs('static/swagger-ui', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)

    # Swagger UI files to download
    files = {
        'swagger-ui-bundle.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js',
        'swagger-ui-standalone-preset.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js',
        'swagger-ui.css': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css'
    }
    
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

    # Create dark theme CSS
    dark_theme_css = """/* Dark theme for Swagger UI */
.swagger-ui {
    background-color: #1c2333;
    color: #e6edf3;
}

.swagger-ui .topbar {
    background-color: #2d333b;
    border-bottom: 1px solid #30363d;
}

.swagger-ui .info .title,
.swagger-ui .info .base-url,
.swagger-ui .info p,
.swagger-ui .info li {
    color: #e6edf3;
}

.swagger-ui .scheme-container {
    background: #2d333b;
    box-shadow: none;
}

.swagger-ui .opblock {
    background: #2d333b;
    border: 1px solid #30363d;
}

.swagger-ui .opblock .opblock-summary {
    border-bottom: 1px solid #30363d;
}

.swagger-ui .opblock-description-wrapper p,
.swagger-ui .response-col_status,
.swagger-ui .response-col_description,
.swagger-ui .parameter__name,
.swagger-ui .parameter__type,
.swagger-ui .parameter__in {
    color: #e6edf3;
}

.swagger-ui .btn {
    background: #2d333b;
    color: #e6edf3;
    border: 1px solid #30363d;
}

.swagger-ui select,
.swagger-ui input[type=text],
.swagger-ui textarea {
    background: #2d333b;
    color: #e6edf3;
    border: 1px solid #30363d;
}

.swagger-ui .model-box,
.swagger-ui section.models {
    background: #2d333b;
    border: 1px solid #30363d;
}

.swagger-ui .model {
    color: #e6edf3;
}

body {
    background-color: #1c2333;
    color: #e6edf3;
}
"""

    # Write dark theme CSS
    with open('static/css/swagger-dark.css', 'w') as f:
        f.write(dark_theme_css)
    print('Created dark theme CSS')
    return True

if __name__ == '__main__':
    setup_swagger_ui()
