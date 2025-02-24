import asyncio
import os
import json
from xportal.utils import fetch_post
from typing import List

# Load the configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

client_region = config['client_region']
time_to_probe_in_seconds = config['time_to_probe_in_seconds']
account_list = config['account_list']

accounts = account_list[client_region]

async def submit_template_job2(template_path: str, parameters: dict=None, outputs: List[str]=None, environment: str=None, destination: str=None) -> str: 
    if environment is None:
        if 'CLOUD_SERVICE_NAME' in os.environ:
            environment = os.environ['CLOUD_SERVICE_NAME']
        else:
            environment = 'Production'

    if template_path.startswith('https://aka.ms/xjpl?templatePath='):
        template_path = template_path.replace("https://aka.ms/xjpl?templatePath=", "")
    if not template_path.startswith('/'):
        template_path = '/' + template_path

    sys_priority = os.getenv("PRIORITY", default="normal")
    copy_of_parameters = parameters.copy() if parameters else None
    if copy_of_parameters:
        if copy_of_parameters.get('PRIORITY', None) is None:
            copy_of_parameters['PRIORITY'] = sys_priority
    else:
        copy_of_parameters = {'PRIORITY': sys_priority}

    body = {
        'ProjectName': 'Production',
        'Severity': 'Sev2',
        'Parameters': {
            'InputParametersJson': json.dumps(copy_of_parameters, default=str) if copy_of_parameters else '',
            'Script': template_path,
            'OutputObjectsList': json.dumps(outputs, default=str) if outputs else '',
            "Environment": environment,
            "Destination": destination
        }
    }
    response = await fetch_post('/api/v1/AAIncidentData/RunScriptIncidentData', json.dumps(body, default=str))
    return response['IncidentDiagnosticItemId']

async def submit_job(a, semaphore):
    async with semaphore:
        parameters = {
            "account": a,
            "time_to_probe_in_seconds": time_to_probe_in_seconds,
        }
        job_id = await with_retry(submit_template_job2, template, parameters, environment="Dedicated", destination=client_region)
        print(job_id)
        return job_id