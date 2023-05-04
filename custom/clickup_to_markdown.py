# clickup_to_markdown.py

import requests
import json
import os
import logging

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


def fetch_lists(space_id, page):
    return fetch_items(f'https://api.clickup.com/api/v2/space/{space_id}/list', page)

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

def process_tasks(tasks, md_file, indent=''):
    for task in tasks:
        task_name = task['name']
        task_id = task['id']
        task_status = task['status']['status']
        task_description = task.get('text_content', '')
        task_metadata = json.dumps(task, indent=2)
        task_completed = 'x' if task['status']['type'] == 'closed' else ' '

        md_file.write(f'{indent}- [{task_completed}] **{task_name}** (Task ID: {task_id})\n')
        md_file.write(f'{indent}  ## Status: {task_status}\n')
        md_file.write(f'{indent}  ### Description:\n')
        md_file.write(f'{indent}  {task_description}\n')
        md_file.write(f'{indent}  ### Metadata:\n```\n{task_metadata}\n```\n\n')

        # # Process subtasks
        # subtask_page = 0
        # while True:
        #     subtasks_data = fetch_subtasks(task_id, subtask_page)

        #     if subtasks_data is None or not subtasks_data['subtasks']:
        #         break

        #     md_file.write(f'{indent}  ### Subtasks:\n')
        #     process_tasks(subtasks_data['subtasks'], md_file, indent='    ')

        #     subtask_page += 1


def export_markdown():
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory_global):
        os.makedirs(output_directory_global)

    # Iterate through lists with pagination and create a markdown file for each list
    list_page = 0
    while True:
        lists_data = fetch_lists(space_id_global, list_page)

        # Check if 'lists' key is not in lists_data or if it's empty
        if 'lists' not in lists_data or not lists_data['lists']:
            break

        for lst in lists_data['lists']:
            list_id = lst['id']
            list_name = lst['name']
            folder_name = lst['folder']['name'] if lst['folder'] else 'No Folder'
            folder_path = os.path.join(output_directory_global, folder_name)

            # Create the folder directory if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            md_file_path = os.path.join(folder_path, f'{list_name}.md')
            logging.info(f'Processing list: {list_name}')

            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                # Process tasks for the current list
                task_page = 0
                while True:
                    tasks_data = fetch_tasks(list_id, task_page)
                    if not tasks_data['tasks']:
                        break

                    process_tasks(tasks_data['tasks'], md_file)

                    task_page += 1

            # Increment the list_page variable to fetch the next page of lists
            list_page += 1
