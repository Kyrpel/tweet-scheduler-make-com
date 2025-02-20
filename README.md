# Tweet Creation from Articles/Screenshots & Social Media
## & Scheduler with Make.com

A web application that helps create and schedule engaging tweets from various content sources. The app processes text and images, generates tweet variations using GPT-4, and 
allows scheduling through Google Sheets integration.

## ✅ Completed Features

- **Content Processing**
  - ✅ Process articles into tweet-friendly format
  - ✅ Extract text from screenshots using GPT-4 Vision
  - ✅ Process TikTok videos with transcription ---> Tweet
  - ✅ Process Instagram videos with transcription ---> Tweet
  - ✅ Process YouTube videos with transcription
  - ✅ Save full transcripts of video content

- **Tweet Generation**
  - ✅ Generate engaging tweets using GPT-4
  - ✅ Maintain original message intent
  - ✅ Include viral hooks and patterns
  - ✅ Auto-format to Twitter length

- **Integration**
  - ✅ Google Sheets scheduling integration
  - ✅ Make.com workflow support

## ⬜ Pending Features

- **Content Processing**
  - ⬜ Direct text to tweet conversion
  - ⬜ Twitter thread creation
  - ⬜ LinkedIn post processing
  - ⬜ Facebook post processing

- **AI Enhancements**
  - ⬜ Multiple tweet variations
  - ⬜ Hashtag suggestions
  - ⬜ Best posting time recommendations

## Examples

### Article to Tweet
Input: Long-form article about AI productivity
Output: "Discover how AI is revolutionizing workplace productivity: New study shows 47% efficiency boost in daily tasks. The key? Integration of smart automation in routine workflows."

### Screenshot to Tweet
Input: Dashboard screenshot showing analytics
Output: "Breaking down the numbers: Our latest analytics reveal a 3x increase in user engagement after implementing these 5 key strategy changes."

### TikTok to Tweet
Input: TikTok about social media automation
Output: "Revolutionize your social media game with AI agents! From automated engagement to smart content curation, discover how AI is changing the future of social media management."

### 1. Fisrt setup the app

![Demo](images/Media1.gif)

### 2. Then setup the below simple make.com workflow

![Demo](images/make.jpg)


## Features

- **Content Processing**
  - Process text input into tweet-friendly format
  - Extract text from images using GPT-4 Vision
  - Process articles from URLs using crawl4ai
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

1. Clone the repository:
```bash
git clone [repository-url]
cd tweet-scheduler
```

2. Backend Setup (Choose A or B):

**Option A: Using Conda (Recommended)**
```bash
# Create and activate conda environment from yml
conda env create -f environment.yml
conda activate tweet-scheduler
```

**Option B: Using Python venv**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend Setup:
```bash
# Install Node.js dependencies
npm install
```

4. Start the Application:
```bash
# Terminal 1: Start Frontend
npm run dev

# Terminal 2: Start Backend
python backend/app.py
```

### Configuration

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

   ![Content Input Demo](images/video%201.gif)

2. **Processing**
   - Click "Process Tweets" to generate tweet variations
   - Review and edit generated tweets in textarea

   ![Processing Demo](images/processing.png)

3. **Scheduling**
   - Review processed tweets
   - Click "Send to Google Sheets" to schedule

   ![Scheduling Demo](images/scheduling.png)

4. **Viral Hooks**
   - Browse hook categories for inspiration
   - Search for specific hooks
   - Copy hooks to use in tweets

   ![Viral Hooks Demo](images/hooks.png)

## Tech Stack

- **Frontend**
  - React
  - Vite
  - CSS Modules

- **Backend**
  - Flask
  - OpenAI GPT-4
  - Google Sheets API
  - crawl4ai (for article extraction)

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
