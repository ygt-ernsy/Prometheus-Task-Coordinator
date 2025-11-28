#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .TaskQueue import TaskQueue
from .NavigationMock import NavigationMock
from .MQTTReporter import MQTTReporter
from .qr_parser import QrParser


class TaskCoordinator(Node):
    def __init__(self):
        super().__init__("task_coordinator")  # Fixed: super() with ()
        self.get_logger().info("Prometheus Task Coordinator Started")

        # Initialize components
        self.task_queue = TaskQueue()
        self.navigation = NavigationMock()
        self.reporter = MQTTReporter()  # Keep for PDF requirement

        # ROS2 Subscriber - listens for QR codes
        self.qr_subscription = self.create_subscription(
            String,
            "/qr_code_input",      # Added / prefix
            self.qr_callback,       # Added callback
            10
        )

        # ROS2 Publisher - publishes task status
        self.status_publisher = self.create_publisher(
            String,
            "/task_status",         # Added / prefix
            10
        )

        # ROS2 Timer - processes tasks every 1 second
        self.timer = self.create_timer(1.0, self.process_tasks_callback)

    def qr_callback(self, msg):
        """
        Callback when QR code message is received.
        msg is std_msgs.msg.String object, not a Python string!
        """
        qr_string = msg.data  # Extract actual string from message
        self.get_logger().info(f"Received QR code: {qr_string}")

        # Parse and add to queue
        task = QrParser(qr_string).create_task()
        if task:
            self.task_queue.enqueue(task)
            self.get_logger().info(f'Task {task.ID} added to queue (Priority: {task.priority})')
        else:
            self.get_logger().error('Failed to parse QR code')

    def process_tasks_callback(self):
        """
        Timer callback - processes next task every 1 second.
        Replaces the old run() method.
        """
        task = self.task_queue.get_next_task()
        
        if task is None:
            # No task to process
            return
        
        self.get_logger().info(f'Processing Task {task.ID}')
        
        # Report task started (both MQTT and ROS2)
        self.reporter.report_status(
            task.ID,
            task.taskType.value,
            task.task_status.value
        )
        self.publish_status(
            task.ID,
            task.taskType.value,
            task.task_status.value
        )
        
        # Check timeout
        if task.is_timed_out():
            self.task_queue.timeout_current_task()
            self.reporter.report_status(task.ID, task.taskType.value, "TIMEOUT")
            self.publish_status(task.ID, task.taskType.value, "TIMEOUT")
            self.get_logger().warn(f'Task {task.ID} timed out')
            return
        
        # Navigate to target position
        success = self.navigation.navigate_to(task.aim_coordinants)
        
        # Update task status based on result
        if success:
            self.task_queue.complete_current_task()  # Fixed typo
            self.reporter.report_status(task.ID, task.taskType.value, "COMPLETED")
            self.publish_status(task.ID, task.taskType.value, "COMPLETED")
            self.get_logger().info(f'Task {task.ID} completed successfully')
        else:
            self.task_queue.fail_current_task()
            self.reporter.report_status(task.ID, task.taskType.value, "FAILED")
            self.publish_status(task.ID, task.taskType.value, "FAILED")
            self.get_logger().error(f'Task {task.ID} failed')

    def publish_status(self, task_id, task_type, status):
        """
        Publish task status to ROS2 topic.
        """
        msg = String()
        msg.data = f"Task:{task_id}|Type:{task_type}|Status:{status}"
        self.status_publisher.publish(msg)
        self.get_logger().info(f'Published to ROS2: {msg.data}')

def main(args=None):
    """
    Main entry point for the TaskCoordinator node.
    """
    rclpy.init(args=args)
    
    try:
        coordinator_node = TaskCoordinator()
        
        # Log that the system is online
        coordinator_node.get_logger().info('Task Coordinator System Online. Waiting for QR Codes...')
        
        # Spin the node to process callbacks (QR input and Timer)
        rclpy.spin(coordinator_node)
        
    except KeyboardInterrupt:
        # Allow clean exit with Ctrl+C
        pass
    except Exception as e:
        print(f"Runtime Error: {e}")
    finally:
        # clean shutdown
        if 'coordinator_node' in locals():
            coordinator_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()