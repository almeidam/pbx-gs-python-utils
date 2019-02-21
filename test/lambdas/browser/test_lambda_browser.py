import base64
import unittest

from utils.Dev import Dev
from utils.Process import Process
from utils.aws.Lambdas import Lambdas


class Test_Lambda_lambda_browser(unittest.TestCase):
    def setUp(self):
        self.lambda_browser = Lambdas('browser.lambda_browser',memory=3008)

    def _save_png_file(self, png_data):
        png_file = '/tmp/lambda_png_file.png'
        if png_data:
            with open(png_file, "wb") as fh:
                fh.write(base64.decodebytes(png_data.encode()))

    def test_just_update(self):
        self.lambda_browser.update_with_src()

    def test_update_and_invoke(self):
        payload ={ "params" : []}
        result = self.lambda_browser.update_with_src().invoke(payload)
        Dev.pprint(result)

    def test_markdown(self):
        #payload = {"params": ['markdown'] }
        payload = {"params": ['markdown', '# title from Lambda\n', "normal text"]}
        png_data = self.lambda_browser.update_with_src().invoke(payload)
        #Dev.pprint(png_data)
        self._save_png_file(png_data)

    def test_screenshot_png(self):
        url = 'https://www.google.co.uk'
        url = 'http://news.bbc.co.uk/aaaa'
        #url = 'http://visjs.org/'
        #url ='https://www.o2.co.uk'
        #url = 'https://www.slack.com'
        payload = {"params": ['screenshot_png',url]}
        png_data = self.lambda_browser.update_with_src().invoke(payload)
        self._save_png_file(png_data)

    def test_screenshot(self):
        team_id = 'T7F3AUXGV'
        channel = 'DDKUZTK6X'
        url = 'https://www.google.co.uk/aaa'
        url = 'https://news.bbc.co.uk/aaa'
        #url = 'http://visjs.org/'

        payload = {"params": ['screenshot', url,], 'data': {'channel':channel, 'team_id': team_id}}
        self.lambda_browser.update_with_src()
        result = self.lambda_browser.invoke(payload)
        Dev.pprint(result)

    def test_list(self):
        payload = {"params": ['list']}
        result = self.lambda_browser.update_with_src().invoke(payload)
        Dev.pprint(result)

    def test_lambda_status(self):
        payload = {"params": ['lambda_status']}
        result = self.lambda_browser.update_with_src().invoke(payload)
        Dev.pprint(result)

    def test_render__bootstrap_cdn(self):
        payload = {"params": ['render','/examples/bootstrap-cdn.html',0,0,600,50]}
        #self.lambda_browser.update_with_src()
        png_data = self.lambda_browser.invoke(payload)
        self._save_png_file(png_data)

    def test_render__cup_of_team(self):
        payload = {"params": ['render','examples/wardley_map/cup-of-tea.html']}
        #self.lambda_browser.update_with_src()
        png_data = self.lambda_browser.invoke(payload)
        self._save_png_file(png_data)

    # def test_use_api_browser(self):
    #     url = 'https://www.google.co.uk/aaaaaasd'
    #     payload  = {"params": ['use_api_browser', url]}
    #
    #     self._save_png_file(png_data)