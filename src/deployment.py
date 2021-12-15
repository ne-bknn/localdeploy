import subprocess
from pathlib import Path

from app import Job, JobStatus
from app import settings

def git_pull(dir: Path):
    out = subprocess.Popen(["git", "-C", str(dir), "pull"])
    exit_code = out.wait()
    if exit_code != 0:
        raise ValueError

def docker_compose_up(dir: Path):
    out = subprocess.Popen(["docker-compose", "up", "-d", "--build", "--no-deps", "-f", dir / "docker-compose.yml"])
    exit_code = out.wait()
    if exit_code != 0:
        raise ValueError

def redeploy(job: Job):
    name = job.deploy_name
    base_dir = settings.base_dir
    cwd = Path(base_dir) / name
    try:
        git_pull(cwd)
        job.status = JobStatus.deploying
    except ValueError:
        job.status = JobStatus.failed_syncing
        return

    try:
        docker_compose_up(cwd)
        # todo: add healthcheck
        job.status = JobStatus.done
    except ValueError:
        job.status = JobStatus.failed_deploying
        return

