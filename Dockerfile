# Use the official Python image from the Docker Hub
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
# Also install krb5-user to resolve the gssapi dependency issue
RUN apt-get update && apt-get install -y krb5-user
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "streamlit_app.py"]
