-----

# Prometheus Autonomous Logistics Rover - Task Coordinator

## 📖 Project Overview

This repository contains the **Task Coordinator Module** for the Prometheus Autonomous Logistics Rover. It is a ROS 2 (Humble) based system designed to parse logistics instructions from QR codes, manage a prioritized task queue, and coordinate navigation and status reporting.

The system is fully containerized using Docker, ensuring a consistent development and execution environment without requiring a native ROS 2 installation on the host machine.

## 🚀 Key Features

  * **Priority Task Queue:** Implements a custom scheduling algorithm that processes tasks based on priority (1-5, with 5 being highest) and handles priority inversion for incoming high-priority tasks.
  * **QR Code Parsing:** Robust parsing engine that decodes structured task strings (ID, Position, Priority, Type, Timeout) and handles malformed data gracefully.
  * **Mock Navigation:** Simulates the time-domain behavior of a rover moving between coordinates $(x, y, \theta)$.
  * **MQTT Status Reporting:** Simulates the publication of task states (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `TIMEOUT`) to an MQTT topic.
  * **ROS 2 Integration:** Operates as a standard ROS 2 Node (`task_coordinator`) with subscriptions and timers.
  * **Dockerized Environment:** Includes a "Bonus" development environment configuration for rapid deployment.

## 🛠️ Prerequisites

  * **Docker**
  * **Docker Compose**
  * **Make** (Optional, but recommended for using the included shortcuts)

## 📂 Project Structure

```text
.
├── Makefile                   # Shortcut commands for build, test, and run
├── Dockerfile                 # ROS 2 Humble image definition
├── docker-compose.yml         # Service orchestration
├── entrypoint.sh              # ROS 2 environment setup
├── test_scenarios.py          # Integration simulation script
├── test_suite.py              # Unit tests
└── prometheus_task/           # Main Python Package
    ├── __init__.py
    ├── TaskCoordinator.py     # Main ROS 2 Node
    ├── TaskQueue.py           # Priority Queue Logic
    ├── Task.py                # Data Class
    ├── NavigationMock.py      # Navigation Simulation
    ├── MQTTReporter.py        # Status Reporting
    └── QrParser.py            # String Parsing Logic
```

## ⚡ Quick Start

The project includes a `Makefile` to simplify Docker commands.

### 1\. Build the System

Build the ROS 2 Docker image containing all dependencies.

```bash
make build
```

### 2\. Run the Simulation

This command starts the container and immediately executes the system integration test. You will see the Task Coordinator start, receive simulated QR codes, reorder them by priority, and execute them.

```bash
make run
```

*Note: This runs in interactive mode. You can stop it with `Ctrl+C`.*

### 3\. Run Unit Tests

To verify individual components (Queue sorting logic, Parsing validation, etc.), run the test suite:

```bash
make test
```

## 🏗️ Design Decisions

### Priority Queue Logic

The `TaskQueue` is implemented to ensure critical logistics tasks take precedence. When a new task with Priority 5 arrives, it is placed ahead of pending Priority 1-4 tasks. The sorting logic uses `reverse=True` to handle the priority integer comparison correctly (Higher number = Higher Priority).

### Navigation Simulation

To avoid dependencies on a full physics engine (like Gazebo) for this logic test, a `NavigationMock` class is used. It accepts target coordinates and simulates a successful traversal, returning control to the coordinator upon arrival.

### MQTT Reporting

The `MQTTReporter` is designed to be modular. While currently simulating output to `stdout`, it can be easily swapped for a `paho-mqtt` client implementation to connect to a real broker (e.g., Mosquitto) without changing the core coordinator logic.

## 🔧 Make Commands Reference

| Command | Description |
| :--- | :--- |
| `make build` | Build the Docker image. |
| `make run` | Build the image and run the integration simulation (`test_scenarios.py`). |
| `make test` | Run the unit test suite (`test_suite.py`) using `pytest`. |
| `make shell` | Open an interactive Bash shell inside the container for debugging. |
| `make clean` | Stop containers and remove docker volumes. |

-----

