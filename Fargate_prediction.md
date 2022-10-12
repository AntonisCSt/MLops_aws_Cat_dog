# Steps for pushing to prediction service to fargate

Main steps taken by: 
https://www.youtube.com/watch?v=aa3gGwJpCro&t=0s

## 1) Push image to ECR

Here we going to create a new repository and push our image to ECR.

Requirements: AWS account, AWS CLI, Docker

1) Create an ECR Private repository in Amazon ECR. Make sure you copy the <ECR_URL> of your new repo.

2) In the AWS CLI, log in to ECR (for windows):

(please advise your Push commands for prediction-service for more accurate commands and OS specifications)

```
aws ecr get-login-password --region [your region] | docker login --username AWS --password-stdin [your aws_account_id].dkr.ecr.[your region].amazonaws.com
```

```
build the docker image
docker build -t <your image name>:<your tag> .
```

```
tag the docker image
docker tag <your image name> <ECR_URL>
```
```
docker tag <your image name>:<your tag> [your aws_account_id].dkr.ecr.[your region].amazonaws.com/<your aws image name>:<your aws tag>
```


Push to ECR:
```
docker push [your aws_account_id].dkr.ecr.[your region].amazonaws.com/<your aws image name>:<your aws tag>
```

Congratulations! Now your image is in the cloud!


## 2) Create your app network

We want our container (which it will contain couple of tasks) to run in a public network. We will use a load balancer to make the container accesible just to the public (through Internet Gateway) only and distribute the load to the tasks. The tasks should be in a private network so none can access them but us.

Also, we will need a NAT Gateway to make the container access internet because it needs to download some libraries.

<add image>

## 2.1) Create VPC

Let's start :

Go to VPC dashboard and create a VPC.
Choose a name and set your IPv4 CIDR (I set it to 10.0.0.0/16).

Now lets create 2 public and 2 private CIDR subnets. Go to Subnets and create:
1) public (10.0.1.0/24) in region-1a
2) public (10.0.2.0/24) in region-1b
3) private (10.0.3.0/24) in region-1a
4) private (10.0.4.0/24) in region-1b


Also, in order to make the public subnets actually public create an Internet gateway. Then go to actions and attach to your VPC.

Next, create two route tables (for public and private subnets).

#### Public route table:
1) myvpc-public-rt1 (attach your vpc you created)

Edit the public route table to have a destination 0.0.0.0/0 and target Internet Gateway.

Attach the public route table to the two public subnets.

#### Private route table:
2) myvpc-private-rt1 (attach your vpc you created)

Attach the private route table to the two private subnets.

## 2.2) Configure ECS ,Fargate and Load Balancer

## ECS

Go to your ECS clusters and create a Cluster.
Choose AWS Fargate and give it a name. It will ask you to create a VPC. You can choose the default.

Create a task definition (like a container). Choose Fargate type. Add a name of your choice. (depending on you application you might want to assign specific role. If not leave it empty). In Task excecution IAM role, create a new IAM role.
Choose minimum task sizes. Add a container. There choose your image URI from Step 1) (you have to go to ECR and choose it). In the container port mapping specify the container port. For this service the port is 9696. Leave everything the same. (You can define enviroment virables if you want). Click Create.

You can check now that you have a cluster:

<add image>

Now lets create a service:

Go to the cluster and choose "create a service". Launch type should be FARGATE. Choose 2 number of tasks (if one fails it will remove it and spin another). Rolling updates.

Configure VPC: Here aws asks you to configure the network for your tasks. so, select the VPC that was created in section 2) and as a subnets choose the private 01 and private 02 that you created. Then specify the security group. Currently the security group accepts for HTTP from anywhere. But we want only our Load balancer to access those tasks. So keep this and we will change it later!

For Load balancing choose Application Load Balancer. Health check period = 30. If you dont have a load balancer aws will give you a link for EC2. Open a tab and create a load balancer.

### Load balancer: 
In the opened page, select application load balancer. Give it a name. A listener (propably in port 80) will be selected automatically for you. For Availability zones, select two and add the two public subnets you created in section 2). In next section create a new security group. and there add HTTP on port 80 with any source (0.0.0.0/0 ::0). Configure Routing: We dont ahve any target group so create one. Make sure you select type IP. Keep the same protocol. Continue and create load balancer.

Go back to the fargate tab. Press refresh and select the load balancer you created. For ALB listener port choose the one you created before (usally 80 HTTP). Target group the ALB. Go and create your service.

Go check it out and check the tasks. If it they stopping it because your app (Dockerfile) does require internet. So we need to create a NAT Gateway for your fargate service.

### CREATE NAT GATEWAY:

NAT always goes outbound so none can access our tasks. So lets create it.

In the VPC Dashboard go to NAT Gateways. Create a new one. NAT always requires a public subent with internet access. So choose one of the public ones. And create a new EIP. 

Now we have to change the private route table.

In the private route edit routes and add route. Choose 0.0.0.0/0 and choose as a target the nat gateway.

So now the tasks should be able to reach internet. (need to wait a bit  for that).

Finnaly, we have to do one other change. We have to make sure the fargate security group have access to security group attached to the load balancer. Go to your clusters, Tasks and click update. Go to Configure network. Select the Security group. Go to Inbound Rules and edit rules. You will need the Load balancer's security group. To do that, open EC2 in a new tab. Go to load balancer section. Under the security section you can find the security group attached to the ALB (copy it). ALB should be accesible to anywhere. So, we want this ALB to access the FARGATE tasks. Copy the ALB security group and edit the source of the inbound rules of the clusters.




















