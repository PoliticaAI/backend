from flask import Flask, jsonify, request, make_response
import threading
import uuid

import services.llm as llm
import services.duckduckgo as ddg
import services.historical as historical

from flask_cors import CORS

from newspaper import Article


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

process_status = {}


def analysis(url, process_id):
    try:
        # Phase 1 - article extraction
        process_status[process_id] = {
            "status": "Downloading and extracting article",
            "progress": 1
        }

        article = Article(url)
        article.download()
        article.parse()
        
        final_response = {
            "title": article.title,
        }

        # Phase 2 - GPT analysis
        while True:
            try:
                process_status[process_id] = {
                    "status": "Running LLM",
                    "progress": 2,
                }

                final_response["gpt_response"] = llm.GPTAnalyzer.analyze_article(article.text)

                break
            except:
                process_status[process_id] = {
                    "status": "Retrying LLM",
                    "progress": 2,
                }
                pass

        # Phase 3 - DuckDuckGo search
        process_status[process_id] = {
            "status": "Running similar article search",
            "progress": 3,
        }

        final_response["ddg_response"] = ddg.SearchEngine.get_links(article.title)
        final_response["ddg_response"] = ddg.SearchEngine.filter_links(final_response["ddg_response"], url)

        # Phase 4 - Historical rating extraction
        process_status[process_id] = {
            "status": "Grabbing historical information",
            "progress": 4,
        }

        final_response["historical"] = historical.HistoricalAnalyzer.get_historical_data(url)

        # Finished!
        process_status[process_id] = {
            "status": "Finished",
            "result": final_response,
            "progress": 5,
        }
    except Exception as e:
        print(e)
        process_status[process_id] = {"status": "Failed", "progress": -1}

    return final_response


@app.route("/start_analysis", methods=["POST"])
def start_analysis():
    print(request.json)
    url = request.json["url"]

    process_id = str(uuid.uuid4())

    task_thread = threading.Thread(target=analysis, args=(url, process_id))
    task_thread.start()

    process_status[process_id] = {"status": "Starting up", "progress": 0}

    # Return the process ID and status URL
    response_data = {"process_id": process_id, "status_url": f"/status/{process_id}"}

    return jsonify(response_data), 202


@app.route("/status/<process_id>", methods=["GET"])
def check_status(process_id):
    if process_id in process_status:
        status = process_status[process_id]["status"]
        progress = process_status[process_id]["progress"]

        if status == "Finished":
            result = process_status[process_id]["result"]
            return jsonify({"status": status, "progress": progress, "result": result})
        elif status == "Failed":
            return jsonify({"status": status, "progress": progress}), 500
        else:
            return jsonify({"status": status, "progress": progress})
    else:
        return jsonify({"error": "Process ID not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5555)
