#!/usr/bin/env python3
import time
from prometheus_task.TaskQueue import TaskQueue
from prometheus_task.NavigationMock import NavigationMock
from prometheus_task.MQTTReporter import MQTTReporter
from prometheus_task.qr_parser import QrParser

def run_simulation():
    print("================================================================")
    print("   PROMETHEUS AUTONOMOUS LOGISTICS ROVER - SIMULATION START")
    print("================================================================\n")

    # 1. Initialize Components
    # [cite: 3] Developing a Task Coordinator module
    queue = TaskQueue()
    nav = NavigationMock()
    reporter = MQTTReporter()
    
    print("[SYSTEM] Modules Initialized: Queue, Navigation, MQTT Reporter.\n")

    # 2. Simulate Incoming QR Codes (The Scenario)
    # We simulate a burst of incoming requests from the camera
    # [cite: 24] String format example
    incoming_qr_codes = [
        # Normal Priority Delivery
        "ID:101;POS:10.5,20.0,0.0;PRIO:3;TYPE:delivery;TIMEOUT:60", 
        
        # Low Priority Scan
        "ID:102;POS:5.0,5.0,1.5;PRIO:1;TYPE:scan;TIMEOUT:120", 
        
        # High Priority Pickup (Should jump to front of queue)
        # [cite: 13] Priority 1-5
        "ID:999;POS:0.0,0.0,0.0;PRIO:5;TYPE:pickup;TIMEOUT:45",
        
        # Malformed QR Code (Test Error Handling)
        #  Hatalı formatlarda uygun hata mesajı
        "ID:ERROR;POS:INVALID;PRIO:99",
        
        # Timeout Scenario Task (Very short timeout)
        # [cite: 15] Timeout: Görevin tamamlanması için maksimum süre
        "ID:404;POS:30.0,30.0,0.0;PRIO:4;TYPE:wait;TIMEOUT:1" 
    ]

    print("--- PHASE 1: RECEIVING & PARSING TASKS ---")
    for qr_string in incoming_qr_codes:
        print(f"Cam Input: '{qr_string}'")
        parser = QrParser(qr_string)
        task = parser.create_task()
        
        if task:
            queue.enqueue(task)
            print(f" -> [SUCCESS] Task {task.ID} Enqueued (Priority: {task.priority})")
        else:
            print(" -> [ERROR] Parse Failed. Dropping string.")
        time.sleep(0.2) # Simulate processing delay

    print("\n--- PHASE 2: PROCESSING QUEUE (PRIORITY CHECK) ---")
    #  Önceliğe göre sıralama
    print("Verifying Order (Expected: 999 -> 404 -> 101 -> 102)")
    
    # We process tasks until the queue is empty
    while True:
        # Get next task
        current_task = queue.get_next_task()
        
        # [cite: 21] Aynı anda yalnızca bir görevin çalıştırılabilmesi
        if current_task is None:
            print("[SYSTEM] Queue empty. Simulation complete.")
            break

        print(f"\n>>> PROCESSING TASK ID: {current_task.ID} (Type: {current_task.taskType.value})")
        
        # Report Start via MQTT 
        reporter.report_status(current_task.ID, current_task.taskType.value, "IN_PROGRESS")

        # Simulate Timeout Logic for Task 404
        if current_task.ID == 404:
            print("[SIMULATION] Forcing delay to trigger timeout...")
            time.sleep(1.5) # Wait longer than the 1s timeout defined in QR
            
            if current_task.is_timed_out():
                queue.timeout_current_task()
                reporter.report_status(current_task.ID, current_task.taskType.value, "TIMEOUT")
                print(f"[RESULT] Task {current_task.ID} Timed Out as expected.")
                continue # Skip navigation

        # Navigation 
        success = nav.navigate_to(current_task.aim_coordinants)

        # Finalize Task
        if success:
            # Note: Ensure method name matches your class (complete_current_task vs complate_current_task)
            queue.complete_current_task()
            reporter.report_status(current_task.ID, current_task.taskType.value, "COMPLETED")
            print(f"[RESULT] Task {current_task.ID} Finished Successfully.")
        else:
            queue.fail_current_task()
            reporter.report_status(current_task.ID, current_task.taskType.value, "FAILED")

        time.sleep(0.5) # Pause between tasks

    print("\n================================================================")
    print("   SIMULATION END")
    print("================================================================")

if __name__ == "__main__":
    run_simulation()
