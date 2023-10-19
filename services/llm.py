import openai
from newspaper import Article
import os
from dotenv import load_dotenv

load_dotenv()

class GPTAnalyzer:
    @staticmethod
    def __parse_text(text):
        parsed_text = []
        for i in text.strip().split('\n\n'): 
            for j in i.split('\n'):
                parsed_text.append(j.strip().strip("**"))
        parsed_text = dict([(parsed_text[i], parsed_text[i+1]) for i in range(0, len(parsed_text), 2)])
        return parsed_text

    @staticmethod
    def analyze_article(url):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        article = Article(url)
        article.download()
        article.parse()

        prompt = f"""
        Give an answer and only an answer on a scale of [-10, 10], and make it so that -10
        is left-leaning, and 10 is right-leaning, and 0 is neutral. Make sure it's an estimate,
        which is ok, and it is a priority to only give that format for the answer, and that you 
        bold the answer. Focus less on the direct content of the article and more so on how it is being presented by the news source.
        Think about your thought process, but do not output it in any way or form.
        Bold only the answer, and give the answer in the format of 
        "**[Number]:Neutral/Left/Right**", make sure it is that exact format for the answer.

        After you give the ranking, include a line of 5 equal signs ("=====") here.

        After the line of equal signs, give 3 reasons as to WHY you gave that ranking in the format:
        "**[Very short summary of Reason 1]: [Longer explanation of reason 1]**
        **[Very short summary of Reason 2]: [Longer explanation of reason 2]**
        **[Very short summary of Reason 3]: [Longer explanation of reason 3]**

        Include a line of 5 equal signs ("=====") here.

        Do NOT include a title for this section.
        After the line of equal signs, make a list of 3 that you think are present in the article, using the following format:
        "**[Fallacy/bias 1 name]: [Longer explanation of fallacy/bias 1]**
        **[Fallacy/bias 2 name]: [Longer explanation of fallacy/bias 2]**
        **[Fallacy/bias 3 name]: [Longer explanation of fallacy/bias 3]**
        "

        Make sure everything is in its format. Do NOT add any extra text to attempt to label the information.
        Do NOT include a title for any section of the prompt.

        Article: {article.text}
        """

        response = openai.Completion.create(engine="gpt-3.5-turbo", prompt=prompt, max_tokens=1000)
        text_response = response.choices[0].text.strip()
        
        parsed_response = text_response.split("=====")

        ranking = [i.strip("**").strip() for i in parsed_response[0].strip().split(':')]
        reasons = GPTAnalyzer.__parse_text(parsed_response[1])
        fallacies = GPTAnalyzer.__parse_text(parsed_response[2])

        gpt_response = {
            'ranking': ranking,
            'reasons': reasons,
            'fallacies': fallacies,
            'title': article.title,
            'top_image': article.top_image
        }

        return gpt_response

if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    url = 'https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking'
    result = GPTAnalyzer.analyze_article(url)
    print(result)
