FROM python:3.12

# Set work directory
WORKDIR /app

# Install necessary tools
RUN apt-get update && apt-get install -y \
    g++ \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies from Pipfile.lock
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the Django project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["pipenv", "run", "gunicorn", "fountainhead.wsgi:application", "--bind", "0.0.0.0:8000"]