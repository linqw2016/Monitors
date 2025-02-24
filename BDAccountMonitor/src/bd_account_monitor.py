import asyncio
import os
import json
from xportal.utils import fetch_post
from typing import List

client_region = "norwayeast"
time_to_probe_in_seconds = 360

account_list = {
    "eastus": [
        "toszrseus001",
        "toszrseus002",
        "toszrseus003",
        "toszrseus004",
        "toszrseus005",
        "toszrseus006",
        "toszrseus007",
        "toszrseus008",
        "toszrseus009",
        "toszrseus010",
        "toszrseus011",
        "toszrseus012",
        "toszrseus013",
        "toszrseus014",
        "toszrseus015",
        "toszrseus016",
        "toszrseus017",
        "toszrseus018",
        "toszrseus019",
        "toszrseus020",
    ],
    "eastus2": [
        "toszrseus2001",
        "toszrseus2002",
        "toszrseus2003",
        "toszrseus2004",
        "toszrseus2005",
        "toszrseus2006",
        "toszrseus2007",
        "toszrseus2008",
        "toszrseus2009",
        "toszrseus2010",
        "toszrseus2011",
        "toszrseus2012",
        "toszrseus2013",
        "toszrseus2014",
        "toszrseus2015",
        "toszrseus2016",
        "toszrseus2017",
        "toszrseus2018",
        "toszrseus2019",
        "toszrseus2020",
        "tosazureus001",
        "tosazureus002",
        "tosazureus003",
        "tosazureus004",
        "tosazureus005",
        "tosazureus006",
        "tosazureus007",
        "tosazureus008",
        "tosazureus009",
        "tosazureus010",
        "tosazureus011",
        "tosazureus012",
    ],
    "norwayeast": [
        "toszrsno001",
        "toszrsno002",
        "toszrsno003",
        "toszrsno004",
        "toszrsno005",
        "toszrsno006",
        "toszrsno007",
        "toszrsno008",
        "toszrsno009",
        "toszrsno010",
        "toszrsno011",
        "toszrsno012",
        "toszrsno013",
        "toszrsno014",
        "toszrsno015",
        "toszrsno016",
        "toszrsno017",
        "toszrsno018",
        "toszrsno019",
        "toszrsno020",
    ],
    "southeastasia": [
        "toszrssg01",
        "toszrssg02",
        "toszrssg03",
        "toszrssg04",
        "toszrssg05",
        "toszrssg06",
        "toszrssg07",
        "toszrssg08",
        "toszrssg09",
        "toszrssg10",
        "toszrssg11",
        "toszrssg12",
        "toszrssg13",
        "toszrssg14",
        "toszrssg15",
        "toszrssg16",
        "toszrssg17",
        "toszrssg18",
        "toszrssg19",
        "toszrssg20",
        "tosazuresg001",
        "tosazuresg002",
        "tosazuresg003",
        "tosazuresg004",
        "tosazuresg005",
        "tosazuresg006",
        "tosazuresg007",
        "tosazuresg008",
        "tosazuresg009",
        "tosazuresg010",
        "tosazuresg011",
        "tosazuresg012",
        "tosazuresg013",
        "tosazuresg014",
        "tosazuresg015",
        "tosazuresg016",
        "tosazuresg017",
        "tosazuresg018",
        "tosazuresg019",
        "tosazuresg020",
    ],
    "northeurope": [
        "toszrsie001",
        "toszrsie002",
        "toszrsie003",
        "toszrsie004",
        "toszrsie005",
        "toszrsie006",
        "toszrsie007",
        "toszrsie008",
        "toszrsie009",
        "toszrsie010",
        "toszrsie011",
        "toszrsie012",
        "toszrsie013",
        "toszrsie014",
        "toszrsie015",
        "toszrsie016",
        "toszrsie017",
        "toszrsie018",
        "toszrsie019",
        "toszrsie020",
    ]
}

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