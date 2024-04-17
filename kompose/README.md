## Deploy to K8s (Open Telekom Cloud)

### Manual steps:

- Create Elastic Volume Service (EVS) [separate resource outside the cluster]
- Create Persistent Volume (PV) in K8s/Storages and bound to the EVS

Execute (having proper kubectl config)

`kubectl apply -f .`

### Networking

1. Create Elastic IP (EIP)
2. Create NAT Gateway with SNAT Rule associated with the EIP
3. Attach the NAT Gateway to K8s VPC
