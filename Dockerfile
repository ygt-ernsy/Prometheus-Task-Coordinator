FROM ros:humble-ros-core

LABEL maintainer="Prometheus Software" \
      description="ROS2 Humble Task Management System" \
      version="1.0"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    ROS_DISTRO=humble \
    PYTHONPATH=/app:$PYTHONPATH

# Install dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    ros-humble-rclpy \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files
COPY prometheus_task ./prometheus_task
COPY test_scenarios.py .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir paho-mqtt pydantic

# Setup entrypoint script
RUN echo '#!/bin/bash\nset -e\nsource /opt/ros/$ROS_DISTRO/setup.bash\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Auto-source ROS setup for every new shell
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
