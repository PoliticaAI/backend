import unittest
import json
import time

from index import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_start_analysis_endpoint(self):
        request_data = {'url': 'https://www.foxnews.com/politics/house-passes-1-year-africa-aids-relief-extension-with-safeguard-gop-rep-says-stops-biden-abortion-hijacking'}

        response = self.app.post('/start_analysis', data=json.dumps(request_data), content_type='application/json')

        self.assertEqual(response.status_code, 202)

        response_data = json.loads(response.get_data(as_text=True))
        self.assertIn('process_id', response_data)
        self.assertIn('status_url', response_data)

        process_id = response_data['process_id']

        self.check_status_with_timeout(process_id)

    def check_status_with_timeout(self, process_id):

        while True:
            time.sleep(2.5)
            status_response = self.app.get(f'/status/{process_id}')
            status_data = json.loads(status_response.get_data(as_text=True))

            print(status_data)
            
            if status_data['status'] == 'completed' and 'result' in status_data:
                break
            elif status_data['status'] == 'failed':
                self.fail('Analysis failed')
                break

if __name__ == '__main__':
    unittest.main()
