import re
from openai import OpenAI
from typing import List, Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json
import os

def split_tweets_with_gpt4(text: str) -> List[str]:
    """Splits a string of tweets using the OpenAI GPT-4 API."""
    try:
        # Initialize the client with just the API key
        client = OpenAI()  # It will automatically use the OPENAI_API_KEY environment variable
        
        # Normalize the input text
        text = text.replace('"', '"').replace('"', '"').replace("'", "'").replace('–', '-')
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that processes tweets. For each tweet you should:
1. Remove any numbering at the start
2. Remove any quotes at the start or end
3. Remove all hashtags (e.g., #Motivation)
4. Remove all emojis
5. Preserve the actual message content
6. Preserve line breaks within tweets (when text is structured in multiple lines)
7. Remove any extra whitespace at start/end of lines
8. Convert smart quotes and apostrophes to regular ones
9. Be smart enought and idenify when start a new tweet, when not.
"""
                },
                {
                    "role": "user",
                    "content": f"Please process the following text into individual tweets, applying the cleaning rules for each tweet. Preserve line breaks within tweets when they exist:\n\n{text}\n\nReturn only the cleaned tweets, with a blank line between each tweet."
                }
            ]
        )

        if response.choices:
            content = response.choices[0].message.content.strip()
            tweets = []
            for tweet in content.split("\n\n"):
                if tweet.strip():
                    cleaned_tweet = tweet.strip()
                    cleaned_tweet = cleaned_tweet.replace('"', '"').replace('"', '"')
                    cleaned_tweet = cleaned_tweet.replace("'", "'").replace('–', '-')
                    tweets.append(cleaned_tweet)
            return tweets
        else:
            print("No choices returned from OpenAI API.")
            return []

    except Exception as e:
        print(f"Error during OpenAI API call: {str(e)}")
        raise Exception(f"OpenAI API error: {str(e)}")

class GoogleSheetsManager:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """Initialize Google Sheets connection."""
        self.spreadsheet_id = spreadsheet_id
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()

    def create_header(self):
        """Creates the header row if the sheet is empty."""
        header = [
            ["Date", "Day",
             "Type 1", "Content 1", "Characters 1", "Image 1", "Video 1",
             "Type 2", "Content 2", "Characters 2", "Image 2", "Video 2",
             "Type 3", "Content 3", "Characters 3", "Image 3", "Video 3",
             "Type 4", "Content 4", "Characters 4", "Image 4", "Video 4",
             "Type 5", "Content 5", "Characters 5", "Image 5", "Video 5"]
        ]
        
        self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body={'values': header}
        ).execute()

    def get_last_entry_info(self) -> Tuple[Optional[str], Optional[str], int, int]:
        """Gets the last date, day, and row number from the existing sheet."""
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:Z'
            ).execute()
            
            values = result.get('values', [])
            if len(values) <= 1:  # Only header or empty
                return None, None, 2, 0
            
            last_row = values[-1]
            last_date = last_row[0]
            last_day = last_row[1]
            
            # Check for first empty content column
            first_empty_column = -1
            for i in range(5):
                content_index = 3 + (i * 5)
                if content_index >= len(last_row) or not last_row[content_index]:
                    first_empty_column = i
                    break
            
            if first_empty_column == -1:
                return last_date, last_day, len(values) + 1, 0
            else:
                return last_date, last_day, len(values), first_empty_column
                
        except Exception as e:
            print(f"Error reading sheet: {e}")
            return None, None, 2, 0

    def update_sheet(self, row_number: int, values: List[str]):
        """Updates a row in the sheet."""
        range_name = f'Sheet1!A{row_number}'
        body = {
            'values': [values]
        }
        self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

def add_tweets_to_sheet(
    sheets_manager: GoogleSheetsManager,
    tweets: List[str],
    start_date: str = "15/02/2025",
    start_day: str = "Saturday"
):
    """Adds tweets to the Google Sheet sequentially."""
    last_date, last_day, current_row, start_column = sheets_manager.get_last_entry_info()
    
    date = last_date if last_date else start_date
    day = last_day if last_day else start_day
    
    print(f"Continuing from date: {date}, day: {day}, column: {start_column + 1}")
    
    tweet_index = 0
    column_index = start_column

    while tweet_index < len(tweets):
        # Initialize row data
        row = [date, day]
        content_data = [""] * 25  # 5 blocks of 5 columns each

        # Fill remaining columns in the current row
        while column_index < 5 and tweet_index < len(tweets):
            cleaned_tweet = tweets[tweet_index]
            base_pos = column_index * 5
            
            # Set Type
            content_data[base_pos] = "Text"
            # Set Content
            content_data[base_pos + 1] = cleaned_tweet
            # Set Character count formula
            column_letter = chr(68 + (column_index * 5))
            content_data[base_pos + 2] = f"=LEN({column_letter}{current_row})"
            
            tweet_index += 1
            column_index += 1
        
        # Update the sheet
        sheets_manager.update_sheet(current_row, row + content_data)
        
        if column_index == 5:
            # Reset for next row
            column_index = 0
            current_row += 1
            
            # Update date and day
            day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day)
            day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(day_index + 1) % 7]
            
            # Update date
            date_parts = date.split("/")
            day_number = int(date_parts[0])
            month = int(date_parts[1])
            year = int(date_parts[2])
            
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                days_in_month[1] = 29
            
            day_number += 1
            if day_number > days_in_month[month - 1]:
                day_number = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            
            date = f"{day_number:02d}/{month:02d}/{year:04d}"

if __name__ == "__main__":
    CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
    
    # Print the service account email
    with open(CREDENTIALS_FILE) as f:
        credentials = json.load(f)
        print(f"Share your Google Sheet with this email: {credentials['client_email']}")
    
    # Initialize Google Sheets manager
    sheets_manager = GoogleSheetsManager(CREDENTIALS_FILE, SPREADSHEET_ID)
    
    # Create header if needed
    sheets_manager.create_header()
