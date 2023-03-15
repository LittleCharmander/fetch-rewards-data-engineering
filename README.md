### How to use

This project creates a main service inside the docker-compose.yaml, which will fetch a message from AWS SMS using boto3, mask PII of the message, and save the log-in information to SQL database using SQLAlchemy. 

To run the code, first run the docker-compose by typing `docker-compose -f docker-compose.yaml up`.
Here I use `CMD ["sleep", "infinity"]` in the Dockerfile, so we will need to open the interactive terminal of the main service to run `python main.py`. Then the code should be able to perform the task and we could check the database using the terminal by running the following

`apt-get update`
`apt-get -y install postgresql`
`psql -d postgres -U postgres -p 5432 -h localhost -W`
`postgres=# select * from user_logins;`

### Questions

1. How would you deploy this application in production? 
To deploy this application in production, run the container produced by Dockerfile would suffice, and remember to change the entrypoint to main.py. Modify the url to AWS SMS service and PostgreSQL database accordingly. 

2. What other components would you want to add to make this production ready? 
This project is a prototype to show the main steps only. To make it into production code, we need to address several issues. First of all, we want to handle all the messages in the queue. This can be done by adding additional logic (for example loop) outside the main.py. Depending on the amount of messages, we might want to scale the project by potentially using kubernetes. Secondly, we want to safely save the secret_key we used for encryption. Lastly, we would want to set primary key in the postgres table to make it faster. 
Also, it is a good practice to add unit test and logging into the code, which are currently missing. 

3. How can this application scale with a growing dataset. 
Like I mentioned above, consider kubernetes for fast processing of data, and setting up primary key in postgres for faster consuming of data. 

4. How can PII be recovered later on? 
I wrote a decryption function. Although I haven't tested it yet, but the algorithm I used should be able to reverse the encryption process. 

5. What are the assumptions you made? 
In this prototype, I assume this is at least one message in the queue, and the user_logins table already exists. 


### Notes to myself

Useful commands:
docker-compose -f docker-compose.yaml up
docker exec -it [container ID] /bin/bash
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
apt-get update
apt-get -y install postgresql
psql -d postgres -U postgres -p 5432 -h localhost -W
postgres
postgres=# select * from user_logins;

Example message:
{'MessageId': '4e1146b6-21d0-45f3-85d6-33b985133aaf', 'ReceiptHandle': 'ZTUxYTA3NGMtYjM3Zi00Y2RhLThlOGEtMDgwZmM0YzEzNmRmIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6bG9naW4tcXVldWUgNGUxMTQ2YjYtMjFkMC00NWYzLTg1ZDYtMzNiOTg1MTMzYWFmIDE2Nzg4NjE3MjUuMDk1MzIyMQ==', 'MD5OfBody': 'e4f1de8c099c0acd7cb05ba9e790ac02', 'Body': '{"user_id": "424cdd21-063a-43a7-b91b-7ca1a833afae", "app_version": "2.3.0", "device_type": "android", "ip": "199.172.111.135", "locale": "RU", "device_id": "593-47-5928"}', 'Attributes': {'SentTimestamp': '1678861336'}}
