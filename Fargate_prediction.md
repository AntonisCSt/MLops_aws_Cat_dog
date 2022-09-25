# Steps for pushing to prediction service to fargate

Main steps taken by: 
https://www.youtube.com/watch?v=aa3gGwJpCro&t=2266s

## 1) Push image to ECR

log in to ECR
(aws ecr get-login --no-include-email --region us-east-1)

build the docker image
docker build -t youtube:latest .

tag the docker image
docker tag <IMAGE_NAME> <ECR_URL>

push to ECR
docker push <ECR_URL>

## 2) Create your app network

We want our container (tasks) to run in a public network. We prefer a load balancer to be accesible just to the public (Internet Gateway) only and distribute the load.

Also, we will need a NAT Gateway to outbound traffic to internet Gateway just to download needed packages.

### 2.1) Create VPC


Go to VPC dashboard and create a VPC.
Inside it create 2 public and 2 private CIDR subnets.

Also, in order to make the public subnets actually public create an Internet gateway. Go to actions and attach to your VPC.

Create two route tables (for public and private subnets).

Edit the public route table to have a destination 0.0.0.0/0 and target Internet Gateway.

Attach the private route table to the two private subnets. In Route Tables edit the subnet association. and select only the two private association you created. Do the same for the public. subnets

### 2.2) Configure ECS ,Fargate and Load Balancer

##### ECS

Go to your ECS and create a cluster.
Choose AWS Fargate and give it a name. It will ask you to create a VPC. You can choose the default.

Create a task definition (like a container). Add a name of your choice. Create a new IAM role.
Choose minimum task sizes. Add a container. There choose your image URI from Step 1) (you ave to go to ECR and choose it). In the container port mapping specify the container port *[Antonis fill this]*.

Go to the cluster and create a service. Launch type should be FARGATE. Choose 2 number of tasks (if one fails it will remove it and spin another). Rolling updates.
Configure VPC. Here you it asks you to configure the network for your tasks. So choose the VPC that was created in 2) and as a subnet choose the private one. Then Specify the security group. Currently the security group accepts for HTTP from anywhere. But we want only our Load balancer to acces those tasks. So keep this and we will change it later!

For Load balancing choose Application Load Balancer. Health check period = 30. IF you dont have a load balancer it will give you a link for EC2. Open a tab and create There create a load balancer

Load balancer: internet facing and also make sure you added public subnets. There create a new security group. and there add HTTP on port 80 with any source (0.0.0.0/0 ::0). Configure Routing: We dont ahve any target group so create one. Make sure you select type IP. Keep the same protocol. Continue and create load balancer.

GO back to the fargate tab. Press refresh and choose the load balancer you created. For ALB listener port choose the one you created before (usally 80 HTTP). Target group the ALB. Go and create your service.

Go check it out and check the tasks. If it they stopping it because your app (Dockerfile) does require internet. So we need to create a NAT Gateway for your fargate service.

#### CREATE NAT GATEWAY:

NAT always goes outbound so none can access our tasks. So lets create it.

In the VPC Dashboard go to NAT Gateways. Create a new one. NAT always requires a public subent with internet access. So choose one of the public ones. And create a new EIP. 

Now we have to change the private route table.

In the private route edit routes and add route. Choose 0.0.0.0/0 and choose as a target the nat gateway.

So now the tasks should be able to reach internet. (need to wait a bit  for that).

Finnaly, we have to do one other change. We have to make sure the fargate security group have access to security group attached to the load balancer. Go to your clusters, Tasks and click blue button update. Go to Configure network. Select the Security group. Go to inbound Rules and edit rules. You will need the Load balancer's security group. Open EC2 in a new tab. Go to load balancer section. Under the security section you can find the security group attached to the ALB. ALB should be accesible to anywhere. So, we want this ALB to access the FARGATE tasks. Copy the ALB security group and edit the source of the inbound rules of the clusters.


















