import streamlit.components.v1 as components

def camera_input_component():
    """
    Custom camera component that forces rear-facing camera on mobile devices.
    Returns the captured image as base64.
    """
    
    camera_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }
            .camera-container {
                max-width: 100%;
                margin: 0 auto;
                text-align: center;
            }
            .file-input-wrapper {
                position: relative;
                overflow: hidden;
                display: inline-block;
                width: 100%;
                max-width: 400px;
            }
            .btn-camera {
                border: 2px solid #0066cc;
                color: white;
                background-color: #0066cc;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                border-radius: 5px;
                width: 100%;
                transition: all 0.3s;
            }
            .btn-camera:hover {
                background-color: #0052a3;
            }
            .file-input-wrapper input[type=file] {
                font-size: 100px;
                position: absolute;
                left: 0;
                top: 0;
                opacity: 0;
                cursor: pointer;
                width: 100%;
                height: 100%;
            }
            #preview {
                margin-top: 20px;
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .success-msg {
                color: #28a745;
                margin-top: 10px;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="camera-container">
            <div class="file-input-wrapper">
                <button class="btn-camera">📷 Abrir Cámara</button>
                <input type="file" 
                       id="cameraInput" 
                       accept="image/*" 
                       capture="environment">
            </div>
            <div id="message"></div>
            <img id="preview" style="display:none;">
        </div>

        <script>
            const input = document.getElementById('cameraInput');
            const preview = document.getElementById('preview');
            const message = document.getElementById('message');

            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {
                        preview.src = event.target.result;
                        preview.style.display = 'block';
                        message.innerHTML = '<div class="success-msg">✓ Imagen capturada correctamente</div>';
                        
                        // Send data back to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: event.target.result
                        }, '*');
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        </script>
    </body>
    </html>
    """
    
    # Create the component
    component_value = components.html(camera_html, height=600)
    return component_value

