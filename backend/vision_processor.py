import base64
from typing import List
from openai import OpenAI
import os

class VisionProcessor:
    def __init__(self):
        self.client = OpenAI()

    def encode_image(self, image_file) -> str:
        """Convert image file to base64 string."""
        try:
            # Reset file pointer to beginning
            image_file.seek(0)
            # Read and encode the file
            return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            return None

    def process_images(self, image_files: List, instructions: str = "") -> List[str]:
        """Process multiple images using GPT-4 Vision API."""
        try:
            # Default instruction if none provided
            if not instructions:
                instructions = """
                Please analyze these images and extract all text content:
                1. Extract all text exactly as it appears
                2. Preserve the original formatting and line breaks
                3. Include all relevant text content
                4. Maintain the original structure of the text
                5. Exclude any UI elements or metadata
                6. Do not add any labels or numbering (like "Tweet 1:", "Tweet 2:")
                7. Separate different text blocks with line breaks
                
                Format your response as plain text only.
                Do not add any explanations or formatting.
                Just return the extracted text content.

                
Tweet 2: "Scare a programmer with only one word. Go!"
should be : 
"Scare a programmer with only one word. Go!"
                """

            # Prepare image content list
            image_contents = []
            for image_file in image_files:
                base64_image = self.encode_image(image_file)
                if base64_image:
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })

            if not image_contents:
                return []

            # Prepare the complete message content
            message_content = [{"type": "text", "text": instructions}]
            message_content.extend(image_contents)

            # Make the API call
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Correct model name
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=1000,
                temperature=0.1  # Lower temperature for more accurate extraction
            )

            # Extract the raw text content
            content = response.choices[0].message.content
            
            # Basic cleaning while preserving structure
            text_blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
            
            return text_blocks

        except Exception as e:
            print(f"Error processing images: {str(e)}")
            return []

    def process_image(self, image_file, instructions: str = "") -> List[str]:
        """Process a single image (backward compatibility)."""
        return self.process_images([image_file], instructions)
