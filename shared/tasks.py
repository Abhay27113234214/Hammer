from celery import Celery
import time 

celery_app = Celery('hammer_tasks', broker='redis://127.0.0.1:6379/0')

@celery_app.task
def test_connection(name):
    print(f"\n[WORKER] Received a job from: {name}")
    print(f"[WORKER] Simulating heavy math calculation...")
    
    time.sleep(5)
    
    print(f"[WORKER] Job complete for {name}!\n")
    return "Success"

