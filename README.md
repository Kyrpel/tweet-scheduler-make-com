# Tweet Creation & Scheduler with Make.com

A web application that helps create and schedule engaging tweets from various content sources. The app processes text and images, generates tweet variations using GPT-4, and allows scheduling through Google Sheets integration.

## Features

- **Content Processing**
  - Process text input into tweet-friendly format
  - Extract text from images using GPT-4 Vision
  - Process articles from URLs
  - Maintain original message with minimal adjustments

- **Viral Hooks Inspiration**
  - Browse different categories of viral hooks
  - Search and filter hooks
  - Copy hooks to clipboard
  - Categories: Question, Challenge, Story, Authority, Stats

- **Two-Step Publishing**
  1. Process content and review generated tweets
  2. Schedule approved tweets to Google Sheets

## Setup

### 1. Google Sheets Configuration

1. Create a Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API for your project

2. Create Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Fill in service account details
   - Grant "Editor" role for Google Sheets

3. Generate Credentials:
   - Select your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Save the downloaded file as `credentials.json`

4. Create Google Sheet:
   - Create a new Google Sheet
   - Copy the Sheet ID from URL (the long string between /d/ and /edit)
   - Share the sheet with service account email (found in credentials.json)

### 2. Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `backend/requirements.yaml`:
```yaml
name: tweet-scheduler
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.9
  - pip
  - pip:
    - flask
    - flask-cors
    - openai
    - google-auth
    - google-auth-oauthlib
    - google-auth-httplib2
    - google-api-python-client
    - python-dotenv
    - crawl4ai
    - nest-asyncio
```

4. Create conda environment from YAML:
```bash
conda env create -f backend/requirements.yaml
conda activate tweet-scheduler
```

### 3. Frontend Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd tweet-scheduler
```

2. Install dependencies:
```bash
# Frontend
npm install

# Backend
pip install -r requirements.txt
```

4. Start the application:
```bash
# Frontend
npm run dev

# Backend
python backend/app.py
```

### 4. Configuration

Create `config.json` in project root:
```json
{
  "openai_api_key": "your-openai-key",
  "google_sheets_credentials_file": "./credentials.json",
  "google_sheets_id": "your-sheet-id-from-url"
}
```

## Usage

1. **Content Input**
   - Paste text directly
   - Upload/paste images
   - Enter article URLs

2. **Processing**
   - Click "Process Tweets" to generate tweet variations
   - Review and edit generated tweets in textarea

3. **Scheduling**
   - Review processed tweets
   - Click "Send to Google Sheets" to schedule

4. **Viral Hooks**
   - Browse hook categories for inspiration
   - Search for specific hooks
   - Copy hooks to use in tweets

## Tech Stack

- **Frontend**
  - React
  - Vite
  - CSS Modules

- **Backend**
  - Flask
  - OpenAI GPT-4
  - Google Sheets API

## Project Structure

```
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── GPT4_make_scheduler.py # Tweet processing logic
│   ├── vision_processor.py    # Image processing
│   ├── article_processor.py   # URL processing
│   └── hooks_config.py        # Viral hooks configuration
├── src/
│   ├── components/            # React components
│   ├── config/               # Frontend configuration
│   └── App.jsx               # Main React component
├── shared/
│   └── hooks.json            # Shared hooks data
└── scripts/
    └── sync_hooks.py         # Hooks synchronization
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
