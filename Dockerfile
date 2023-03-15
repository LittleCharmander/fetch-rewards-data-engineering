FROM python:3.9

#set up environment
RUN pip3 install --upgrade pip

# set the working directory in the container
WORKDIR /code

# copy the content of the local src directory to the working directory
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["sleep", "infinity"]  # for debugging purpose
# CMD ["python", "main.py"]