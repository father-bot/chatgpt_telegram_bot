# clickup_to_markdown.py

import requests
import json
import os
import logging
from datetime import datetime

def init(api_key, space_id, output_directory):
    global headers
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    global space_id_global
    space_id_global = space_id

    global output_directory_global
    output_directory_global = output_directory

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_items(url, page):
    response = requests.get(f'{url}?page={page}&archived=false', headers=headers)
    if response.status_code != 200:
        logging.error(f"Error fetching items: status code {response.status_code}, response: {response.text}")
        return None
    return response.json()


def fetch_lists(space_id, page, folder_id=None):
    if folder_id:
        url = f'https://api.clickup.com/api/v2/folder/{folder_id}/list'
    else:
        url = f'https://api.clickup.com/api/v2/space/{space_id}/list'

    return fetch_items(url, page)

def fetch_tasks(list_id, page):
    return fetch_items(f'https://api.clickup.com/api/v2/list/{list_id}/task', page)

def fetch_subtasks(task_id, page):
    url = f'https://api.clickup.com/api/v2/task/{task_id}/subtask'
    response = requests.get(f'{url}?page={page}&archived=false', headers=headers)
    if response.status_code == 404:
        logging.error(f"Error fetching subtasks for task ID {task_id}: status code 404, response: {response.text}")
        return {'subtasks': []}
    elif response.status_code != 200:
        logging.error(f"Error fetching subtasks for task ID {task_id}: status code {response.status_code}, response: {response.text}")
        return None
    return response.json()

def fetch_folders(space_id, page):
    url = f'https://api.clickup.com/api/v2/space/{space_id}/folder'
    return fetch_items(url, page)

def process_tasks(tasks, md_file, indent='', folder_name='', list_name=''):
    for task in tasks:
        task_name = task['name']
        task_id = task['id']
        task_status = task['status']['status']
        task_description = task.get('text_content', '')
        task_completed = 'x' if task['status']['type'] == 'closed' else ' '
        task_creation_date = task['date_created']
        task_owner = task['creator']['username']

        # Convert the creation date to a human-readable format
        creation_date = datetime.fromtimestamp(int(task_creation_date) / 1000)
        human_readable_date = creation_date.strftime('%Y-%m-%d %H:%M:%S')

        folder_tag = folder_name.lower().replace(' ', '-')
        list_tag = list_name.lower().replace(' ', '-')
        
        md_file.write(f'{indent}- [{task_completed}] **{task_name}** (Task ID: {task_id})\n')
        md_file.write(f'{indent}  Status: {task_status}\n')
        md_file.write(f'{indent}  Created: {human_readable_date}\n')
        md_file.write(f'{indent}  Owner: {task_owner}\n')
        md_file.write(f'{indent}  Description:\n')
        md_file.write(f'{indent}  {task_description}\n\n')
        md_file.write(f'{indent}  Tags: #{folder_tag} #{list_tag}\n\n')

def export_markdown():
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory_global):
        os.makedirs(output_directory_global)

    # Fetch folders
    folders_data = fetch_folders(space_id_global, 0)
    folders = folders_data.get('folders', [])

    # Add a dummy "No Folder" item to include folderless lists
    folders.append({'id': None, 'name': 'No Folder'})

    for folder in folders:
        folder_id = folder['id']
        folder_name = folder['name']
        folder_path = os.path.join(output_directory_global, folder_name)

        # Create the folder directory if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Fetch lists for the current folder (or folderless lists if folder_id is None)
        lists_data = fetch_lists(space_id_global, 0, folder_id)
        lists = lists_data.get('lists', [])

        for lst in lists:
            list_id = lst['id']
            list_name = lst['name']
            md_file_path = os.path.join(folder_path, f'{list_name}.md')
            logging.info(f'Processing list: {list_name}')

            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                # Add folder and list titles to the markdown file
                md_file.write(f'# {folder_name}\n\n')
                md_file.write(f'## {list_name}\n\n')

                # Process tasks for the current list
                task_page = 0
                while True:
                    tasks_data = fetch_tasks(list_id, task_page)
                    if not tasks_data['tasks']:
                        break

                    process_tasks(tasks_data['tasks'], md_file, folder_name=folder_name, list_name=list_name)

                    task_page += 1
