FROM python:3.12.4-slim

# Set the working directory
WORKDIR /petshopapi

# Copy the requirements file
COPY ./petshopapi/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./petshopapi ./petshopapi

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "petshopapi.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]