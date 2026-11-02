FROM tabulario/spark-iceberg:latest

USER root

# Install Jupyter Lab and prettytable
RUN pip3 install --no-cache-dir jupyterlab prettytable

WORKDIR /home/iceberg/notebooks

# Copy entrypoint script and set permissions
COPY entrypoint.sh /home/iceberg/notebooks/spark/entrypoint.sh
RUN chmod +x /home/iceberg/notebooks/spark/entrypoint.sh

# Run as root or let the base image handle its default user context safely
USER root

ENTRYPOINT ["/home/iceberg/notebooks/spark/entrypoint.sh"]