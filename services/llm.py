import openai
from newspaper import Article
import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

class GPTAnalyzer:
    SCHEMA = {
        "type": "object",
        "properties": {
            "ranking": {
                "type": "string",
                "description": "Article ranking in terms of bias",
                "enum": ["-10", "-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
            },
            "reasons": {
                "type": "array",
                "description": "Reasons for the given ranking",
                "items": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Short summary or title of the reason"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Detailed explanation or description of the reason"
                        }
                    },
                    "required": ["reason", "explanation"]
                }
            },
            "fallacies": {
                "type": "array",
                "description": "List of fallacies or biases in the article",
                "items": {
                    "type": "object",
                    "properties": {
                        "bias": {
                            "type": "string",
                            "description": "Name of the fallacy or bias"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Description or explanation of the fallacy or bias"
                        }
                    },
                    "required": ["bias", "explanation"]
                }
            },
            "summary": {
                "type": "string",
                "description": "Brief summary of the article"
            }
        },
        "required": ["ranking", "reasons", "fallacies", "summary"]
    }


    @staticmethod
    def analyze_article(url):
        article = Article(url)
        article.download()
        article.parse()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Call the OpenAI API
        completion = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Analyze this article for bias: {article.text}"}
            ],
            functions=[{"name": "analyze", "parameters": GPTAnalyzer.SCHEMA}],
            function_call={"name": "analyze"},
            temperature=0,
        )

        # Extract analysis from the response
        analysis = completion.choices[0].message.function_call.arguments
        return analysis, article.title

if __name__ == "__main__":
    url = 'https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking'
    result = GPTAnalyzer.analyze_article(url)
    print(result)
