import datetime
import logging
from typing import Dict, List, NamedTuple

from telegram.ext.jobqueue import Days, JobQueue

import db
import time_
from currencies import Currencies
from BotExceptions import JobException
from db import UpdateValue


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TIME_FORMAT = '%H:%M:%S'


class Id(NamedTuple):
    chat: int
    user: int
    
class Job(NamedTuple):
    currency_index: str
    time: str
    days: str
    id: Id

def _load_jobs() -> List[Dict]:
    result = db.fetchall(
        'job', 'currency_index_id chat_id execute_time days'.split(),
        f'WHERE `status` = "active"'
    )
    return result

def init(queue: JobQueue, callback: callable):
    '''Pre-inittalize installed jobs from DB.'''
    jobs = _load_jobs()
    for job in jobs:
        time = time_.get_msk(job['execute_time'])
        job_name = get_job_name( job['currency_index_id'] )
        days = eval(','.join(job['days']))
        queue.run_daily(callback, 
                        time=time, 
                        days=days, 
                        context=job['chat_id'], 
                        name=job_name)

def add_job(job: Job) -> None:
    '''Insert or update job to db.'''
    dict_values = {
        'currency_index_id': job.currency_index,
        'user_id': job.id.user,
        'chat_id': job.id.chat,
        'execute_time': job.time,
        'days': job.days
    }
    print(dict_values)
    constraint = 'currency_index_id chat_id'.split()
    db.insert('job', dict_values, constraint)

def disable_job(queue: JobQueue, chat_id: int, currency_index: str=None) -> None:
    ''' Disable an existing "active" jobs and set "disable" to db rows
        by currency index and chat id. '''
    jobs = queue.get_jobs_by_name( get_job_name(currency_index) )
    _remove_jobs(queue, jobs)

    where_clause = f'WHERE `chat_id` = {chat_id} '\
                    'AND `status` = "active" '
    if currency_index: 
        where_clause += f'AND `currency_index_id` = "{currency_index}"'
    db.update(
        'job', UpdateValue(column='status',value='disable'),
        where_clause
    )

def _remove_jobs(queue: JobQueue, _jobs: tuple=None) -> None:
    '''Remove from job queue. 
       If jobs tuple is None then remove all jobs from job queue.'''
    jobs = queue.jobs() if not _jobs else _jobs
    for job in jobs:
        job.schedule_removal()


def get_job_queue_by_chat(id: int) -> List[Job]:
    '''Return active jobs data from db'''
    job_queue = db.fetchall(
        'job', 'currency_index_id chat_id user_id execute_time days'.split(),
        f'WHERE chat_id = {id} AND status = "active"'
    )
    result = []
    for job in job_queue:
        result.append(
            Job(currency_index=job['currency_index_id'],
                time=job['execute_time'],
                days=job['days'],
                id=Id( chat=job['chat_id'], user=['user_id'] ))
        )
    return result

def get_job_name(currency_index: str) -> str:
    '''Return formulaic job name containing currency index.'''
    return f'job_{currency_index}'

def get_currency_index(job_name: str) -> str:
    return job_name[4:]
