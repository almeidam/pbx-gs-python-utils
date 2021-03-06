from api_jira.API_Jira_Rest import API_Jira_Rest
from api_jira.API_Jira      import API_Jira
from api_jira.API_Jira_Sheets_Sync import API_Jira_Sheets_Sync
from gs.API_Issues          import API_Issues
from gsuite.GSheets         import GSheets
from utils.Dev              import Dev
from utils.Elastic_Search import Elastic_Search
#from utils.Local_Cache import use_local_cache_if_available, save_result_to_local_cache
from utils.Misc import Misc


class API_Jira_Sheets_Create(API_Jira_Sheets_Sync):
    def __init__(self, file_id):
        super().__init__(file_id)

    def sheet_data(self):
        sheet_name = self.sheet_name()
        return self.get_sheet_data(sheet_name)

    def calculate_jira_actions(self,sheet_data):
        jira_actions = []
        for row in sheet_data:
            index = row.get('index')
            if   row.get('Key'                       ) != 'new' : status = 'skip_issue - Key value was not new'
            elif Misc.none_or_empty(row, 'Summary'   )          : status = 'skip_issue - Summary value was empty'
            elif Misc.none_or_empty(row, 'Project'   )          : status = 'skip_issue - Project value was empty'
            elif Misc.none_or_empty(row, 'Issue Type')          : status = 'skip_issue - Issue Type value was empty'
            else:
                status = 'create_issue'

            jira_actions.append({'index':index , 'status': status, 'row': row})
        return jira_actions

    def execute_jira_actions(self, jira_actions):
        for jira_action in jira_actions:
            status = jira_action.get('status')
            if status == 'create_issue':
                row        = jira_action.get('row')
                project    = row.get('Project')
                issue_type = row.get('Issue Type')
                summary    = row.get('Summary')
                description = 'Issue created by GSBot'

                try:
                    result = self.jira().issue_create(project,summary, description,issue_type)
                    jira_action['status'  ] = 'issue_created'
                    jira_action['Jira_Key'] =  result.key
                except Exception as error:
                    jira_action['status'] = "Error: {0}".format(error)

    def update_sheet_with_status(self,jira_actions):
        requests      = []
        sheet_id      = self.sheet_id()
        status_col    = Misc.array_find(self.headers, 'Status')
        key_col       = Misc.array_find(self.headers, 'Key'   )
        jira_link_col = Misc.array_find(self.headers, 'Jira Link')
        if status_col:
            for jira_action in jira_actions:
                row_index = jira_action.get('index') + 1
                status    = jira_action.get('status')

                if status   == 'create_issue' : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, status_col, row_index, 1.0, 1.0, 0.5))
                elif status == 'issue_created': requests.append(self.gsheets().request_cell_set_background_color(sheet_id, status_col, row_index, 0.5, 1.0, 0.5))
                else                          : requests.append(self.gsheets().request_cell_set_background_color(sheet_id, status_col, row_index, 1.0, 0.5, 0.5))

                requests.append(self.gsheets().request_cell_set_value(sheet_id, status_col, row_index, status       ))

                if status == 'issue_created':
                    jira_key  = jira_action.get('Jira_Key')
                    jira_link = '=HYPERLINK("https://jira.photobox.com/browse/{0}","{0}")'.format(jira_key)
                    requests.append(self.gsheets().request_cell_set_value(sheet_id, key_col      , row_index, jira_key ))
                    requests.append(self.gsheets().request_cell_set_value(sheet_id, jira_link_col, row_index, jira_link))



        return self.gsheets().execute_requests(self.file_id, requests)