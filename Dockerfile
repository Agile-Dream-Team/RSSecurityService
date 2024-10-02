# Use an official Python runtime as a base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /code

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container at /code
COPY . /code/

# Set environment variables
ENV WEBHOOK_PORT=8000
ENV WEBHOOK_HOST=0.0.0.0
ENV ENVIRONMENT=prod

# Command to run the application
CMD ["sh", "-c", "uvicorn main:app --host $WEBHOOK_HOST --port $WEBHOOK_PORT $(if [ \"$ENVIRONMENT\" = \"dev\" ]; then echo '--reload'; fi)"]