# **EC2 Scheduler**
## Save money by scheduling your ec2 instances

ec2-scheduler is a service powered by AWS Lambda. Setup up a tag `AutoStartSchedule` and `AutoStopSchedule` with cron values. This gives a flexibility for configuring start and stop times for EC2 Instances as per need.

The lambda runs every 30 mins and validate every instance tag values with specified time zone datetime. 
 
This lambda has optional POST api support to start/stop individual instance or group of instances.

## Configure EC2 Instances

Instances to be scheduled must have a `AutoStartSchedule`, `AutoStopSchedule` and `ScheduledShutdown` tags
 ```
 Tag:                  Value:
 	
 AutoStartSchedule     0 9 * * *             
 AutoStopSchedule      0 21 * * *
 ScheduledShutdown     true
 Domain                MUMBAI
 ```
 
 1. **AutoStartSchedule :** 
    The particular instance will start based on this cron value.
 2. **AutoStopSchedule :** 
    The particular instance will stop based on this cron value.
 3. **ScheduledShutdown :** 
    The particular instance needs to be part of the scheduler is decided based on the value true/false.
 4. **Domain :** 
    This flag is used to group the instances and start or stop the group instances manually using api mentioned below.
   
 
 Incase, if needed to exclude particular ec2 instance to be excluded from scheduler, set `ScheduledShutdown` as `false`

## Installation 
- [serverless](https://serverless.com)

    We are using serverless for lambda setup on AWS
    
    ```./deploy.sh <{stage} [{aws profile}]>``` stage can be dev or staging
    

## Start and Stop Instance

Once lambda is deployed, you will get the POST api endpoint. 

```
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service .zip file to S3 (5.08 MB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
....................................
Serverless: Stack update finished...
Service Information
service: ec2-scheduler
stage: staging
region: ap-south-1
stack: ec2-scheduler-staging
api keys:
  None
endpoints:
  POST - https://sw1ac.execute-api.ap-south-1.amazonaws.com/staging/ec2-multi-schedule
  POST - https://sw1ac.execute-api.ap-south-1.amazonaws.com/staging/ec2-group-schedule
functions:
  scheduler: ec2-scheduler-staging-scheduler
  ec2_multi_schedule:: ec2-scheduler-staging-ec2_multi_schedule
  ec2_group_schedule: ec2-scheduler-staging-ec2_group_schedule
Serverless: Removing old service versions...

```

Note:  `scheduler` function triggers every 30 mins and is dependent on `ScheduledShutdown` flag.

**Endpoints**:

1. **ec2_multi_schedule**

    API type : POST
    
    function : ec2_multi_schedule 
    
    sample url : https://sw1ac.execute-api.ap-south-1.amazonaws.com/staging/ec2-multi-schedule
    
    sample payload: 
    ```
    {
        "instance_ids": ["i-05c9f3b83"], // valid instance ids
        "action":"start" // action should be start or stop
    }
    ```

2. **ec2_group_schedule**

    API type : POST
    
    function : ec2_group_schedule 
    
    sample url : https://sw1ac.execute-api.ap-south-1.amazonaws.com/staging/ec2-group-schedule
    
    sample payload: 
    ```
    {
        "group_ids": ["MUMBAI"], // valid domain name
        "action":"start" // action should be start or stop
    }
    ```

**Use Cases**:
 
 * Schedule your development/staging instances during working hours to save cost.
 
 
**License**
 
 GNU License (see [LICENSE](LICENSE))