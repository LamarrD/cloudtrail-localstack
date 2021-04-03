# cloudtrail-localstack
Demo repo to show cloudtrail data events in localstack.  

The behavior i desire is that after starting localstack and creating a cloudtrail+cloudtrail logging
bucket, and performing actions that should generate cloudtrail events that i'd see the cloudtrail 
logs in the logging bucket.

Currently the behavior i'm noticing is the cloudtrail and bucket is being successfully created, but 
the log files never show up in the logging bucket. I believe the issue is related to the fact that
these are Data Events rather than management events (i believe i've seen management events in
cloudtrail localstack)

## Steps to reproduce desired behavior in AWS
After setting up credentials, region, etc 
```python3 main.py```
## Steps to reproduce undesired behavior in localstack
### Start localstack pro
```export LOCALSTACK_API_KEY=KEY```
```DNS_ADDRESS=127.0.0.1 localstack start```

### Run Script
```python3 main.py```

