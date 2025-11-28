from .Task import Task
from .TaskType import TaskType

class QrParser:
    def __init__(self, qr_string: str):
        self.qr_string = qr_string
    
    def create_task(self):
        """
        Parse QR string and create Task object.
        Expected format: ID:42;POS:1.0,2.0,0.0;PRIO:3;TYPE:pickup;TIMEOUT:60
        
        Returns:
            Task object if successful, None if parsing fails
        """
        try:
            # Split by semicolon to get fields
            fields = self.qr_string.split(';')
            
            # Create a dictionary to store parsed values (order-independent)
            data = {}
            for field in fields:
                key, value = field.split(':')
                data[key.upper()] = value
            
            # Validate required fields
            required_fields = ['ID', 'POS', 'PRIO', 'TYPE', 'TIMEOUT']
            for req_field in required_fields:
                if req_field not in data:
                    raise ValueError(f"Missing required field: {req_field}")
            
            # Parse ID
            task_id = int(data['ID'])
            
            # Parse position (convert "1.0,2.0,0.0" to tuple of floats)
            pos_values = data['POS'].split(',')
            if len(pos_values) != 3:
                raise ValueError(f"Position must have 3 values (x,y,theta), got {len(pos_values)}")
            target_pos = tuple(float(v) for v in pos_values)
            
            # Parse priority (validate range 1-5)
            priority = int(data['PRIO'])
            if not 1 <= priority <= 5:
                raise ValueError(f"Priority must be between 1-5, got {priority}")
            
            # Parse task type (convert to TaskType enum)
            task_type_str = data['TYPE'].lower()
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                raise ValueError(f"Invalid task type: {task_type_str}. Must be one of: {[t.value for t in TaskType]}")
            
            # Parse timeout
            max_time = int(data['TIMEOUT'])
            if max_time <= 0:
                raise ValueError(f"Timeout must be positive, got {max_time}")
            
            # Create and return Task
            return Task(
                ID=task_id,
                priority=priority,
                task_type=task_type,
                target_pos=target_pos,
                max_time=max_time
            )
            
        except ValueError as e:
            print(f"Error parsing QR code: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing QR code: {e}")
            return None
    
    @staticmethod
    def generate_qr_string(task_id, pos, priority, task_type, timeout):
        """
        Helper function to generate a valid QR string for testing.
        
        Args:
            task_id: int
            pos: tuple (x, y, theta)
            priority: int (1-5)
            task_type: TaskType enum
            timeout: int (seconds)
        
        Returns:
            Formatted QR string
        """
        pos_str = f"{pos[0]},{pos[1]},{pos[2]}"
        return f"ID:{task_id};POS:{pos_str};PRIO:{priority};TYPE:{task_type.value};TIMEOUT:{timeout}"
