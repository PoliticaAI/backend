from flask import Flask, jsonify, request, make_response
import threading
import uuid

import services.llm as llm
import services.duckduckgo as ddg

app = Flask(__name__)

process_status = {}

@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    url = request.json['url']

    def analysis(url):
        try:
            while True:
                try:
                    process_status[process_id] = {'status': 'running llm', 'progress': 1}
                    gpt_response = llm.GPTAnalyzer.analyze_article(url)
                    break
                except:
                    process_status[process_id] = {'status': 'retrying llm', 'progress': 1}
                    pass

            process_status[process_id] = {'status': 'finished llm', 'progress': 2}

            ddg_response = ddg.SearchEngine.get_links(gpt_response['title'])
            ddg_response = ddg.SearchEngine.filter_links(ddg_response, url)

            process_status[process_id] = {'status': 'finished ddg', 'progress': 3}

            final_response = {
                'gpt_response': gpt_response,
                'ddg_response': ddg_response
            }

            process_status[process_id] = {'status': 'completed', 'result': final_response, 'progress': 4}
        except:
            process_status[process_id] = {'status': 'failed', 'progress': 0}

        return final_response

    process_id = str(uuid.uuid4())

    task_thread = threading.Thread(target=analysis, args=(url,))
    task_thread.start()

    process_status[process_id] = {'status': 'started', 'progress': 0}

    # Return the process ID and status URL
    response_data = {
        'process_id': process_id,
        'status_url': f'/status/{process_id}'
    }

    return jsonify(response_data), 202

@app.route('/status/<process_id>', methods=['GET'])
def check_status(process_id):
    if process_id in process_status:
        status = process_status[process_id]['status']
        progress = process_status[process_id]['progress']

        if status == 'completed':
            result = process_status[process_id]['result']
            return jsonify({'status': status, 'progress': progress, 'result': result})
        elif status == 'failed':
            return jsonify({'status': status, 'progress': progress}), 500
        else:
            return jsonify({'status': status, 'progress': progress})
    else:
        return jsonify({'error': 'Process ID not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
