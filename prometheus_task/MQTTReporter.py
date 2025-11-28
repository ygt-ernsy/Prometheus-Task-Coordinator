class MQTTReporter:
    def __init__(self):
        self.topic = "prometheus/task_status"
    
    def report_status(self, task_id, task_type, status):
        message = f"Task:{task_id}|Type:{task_type}|Status:{status}"
        
        print(f"MQTT Publish [{self.topic}]: {message}")
