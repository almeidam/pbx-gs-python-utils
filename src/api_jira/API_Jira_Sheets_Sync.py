from api_jira.API_Jira_Rest import API_Jira_Rest
from api_jira.API_Jira      import API_Jira
from gs.API_Issues          import API_Issues
from gsuite.GSheets         import GSheets
from utils.Dev              import Dev
from utils.Elastic_Search import Elastic_Search
#from utils.Local_Cache import use_local_cache_if_available, save_result_to_local_cache


class API_Jira_Sheets_Sync:
    def __init__(self, file_id,gsuite_secret_id=None):
        self._gsheets           = None
        self._jira              = None
        self._jira_rest         = None
        self._elastic           = None
        self._sheet_name        = None
        self._sheet_name_backup = None
        self._sheet_id          = None
        self._sheet_id_backup   = None
        self.file_id            = file_id
        self.sheet_title        = 'Jira Data'
        self.backup_sheet_title = 'original_jira_data'
        self.headers            = []
        self.gsuite_secret_id   = gsuite_secret_id
        self.elastic_secret_id  = 'elastic-jira-dev-2'
        if not self.gsuite_secret_id:
            self.gsuite_secret_id = 'gsuite_gsbot_user'

    # Helper methods
    def elastic(self):
        if self._elastic is None:
            self._elastic =  API_Issues()
        return self._elastic

    def jira(self):
        if self._jira is None:
            self._jira = API_Jira()
        return self._jira

    def jira_rest(self):
        if self._jira_rest is None:
            self._jira_rest = API_Jira_Rest()
        return self._jira_rest


    def gsheets(self):
        if self._gsheets is None:
            self._gsheets = GSheets(gsuite_secret_id=self.gsuite_secret_id)
        return self._gsheets

    def sheet_name(self):
        if self._sheet_name is None:
            sheets = self.gsheets().sheets_properties_by_title(self.file_id)
            if self.sheet_title not in list(set(sheets)):
                self.gsheets().sheets_add_sheet(self.file_id, self.sheet_title)
            self._sheet_name = self.sheet_title
        return self._sheet_name

    def sheet_name_backup(self):
        if self._sheet_name_backup is None:
            sheets = self.gsheets().sheets_properties_by_title(self.file_id)
            if self.backup_sheet_title not in list(set(sheets)):
                self.gsheets().sheets_add_sheet(self.file_id, self.backup_sheet_title)
            self._sheet_name_backup = self.backup_sheet_title
        return self._sheet_name_backup

    def sheet_id(self):
        if self._sheet_id is None:
            sheets = self.gsheets().sheets_properties_by_title(self.file_id)
            if self.sheet_title in list(set(sheets)):
                self._sheet_id = sheets.get(self.sheet_title).get('sheetId')
        return self._sheet_id

    def sheet_id_backup(self):
        if self._sheet_id_backup is None:
            sheets = self.gsheets().sheets_properties_by_title(self.file_id)
            if self.backup_sheet_title in list(set(sheets)):
                self._sheet_id_backup = sheets.get(self.backup_sheet_title).get('sheetId')
        return self._sheet_id_backup


    # main methods

    def convert_sheet_data_to_raw_data(self,sheet_data):
        raw_data = [self.headers]
        for item in sheet_data:
            row = []
            for header in self.headers:
                row.append(item.get(header))
            raw_data.append(row)
        return raw_data

    def get_sheet_raw_data(self, sheet_name):
        return self.gsheets().get_values(self.file_id, sheet_name)

    #@save_result_to_local_cache
    #@use_local_cache_if_available
    def get_sheet_data(self,sheet_name):
        rows = self.get_sheet_raw_data(sheet_name)
        if rows:
            self.headers = rows.pop(0)
            data = []
            for row_index, row in enumerate(rows):
                item = { 'index':row_index}
                for header_index, header in enumerate(self.headers):
                    if header_index >= len(row):
                        value = None
                    else:
                        value  = row[header_index]
                    if header == 'Jira Link' and len(row) > 0:
                        value = '=HYPERLINK("https://jira.photobox.com/browse/{0}","{0}")'.format(row[0])
                    item[header] = value
                data.append(item)
            return data

    def color_code_cells_based_on_diff_status(self, diff_cells):
        sheet_id = self.sheet_id()

        requests = []
        for diff_cell in diff_cells:
            col    = diff_cell.get('col_index')
            row    = diff_cell.get('row_index')
            status = diff_cell.get('status')
            if status == 'same'          : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 0.5 ,1.0 ,0.5))
            if status == 'sheet_change'  : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 1.0 ,0.5 ,0.5))
            if status == 'jira_change'   : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 0.5 ,0.5 ,1.0))
            if status == 'other'         : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 0.5 ,0.5 ,0.5))

            if status == 'jira-save-ok'  : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 0.0 ,0.5 ,0.5))
            if status == 'jira-save-fail': requests.append(self.gsheets().request_cell_set_background_color(sheet_id, col ,row, 1.0 ,0.0 ,0.0))

        return self.gsheets().execute_requests(self.file_id, requests)

    def diff_cells(self):
        sheet_data = self.get_sheet_data(self.sheet_name())
        backup_data = self.get_sheet_data(self.sheet_name_backup())
        if backup_data is None:
            Dev.pprint("Error: Backup data is not setup, please load the data again")
            return None
        jira_issues = self.get_jira_issues_in_sheet_data(sheet_data)
        return self.diff_sheet_data_with_jira_data(sheet_data, backup_data, jira_issues)

    def diff_sheet(self):
        diff_cells = self.diff_cells()
        if diff_cells:
            self.color_code_cells_based_on_diff_status(diff_cells)
            return "diff completed..."
        return "Error, could not calculate diff_cells (try reloading the data)"

    def diff_sheet_data_with_jira_data(self,sheet_data, backup_data, jira_data):
        if backup_data is None or jira_data is None:
            return None
        diff_cells = []
        print()
        for row_index, row in enumerate(sheet_data):
            try:
                for header_index, header in enumerate(self.headers):
                    key = row['Key']
                    jira_issue    = jira_data.get(key)
                    backup_issue  = backup_data[row_index]
                    if jira_issue and backup_issue:
                        if header in ['Jira Link']: continue
                        sheet_value  = row.get(header)
                        backup_value = backup_issue.get(header, '')
                        jira_value   = jira_issue.get(header,'')

                        if sheet_value:
                            diff_cell = {
                                            'key'         : key          ,
                                            'field'       : header       ,
                                            'row_index'   : row_index + 1,
                                            'col_index'   : header_index ,
                                            'sheet_value' : sheet_value  ,
                                            'backup_value': backup_value ,
                                            'jira_value'  : jira_value   ,

                                        }
                            if   sheet_value == jira_value and sheet_value == backup_value: diff_cell['status'] = 'same'
                            elif sheet_value != jira_value and sheet_value == backup_value: diff_cell['status'] = 'jira_change'
                            elif sheet_value != jira_value and jira_value  == ''          : diff_cell['status'] = 'sheet_change'
                            elif sheet_value != jira_value and jira_value  is None        : diff_cell['status'] = 'sheet_change'
                            elif sheet_value != jira_value and jira_value  == backup_value: diff_cell['status'] = 'sheet_change'
                            else: diff_cell['status'] = 'other'
                            #print("{0:10} {1:20} {2:20} {3:20}".format(key, header, sheet_value, jira_value))
                            diff_cells.append(diff_cell)
            except Exception as error:
                Dev.pprint("Error in row {0}: {1}".format(row_index,row))
        return diff_cells

    def update_sheet_data_with_jira_data(self,sheet_data):
        for item in sheet_data:
            issue = self.get_issue_data(item.get('Key'))
            if issue:
                for column_id in set(item):
                    value = issue.get(column_id)
                    if value:
                        item[column_id] = value

    def get_jira_issues_in_sheet_data(self, sheet_data):
        keys = [row.get('Key') for row in sheet_data if row.get('Key') != '']
        #issues = self.jira().issues(keys)
        issues = self.jira_rest().issues(keys)
        return issues

    #@use_local_cache_if_available
    def get_issues_data(self,issues_id):
        return self.jira_rest().issues(issues_id)

    #@use_local_cache_if_available
    def get_issue_data(self,issue_id):
        return self.jira_rest().issue(issue_id)
        #return self.jira().issue(issue_id)

    def update_file_with_raw_data(self,raw_data,sheet_name):
        self.gsheets().set_values(self.file_id, sheet_name, raw_data)

    def load_data_from_jira(self):
        sheet_data = self.get_sheet_data(self.sheet_name())
        if sheet_data:
            try:
                self.update_sheet_data_with_jira_data(sheet_data)
                raw_data = self.convert_sheet_data_to_raw_data(sheet_data)
                self.update_file_with_raw_data(raw_data, self.sheet_name())             # add data to both
                self.update_file_with_raw_data(raw_data, self.sheet_name_backup())      # first one and the gsbot backup one (to be used to calculate update diffs)
                return "loaded data from jira completed...."
            except Exception as error:
                return "Error in load_data_from_jira: {0}".format(error)
        return "Error: no data for file_id: {0}".format(self.file_id)

    def sync_sheet(self):
        try:
            diff_cells = self.diff_cells()
            if diff_cells:
                self.sync_data_between_jira_and_sheet(diff_cells)
                return "sync data with Jira completed...."
            return "Error, could not calculate diff_cells (try reloading the data)"
        except Exception as error:
            return "Error in sync_sheet: {0}".format(error)

    def sync_data_between_jira_and_sheet(self,diff_cells):

        #fields_to_update = {}
        for item in diff_cells:
            status = item.get('status')
            if status == 'sheet_change':
                key   = item.get('key')
                field = item.get('field')
                value = item.get('sheet_value')
                #fields_to_update[key][field] = value
                message ='[Jira update] for jira issue `{0}` updating field `{1}` with value `{2}` '.format(key, field, value)
                print(message)
                result = self.jira_rest().issue_update_field(key, field, value)
                self.update_backup_data_with_new_jira_value(item)
                if result:
                    item['status'] = 'jira-save-ok'
                else:
                    item['status'] = 'jira-save-fail'
            if status == 'jira_change':
                key = item.get('key')
                field = item.get('field')
                value = item.get('sheet_value')
                Dev.pprint('need to update sheet, for jira issue `{0}` field `{1}` value `{2}` '.format(key, field, value))
        self.color_code_cells_based_on_diff_status(diff_cells)


    def update_backup_data_with_new_jira_value(self,item):
        sheet_id = self.sheet_id_backup()
        requests = [self.gsheets().request_cell_set_value(sheet_id,item.get('col_index'), item.get('row_index'),item.get('sheet_value'))]

        return self.gsheets().execute_requests(self.file_id,requests)

    #@use_local_cache_if_available
    #@save_result_to_local_cache
    def get_graph_nodes(self,graph_name):
        from gs_elk.Lambda_Graph import Lambda_Graph
        graph = Lambda_Graph().get_gs_graph___by_name(graph_name)
        if graph:
            return sorted(graph.nodes)
        return []

    def create_sheet_from_graph(self, graph_name):
        headers = ['Key', 'Jira Link', 'Summary', 'Status', 'Risk Rating', 'Issue Type']
        return self.create_sheet_from_graph_with_headers(graph_name, headers)

    def create_sheet_from_graph_with_headers(self,graph_name, headers=None):
        issues_ids = self.get_graph_nodes(graph_name)
        issues     = self.get_issues_data(issues_ids)

        if headers is None:
            headers    = ['Key']
            for key,values in issues.items():
                for header in values:
                    headers.append(header)
            headers = list(set(headers))
        values = [headers]
        for key,issue in issues.items():
            row = []
            for index in range(0,len(headers)):
                header = headers[index]
                if header == 'Jira Link':
                    value = '=HYPERLINK("https://jira.photobox.com/browse/{0}","{0}")'.format(key)
                else:
                    value = issue.get(header,'')
                row.append(value)

            values.append(row)

        sheet_name = self.sheet_name()
        self.gsheets().set_values(self.file_id,sheet_name,values)
        return self.gsheets().gdrive.file_weblink(self.file_id)
