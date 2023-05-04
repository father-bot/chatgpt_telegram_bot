
#curl -X GET 'https://api.clickup.com/api/v2/team/3784312/space' \
#-H 'Authorization: XYZ' \
#-H 'Content-Type: application/json'


#curl -X GET 'https://api.clickup.com/api/v2/team' \
#-H 'Authorization: XYZ' \
#-H 'Content-Type: application/json'

import clickup_to_markdown
import vault_search
import vault

from bot import config

# Initialize ClickUp to Markdown export
api_key = config.clickup_api_key
workspace_id = "3784312"
space_id = '6710144'
repo_url = 'your_repository_url'
local_path = '../data/vault/1 - Projects/Machiavel (from ClickUp)'
branch_name = 'clickup'
output_directory = 'test_directory'

#vault_instance = vault.Vault(repo_url, local_path, branch_name)
#vault_instance.checkout_branch()

clickup_to_markdown.init(api_key, space_id, local_path)
clickup_to_markdown.export_markdown()

#commit_message = "Update markdown files from ClickUp"
#vault_instance.commit_and_push(commit_message)

# Search the vault
#query_str = "rBlox"
#search_results = vault_search.search_vault(query_str)

#print(search_results)
