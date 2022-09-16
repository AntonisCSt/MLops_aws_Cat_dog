# MLops_aws_project
An mlops project on aws

This repo is all about the best practises of MLops.

I hope this repo is going to be guide for your ML applications.


## Data

Download data from https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset?resource=download .

Create ./data folder and save this dataset on that folder.

## Project roadmap:
0) Find project (smoke data used from kaggle check rest of readme for data source link)
  0.1 Train initial model (DONE) 6/9/2022 : Trained with Random forest and got very good score ~0.99 acc(especially after dropping features due to collinearity) 

1) Create application locally (flask) (DONE) 9/10/2022

2) Dockerize local application (DONE) 9/10/2022

    2.1 Add CI/CD

3) Connect Database. (MongoDB) (DONE) 9/10/2022

4) Create a docker compose (DONE) 9/10/2022

5) Push to ECS

  5.1) Add terraform

6) Expand app by using Monitoring

7) Push expanded app to ECS

8) Add monitoring service to terraform

## Approach 1 ECS and AWS database

## Approach 2 Kubernetes and EKS


## Approach 3 ECS all

Instructions:

make sure you have attached your IAM polices

https://aws.amazon.com/blogs/containers/deploy-applications-on-amazon-ecs-using-docker-compose/
```
docker context create ecs myecs

docker context use myecs

docker compose --project-name smokepred -f docker-compose-ecs.yml up
```
to stop it:
```
docker compose --project-name smokepred down 
```


### conclusions:

You get less control over your services

### next steps:

How to update?

#### read next:

Load balancers
ECS yelp tutorial
security groups
again VPC

