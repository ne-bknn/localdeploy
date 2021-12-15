import asyncio
import random
import time
from typing import Optional
from concurrent.futures.process import ProcessPoolExecutor
from typing import Dict
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi import status, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from .models import Job, JobStatus
from ..deployment import redeploy


jobs: Dict[UUID, Job] = {}
app = FastAPI()


def get_job(job_id: UUID) -> Optional[Job]:
    try:
        res = jobs[job_id]
    except KeyError:
        return None

    return res


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)


async def deploy_wrapper(job: Job) -> None:
    jobs[job.uid].result = await run_in_process(redeploy, job)

@app.post("/hook")
async def webhook(request: Request, status_code=status.HTTP_202_ACCEPTED, background_tasks: BackgroundTasks):
    data = await request.json()
    if "workflow_run" not in data.keys():
        raise RequestValidationError

    workflow_state = data["workflow_run"]

    if (
        workflow_state["status"] == "completed"
        and workflow_state["conclustion"] == "success"
    ):
        deploy_name = data["respository"]["name"]
        new_deploy = Job()
        new_deploy.deploy_name = deploy_name
        jobs[new_deploy.uid] = new_deploy
        background_tasks.add_task(deploy_wrapper, new_deploy)
        return new_deploy


@app.get("/job/{uid}")
async def get_job(uid: UUID) -> Job:
    return jobs[uid]

@app.get("/job/")
async def list_jobs(uid: UUID) -> List[Job]:
    return jobs


@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor(10)


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()
