import openai
from newspaper import Article
import os, json
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


class GPTAnalyzer:
    SCHEMA = {
        "type": "object",
        "properties": {
            "rating": {
                "type": "string",
                "description": "Bias rating, where -10 is leaning left and 10 is leaning right.",
                "enum": [
                    "-10",
                    "-9",
                    "-8",
                    "-7",
                    "-6",
                    "-5",
                    "-4",
                    "-3",
                    "-2",
                    "-1",
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                ],
            },
            "reasons": {
                "type": "array",
                "description": "Reasons for the given ranking",
                "items": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Short summary or title of the reason",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Detailed explanation or description of the reason",
                        },
                    },
                    "required": ["reason", "explanation"],
                },
            },
            "fallacies": {
                "type": "array",
                "description": "List of fallacies or biases in the article",
                "items": {
                    "type": "object",
                    "properties": {
                        "bias": {
                            "type": "string",
                            "description": "Name of the fallacy or bias",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Description or explanation of the fallacy or bias",
                        },
                    },
                    "required": ["bias", "explanation"],
                },
            },
            "summary": {
                "type": "string",
                "description": "Brief summary of the article",
            },
        },
        "required": ["ranking", "reasons", "fallacies", "summary"],
    }

    @staticmethod
    def analyze_article(text):
        # Based on URL https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking
        # Hardcoded - see original function below
        return json.dumps({
            "rating": "7",
            "reasons": [
                {
                    "reason": "Source of Information",
                    "explanation": "The article heavily relies on quotes from Republican representatives and conservative groups, with no counterpoints or perspectives from Democrats or pro-choice groups.",
                },
                {
                    "reason": "Language and Tone",
                    "explanation": "The language used in the article is emotionally charged and leans towards a conservative viewpoint. Phrases like 'Biden has hijacked PEPFAR', 'false narrative', 'What a lie', 'imposing that on these countries' are indicative of a bias.",
                },
            ],
            "fallacies": [
                {
                    "bias": "Confirmation Bias",
                    "explanation": "The article seems to confirm the conservative viewpoint that the Biden administration is using PEPFAR to promote abortions, without presenting any evidence or arguments from the other side.",
                },
                {
                    "bias": "Cherry Picking",
                    "explanation": "The article selectively presents information that supports its viewpoint, while ignoring or downplaying information that might contradict it.",
                },
            ],
            "summary": "The article discusses the extension of funding for the PEPFAR program by House Republicans, with provisions to prevent funding groups that allegedly promote abortions. The article heavily quotes Republican representatives and conservative groups, accusing the Biden administration of using the program to promote abortions. The article does not present any counterpoints or perspectives from Democrats or pro-choice groups.",
        })

    # TODO: to save money, this method has been hardcoded for now - in final stages, need to uncomment
    # @staticmethod
    # def analyze_article(text):
    #     openai.api_key = os.getenv("OPENAI_API_KEY")

    #     # Call the OpenAI API
    #     completion = openai.ChatCompletion.create(
    #         model="gpt-4-0613",
    #         messages=[
    #             {"role": "system", "content": "You are a helpful assistant."},
    #             {"role": "user", "content": f"Analyze this article for bias: {text}"},
    #         ],
    #         functions=[{"name": "analyze", "parameters": GPTAnalyzer.SCHEMA}],
    #         function_call={"name": "analyze"},
    #         temperature=0,
    #     )

    #     # Extract analysis from the response
    #     analysis = completion.choices[0].message.function_call.arguments
    #     return analysis


if __name__ == "__main__":
    url = "https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking"
    article = Article(url)
    article.download()
    article.parse()

    result = GPTAnalyzer.analyze_article(article.text)
    print(result)
