# Azure ML CLI Commands - Quick Reference

## Endpoint Management

### List all online endpoints
az ml online-endpoint list --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} -o table

### Show endpoint details
az ml online-endpoint show --name {ENDPOINT_NAME} --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} --query "{Name:name, Traffic:traffic, Status:provisioning_state}"

### Show endpoint location
az ml online-endpoint show --name {ENDPOINT_NAME} --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} --query "location"

## Deployment Management

### List deployments for an endpoint
az ml online-deployment list --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} --endpoint-name {ENDPOINT_NAME} -o table

### Show deployment details
az ml online-deployment show --name {DEPLOYMENT_NAME} --endpoint-name {ENDPOINT_NAME} --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} --query "{Name:name, Instance:instance_type, InstanceCount:instance_count, Status:provisioning_state}"

## Compute Resources

### List compute instances
az ml compute list --type ComputeInstance --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} -o table

### List batch endpoints
az ml batch-endpoint list --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} -o table

## Quota Management

### Check VM usage (FSv2)
az vm list-usage --location {LOCATION} --query "[?contains(name.value, 'FSv2')]" -o table

### Check general quota usage
az vm list-usage --location {LOCATION} --query "[?contains(name.value, 'Total') || contains(name.value, 'Cluster') || contains(name.value, 'Regional')]" -o table
