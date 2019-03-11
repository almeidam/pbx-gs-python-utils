from unittest import TestCase

from api_jira.API_JIRA_Sheets_Sync import API_JIRA_Sheets_Sync
from utils.Dev import Dev
from utils.Json import Json
from utils.aws.Lambdas import Lambdas


class Test_API_JIRA_Sheets_Sync(TestCase):

    def setUp(self):
        self.file_id  = '1yDxu5YxL9FxY5wQ1EEQlAYGt3flIsm2VTyWwPny5RLA'
        self.file_id ='1gc3jQelTJ8250kCZqOhqBOOZUywGOy3AiNC6cghgHak'
        self.api_sync = API_JIRA_Sheets_Sync(self.file_id)


    def test_jira__gsheets(self):
        Dev.pprint(self.api_sync.jira())
        Dev.pprint(self.api_sync.gsheets())

    def test_elastic(self):
        Dev.pprint(self.api_sync.elastic().elastic.index_list())

    def test_sheet_name_backup(self):
        Dev.pprint(self.api_sync.sheet_name_backup())


    def test_convert_sheet_data_to_raw_data(self):
        sheet_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        raw_data = self.api_sync.convert_sheet_data_to_raw_data(sheet_data)
        Dev.pprint(raw_data)

    def test_color_code_cells_based_on_diff_status(self):
        sheet_data  = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        backup_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name_backup())
        issues      = self.api_sync.get_jira_issues_in_sheet_data(sheet_data)
        diff_cells  = self.api_sync.diff_sheet_data_with_jira_data(sheet_data, backup_data, issues)
        result      = self.api_sync.color_code_cells_based_on_diff_status(diff_cells)
        #Dev.pprint(result)
        #Dev.pprint(diff_cells)


    def test_diff_sheet_data_with_jira_data(self):
        sheet_data  = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        backup_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name_backup())
        issues     = self.api_sync.get_jira_issues_in_sheet_data(sheet_data)
        result     = self.api_sync.diff_sheet_data_with_jira_data(sheet_data, backup_data, issues)
        #Json.save_json('/tmp/tmp_diff_data.json', result)
        Dev.pprint(result)

    def test_get_issue_data(self):
        Dev.pprint(self.api_sync.get_issue_data('RISK-1200'))
        Dev.pprint(self.api_sync.get_issue_data('SL-118'))


    def test_get_jira_issues_in_sheet_data(self):
        sheet_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        issues = self.api_sync.get_jira_issues_in_sheet_data(sheet_data)
        Dev.pprint(len(issues))

    def test_get_sheet_data(self):
        result = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        Dev.pprint(result)

    def test_get_sheet_raw_data(self):
        result = self.api_sync.get_sheet_raw_data()
        Dev.pprint(result)

    def test_update_sheet_data_with_jira_data(self):
        sheet_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        self.api_sync.update_sheet_data_with_jira_data(sheet_data)
        Dev.pprint(sheet_data)

    def test_update_file_with_raw_data(self):
        sheet_data = self.api_sync.get_sheet_data(self.api_sync.sheet_name())
        self.api_sync.update_sheet_data_with_jira_data(sheet_data)
        raw_data   = self.api_sync.convert_sheet_data_to_raw_data(sheet_data)
        self.api_sync.update_file_with_raw_data(raw_data)

    def test_sync_data_between_jira_and_sheet(self):
        diff_cells = self.api_sync.diff_cells()
        #Json.save_json('/tmp/tmp_diff_cells.json',diff_cells)
        #diff_cells = Json.load_json('/tmp/tmp_diff_cells.json')
        self.api_sync.sync_data_between_jira_and_sheet(diff_cells)


    def test_sync_sheet_with_jira__bad_file_id(self):
        self.api_sync.file_id = 'aaaa'
        Dev.pprint(self.api_sync.load_data_from_jira())

    def test_load_data_from_jira(self): Dev.pprint(self.api_sync.load_data_from_jira())
    def test_diff_sheet         (self): Dev.pprint(self.api_sync.diff_sheet         ())
    def test_sync_sheet         (self): Dev.pprint(self.api_sync.sync_sheet         ())

    def test__lambda_update(self):
        Lambdas('gs.elastic_jira').update_with_src()





