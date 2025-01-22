# Use a base image
FROM debian:12

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y curl

RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash && echo 'source "$HOME/.rye/env"' >> ~/.bashrc

RUN echo 'export PATH="$HOME/.rye/shims:$PATH"' >> ~/.bashrc

# Set the working directory in the container
WORKDIR /root/demeter

# Copy the Python application files into the container
COPY . .

RUN mkdir -p log

# Install application dependencies
RUN . ~/.bashrc && rye sync

# Expose the port your Flask application is running on
EXPOSE 5000

# Define the command to run your Python server
CMD ["/root/.rye/shims/python", "app.py"]
