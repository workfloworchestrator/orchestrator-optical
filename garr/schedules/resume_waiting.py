from orchestrator.schedules.scheduling import scheduler
from orchestrator.services.processes import start_process


@scheduler(name="Resume workflows - GARR core", time_unit="minutes", period=6)
def our_run_resume_workflows() -> None:
    start_process("task_resume_workflows")
