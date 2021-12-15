import asyncio
import random
import time
from typing import Optional
from concurrent.futures.process import ProcessPoolExecutor
from typing import Dict
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi import status, HTTPException
from pydantic import BaseModel, Field

from .models import Job, JobStatus


jobs: Dict[UUID, Job] = {}
app = FastAPI()

def get_job(job_id: UUID) -> Optional[Job]:
    try:
        res = jobs[job_id]
    except KeyError:
        return None

    return res


def cpu_bound_func(x: int):
    time.sleep(random.randrange(5, 15))
    return x ** 2


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        app.state.executor, fn, *args
    )


async def start_cpu_bound_task(uid: UUID, param: int) -> None:
    jobs[uid].result = await run_in_process(cpu_bound_func, param)
    jobs[uid].status = "complete"


@app.post("/hook")
async def print_hook(request: Request, status_code=status.HTTP_200_OK):
    print(await request.json())


@app.post("/new_cpu_bound_task/{param}", status_code=status.HTTP_202_ACCEPTED)
async def task_handler(param: int, background_tasks: BackgroundTasks):
    new_task = Job()
    jobs[new_task.uid] = new_task
    background_tasks.add_task(start_cpu_bound_task, new_task.uid, param)
    return new_task


@app.get("/status/{uid}")
async def status_handler(uid: UUID):
    return jobs[uid]




@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor(10)


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()
