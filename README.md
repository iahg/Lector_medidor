# Electric Meter Reader

A professional Streamlit application for automated electric meter analysis using OpenAI's Vision API. This application works on desktop and mobile devices (iOS Safari and Android Chrome).

## Features

- **Mobile Camera Support**: Capture meter images directly from your phone's camera
- **AI-Powered Analysis**: Uses OpenAI GPT-4 Vision to:
  - Extract meter readings
  - Assess reading quality and confidence
  - Evaluate meter condition
  - Provide maintenance recommendations
- **Professional Results**: Display analysis in structured tables and metrics
- **Customizable**: Configure prompts and expected output format

## Deployment to Streamlit Cloud

### Prerequisites
- A GitHub account
- An OpenAI API key (get one at https://platform.openai.com/api-keys)

### Steps to Deploy

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Electric Meter Reader app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository, branch (main), and main file (app.py)
   - Click "Deploy"

3. **Configure the App**:
   - Once deployed, open the app
   - Go to the "Configuration" tab
   - Enter your OpenAI API key
   - The key is stored only in your session and never saved

### Mobile Usage

The app is optimized for mobile browsers:
- **iOS**: Use Safari browser
- **Android**: Use Chrome browser

The camera input feature will work natively on mobile devices, allowing you to capture meter images directly.

## Local Development

To run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. **Main Tab**:
   - Capture an image using your camera
   - Click "Process Image" to analyze
   - View results in structured tables
   - Download results as JSON

2. **Configuration Tab**:
   - Enter your OpenAI API key
   - Customize the analysis prompt
   - Modify the expected JSON output structure
   - Reset to defaults if needed

## Security Notes

- API keys are stored only in session state and are never persisted
- For production use, consider using Streamlit secrets management
- Never commit API keys to your repository

## License

This project is provided as-is for meter reading automation purposes.

