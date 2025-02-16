from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import traceback
import json
import sys  
import logging

sys.path.append(str(Path(__file__).parent))

from GPT4_make_scheduler import split_tweets_with_gpt4, GoogleSheetsManager, add_tweets_to_sheet
from vision_processor import VisionProcessor
from article_processor import ArticleProcessor

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Load configuration
config_path = Path(__file__).parent.parent / 'config.json'
with open(config_path) as config_file:
    config = json.load(config_file)

# Make credentials path relative to the project root
credentials_path = Path(__file__).parent.parent / config['google_sheets_credentials_file']

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/schedule', methods=['POST'])
def schedule_tweets():
    try:
        logger.debug("Starting tweet processing")
        all_tweets = []
        raw_text_content = []
        
        # Process images if they exist
        if 'images' in request.files:
            vision_processor = VisionProcessor()
            image_instructions = request.form.get('imageInstructions', '')
            
            logger.debug("Processing images...")
            image_files = request.files.getlist('images')
            if image_files:
                extracted_text = vision_processor.process_images(image_files, image_instructions)
                if extracted_text:
                    raw_text_content.extend(extracted_text)
        
        logger.debug("Processing text content...")
        # Process text tweets if they exist
        if 'tweets' in request.form:
            text_tweets = request.form.get('tweets')
            if text_tweets:
                raw_text_content.append(text_tweets)
        
        # Process all text content through GPT-4
        if raw_text_content:
            logger.debug("Generating tweet variations...")
            combined_text = "\n\n".join(raw_text_content)
            all_tweets = split_tweets_with_gpt4(combined_text)
        
        if not all_tweets:
            return jsonify({'error': 'No tweets were generated from either images or text'}), 400

        logger.debug("Saving to Google Sheets...")
        # Use stored credentials
        openai_key = config.get('openai_api_key')
        sheets_id = config.get('google_sheets_id')
        
        if not credentials_path.exists():
            return jsonify({'error': f'Google credentials file not found at {credentials_path}'}, 400)

        # Set OpenAI API key in environment
        os.environ['OPENAI_API_KEY'] = openai_key

        # Initialize Google Sheets manager
        sheets_manager = GoogleSheetsManager(str(credentials_path), sheets_id)
        
        # Create header if needed
        sheets_manager.create_header()
        
        # Add tweets to sheet
        add_tweets_to_sheet(sheets_manager, all_tweets)

        return jsonify({'message': 'Tweets scheduled successfully'})

    except Exception as e:
        logger.error(f"Error details: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-article', methods=['POST'])
def process_article():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        processor = ArticleProcessor()
        tweet = processor.process_url_sync(url)  # Use sync version
        
        if not tweet:
            return jsonify({'error': 'Failed to process article'}), 400

        return jsonify({'tweet': tweet})

    except Exception as e:
        logger.error(f"Error processing article: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
