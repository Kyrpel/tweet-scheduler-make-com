# Tweet Scheduler with Make.com Automation 🚀

A tool that helps you automatically schedule and post tweets. It can read tweet screenshots or text input, create variations, and post them automatically using Make.com.

## Setup Guide

### Step 1: OpenAI API Setup
1. Go to [OpenAI's website](https://platform.openai.com/signup)
2. Create an account or sign in
3. Click on your profile icon → View API Keys
4. Click "Create new secret key"
5. Copy your API key (you'll need it later)

### Step 2: Google Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API:
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create credentials:
   - Go to "Credentials" in left menu
   - Click "Create Credentials" → "Service Account"
   - Fill in service account details
   - Click "Done"
5. Download credentials:
   - Click on your new service account
   - Go to "Keys" tab
   - Add Key → Create New Key → JSON
   - Save the downloaded file as "fotogenie-ai-credentials.json"
6. Create a Google Sheet:
   - Go to [Google Sheets](https://sheets.google.com)
   - Create a new sheet
   - Copy the sheet ID from URL (the long string between /d/ and /edit)
   - Share the sheet with the email from your credentials file

### Step 3: Make.com Setup
1. Create account at [Make.com](https://www.make.com)
2. Create a new scenario
3. Set up Google Sheets trigger:
   ![Google Sheets Setup](./images/google-sheets-setup.jpg)
   - Add "Google Sheets" trigger
   - Connect your Google account
   - Select your spreadsheet
   - Watch for new rows
   - Set "Table contains headers" to Yes

4. Add Twitter/X posting:
   ![Twitter Posting Setup](./images/twitter-posting.jpg)
   - Add "Create a Tweet" action
   - Connect your Twitter account
   - Map the columns:
     - Text = Content column
     - Media = Image column
     - Video = Video column

5. Create multiple scenarios:
   ![Make.com Automation Setup](./images/make-automation.jpg)
   - Duplicate your scenario for each type
   - In each scenario, filter by Type number
   - Example:
     ```
     Scenario 1: Filter where Type = "1"
     Scenario 2: Filter where Type = "2"
     etc.
     ```

### Step 4: Program Setup
1. Copy the configuration template:
   ```
   # On Windows
   copy config.json.example config.json

   # On Mac/Linux
   cp config.json.example config.json
   ```

2. Edit config.json with your details:
   ```json
   {
     "openai_api_key": "your-openai-api-key-from-step-1",
     "google_sheets_id": "your-sheet-id-from-step-2",
     "google_sheets_credentials_file": "fotogenie-ai-credentials.json"
   }
   ```

## Using the Program

1. Start the program:
   ```bash
   # Start backend
   python backend/app.py

   # In new window, start frontend
   npm run dev
   ```

2. Open in browser: http://localhost:5173 or 5174

3. Add tweets two ways:
   - **From Screenshots**: 
     - Click "Instructions" box
     - Press Ctrl+V to paste screenshot
   
   - **Type Manually**:
     - Enter tweets in text box

4. Click "Schedule Tweets"

The program will:
- Process your input
- Create tweet variations
- Add them to Google Sheets
- Make.com will post them automatically

## Sheet Structure
The program creates this structure automatically:
```
| Type | Content | Characters | Image | Video | Status | Date | Time |
|------|---------|------------|--------|-------|--------|------|------|
| 1    | Tweet 1 | 240        | URL1   | -     | Ready  | 2/16 | 9:00 |
```

## Troubleshooting

If you get errors:
1. Check all API keys are correct
2. Ensure Google Sheet is shared correctly
3. Verify Make.com scenarios are running
4. Check your internet connection

## Security Note ⚠️
Never share your:
- config.json file
- API keys
- Credentials file

Need help? Open an issue on GitHub!
