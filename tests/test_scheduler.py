from backend.scheduler import create_scheduler

def test_create_scheduler():
    scheduler = create_scheduler(interval_hours=6)
    assert scheduler is not None
    jobs = scheduler.get_jobs()
    assert len(jobs) == 3
