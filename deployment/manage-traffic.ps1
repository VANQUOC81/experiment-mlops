# ============================================================
# BLUE-GREEN TRAFFIC MANAGEMENT SCRIPT (PowerShell)
# ============================================================
# This script helps manage traffic allocation between blue and green deployments
#
# IMPORTANT: Traffic allocation rules
# - With 2+ deployments: Traffic must sum to 100%
# - With 1 deployment: Can be set to 0% before deletion
#
# Usage:
#   .\deployment\manage-traffic.ps1 blue-100    # 100% blue, 0% green
#   .\deployment\manage-traffic.ps1 green-100   # 0% blue, 100% green  
#   .\deployment\manage-traffic.ps1 blue-90     # 90% blue, 10% green
#   .\deployment\manage-traffic.ps1 status      # Show current traffic
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Action
)

$ENDPOINT_NAME = "diabetes-prediction-endpoint"
$RESOURCE_GROUP = "todozi-data-science-rg"
$WORKSPACE_NAME = "todozi-ml-ws"

function Show-Usage {
    Write-Host "Usage: .\deployment\manage-traffic.ps1 {blue-100|green-100|blue-90|blue-75|blue-50|blue-0|green-0|status}" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Traffic Management:" -ForegroundColor Cyan
    Write-Host "  .\deployment\manage-traffic.ps1 blue-100     # All traffic to blue (rollback)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 green-100    # All traffic to green (full switch)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 blue-90      # 90% blue, 10% green (test green)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 blue-75      # 75% blue, 25% green" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 blue-50      # 50/50 split (A/B testing)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Prepare for Deletion (sets traffic to 0% before deleting):" -ForegroundColor Cyan
    Write-Host '  .\deployment\manage-traffic.ps1 blue-0       # Set blue to 0% (only if it is the sole deployment)' -ForegroundColor Gray
    Write-Host '  .\deployment\manage-traffic.ps1 green-0      # Set green to 0% (only if it is the sole deployment)' -ForegroundColor Gray
    Write-Host ""
    Write-Host "Status:" -ForegroundColor Cyan
    Write-Host "  .\deployment\manage-traffic.ps1 status       # Show current traffic allocation" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Note: With multiple deployments, traffic must sum to 100%." -ForegroundColor Yellow
}

function Update-Traffic {
    param(
        [int]$BluePercent,
        [int]$GreenPercent,
        [string]$Description
    )
    
    Write-Host "🔄 Updating traffic allocation..." -ForegroundColor Blue
    Write-Host "   Blue:  $BluePercent%" -ForegroundColor Blue
    Write-Host "   Green: $GreenPercent%" -ForegroundColor Green
    Write-Host "   Description: $Description" -ForegroundColor Gray
    
    # Check which deployments exist
    Write-Host "🔍 Checking existing deployments..." -ForegroundColor Cyan
    
    $blueExists = $false
    $greenExists = $false
    
    az ml online-deployment show `
        --name diabetes-deploy-blue `
        --endpoint-name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $blueExists = $true
        Write-Host "   ✓ Blue deployment exists" -ForegroundColor Gray
    }
    
    az ml online-deployment show `
        --name diabetes-deploy-green `
        --endpoint-name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $greenExists = $true
        Write-Host "   ✓ Green deployment exists" -ForegroundColor Gray
    }
    
    # Validate traffic allocation based on what exists
    if ($BluePercent -eq 0 -and $GreenPercent -eq 0) {
        Write-Host "❌ Cannot set all deployments to 0% traffic!" -ForegroundColor Red
        Write-Host "Use 'blue-0' or 'green-0' to set a single deployment to 0% before deletion." -ForegroundColor Yellow
        exit 1
    }
    
    # If trying to allocate to green but it doesn't exist
    if ($GreenPercent -gt 0 -and -not $greenExists) {
        Write-Host "❌ Green deployment does not exist!" -ForegroundColor Red
        Write-Host "Deploy green first using GitHub Actions workflow (select 'green')" -ForegroundColor Yellow
        exit 1
    }
    
    # If trying to allocate to blue but it doesn't exist
    if ($BluePercent -gt 0 -and -not $blueExists) {
        Write-Host "❌ Blue deployment does not exist!" -ForegroundColor Red
        Write-Host "Deploy blue first using GitHub Actions workflow (select 'blue')" -ForegroundColor Yellow
        exit 1
    }
    
    # Build traffic string based on which deployments exist
    # Azure ML requires you to only specify deployments that actually exist
    $trafficParts = @()
    if ($blueExists) {
        $trafficParts += "diabetes-deploy-blue=$BluePercent"
    }
    if ($greenExists) {
        $trafficParts += "diabetes-deploy-green=$GreenPercent"
    }
    $trafficString = $trafficParts -join ","
    
    Write-Host "   Traffic string: $trafficString" -ForegroundColor Gray
    
    # NOTE: Azure CLI may throw internal Python errors (ValueError) but the operation often succeeds
    # We suppress errors and verify success by checking the actual endpoint state afterward
    Write-Host "🔄 Applying traffic change..." -ForegroundColor Cyan
    
    az ml online-endpoint update `
        --name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --traffic $trafficString 2>$null
    
    # Don't rely on exit code - verify by checking actual traffic state
    Write-Host "🔍 Verifying traffic allocation..." -ForegroundColor Cyan
    
    $currentTraffic = az ml online-endpoint show `
        --name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --query "traffic" -o json | ConvertFrom-Json
    
    # Check if the traffic was actually updated correctly
    $actualBlue = if ($currentTraffic."diabetes-deploy-blue") { $currentTraffic."diabetes-deploy-blue" } else { 0 }
    $actualGreen = if ($currentTraffic."diabetes-deploy-green") { $currentTraffic."diabetes-deploy-green" } else { 0 }
    
    if ($actualBlue -eq $BluePercent -and $actualGreen -eq $GreenPercent) {
        Write-Host "✅ Traffic updated successfully!" -ForegroundColor Green
        Write-Host "   Current state: Blue=$actualBlue%, Green=$actualGreen%" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Traffic allocation may not have updated correctly" -ForegroundColor Yellow
        Write-Host "   Expected: Blue=$BluePercent%, Green=$GreenPercent%" -ForegroundColor Gray
        Write-Host "   Actual:   Blue=$actualBlue%, Green=$actualGreen%" -ForegroundColor Gray
        Write-Host "💡 This might be an Azure CLI internal error. Check Azure ML Studio to verify." -ForegroundColor Yellow
    }
}

function Show-Status {
    Write-Host "Current Traffic Allocation:" -ForegroundColor Yellow
    
    # Get current traffic allocation
    $trafficInfo = az ml online-endpoint show `
        --name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --query "traffic" -o json
    
    Write-Host $trafficInfo
    
    # Get deployment status
    Write-Host "`nDeployment Status:" -ForegroundColor Yellow
    az ml online-deployment list `
        --endpoint-name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --query '[].{Name:name, Status:provisioning_state, Traffic:traffic_percent}' `
        -o table
}

# Main logic
switch ($Action) {
    "blue-100" {
        Update-Traffic -BluePercent 100 -GreenPercent 0 -Description "All traffic to blue (rollback)"
    }
    "green-100" {
        Update-Traffic -BluePercent 0 -GreenPercent 100 -Description "All traffic to green (full switch)"
    }
    "blue-90" {
        Update-Traffic -BluePercent 90 -GreenPercent 10 -Description "90% blue, 10% green (test green)"
    }
    "blue-75" {
        Update-Traffic -BluePercent 75 -GreenPercent 25 -Description "75% blue, 25% green (gradual rollout)"
    }
    "blue-50" {
        Update-Traffic -BluePercent 50 -GreenPercent 50 -Description "50/50 split (A/B testing)"
    }
    "blue-0" {
        Write-Host "⚠️  Preparing blue deployment for deletion (setting to 0% traffic)" -ForegroundColor Yellow
        Write-Host "💡 This only works if blue is the ONLY deployment" -ForegroundColor Yellow
        Write-Host ""
        
        # Check if green exists - if it does, this operation is not allowed
        az ml online-deployment show `
            --name diabetes-deploy-green `
            --endpoint-name $ENDPOINT_NAME `
            --resource-group $RESOURCE_GROUP `
            --workspace-name $WORKSPACE_NAME 2>$null | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "❌ Cannot set blue to 0% because green deployment exists!" -ForegroundColor Red
            Write-Host "Use 'green-100' to route all traffic to green first, then delete blue" -ForegroundColor Yellow
            exit 1
        }
        
        # Only blue exists, so we can set it to 0%
        az ml online-endpoint update `
            --name $ENDPOINT_NAME `
            --resource-group $RESOURCE_GROUP `
            --workspace-name $WORKSPACE_NAME `
            --traffic "diabetes-deploy-blue=0" 2>$null
        
        Write-Host "✅ Blue deployment set to 0% traffic" -ForegroundColor Green
        Write-Host ""
        Write-Host "🗑️  Next step: Delete the deployment" -ForegroundColor Yellow
        Write-Host "   az ml online-deployment delete --name diabetes-deploy-blue --endpoint-name $ENDPOINT_NAME --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME --yes" -ForegroundColor Gray
    }
    "green-0" {
        Write-Host "⚠️  Preparing green deployment for deletion (setting to 0% traffic)" -ForegroundColor Yellow
        Write-Host "💡 This only works if green is the ONLY deployment" -ForegroundColor Yellow
        Write-Host ""
        
        # Check if blue exists - if it does, this operation is not allowed
        az ml online-deployment show `
            --name diabetes-deploy-blue `
            --endpoint-name $ENDPOINT_NAME `
            --resource-group $RESOURCE_GROUP `
            --workspace-name $WORKSPACE_NAME 2>$null | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "❌ Cannot set green to 0% because blue deployment exists!" -ForegroundColor Red
            Write-Host "Use 'blue-100' to route all traffic to blue first, then delete green" -ForegroundColor Yellow
            exit 1
        }
        
        # Only green exists, so we can set it to 0%
        az ml online-endpoint update `
            --name $ENDPOINT_NAME `
            --resource-group $RESOURCE_GROUP `
            --workspace-name $WORKSPACE_NAME `
            --traffic "diabetes-deploy-green=0" 2>$null
        
        Write-Host "✅ Green deployment set to 0% traffic" -ForegroundColor Green
        Write-Host ""
        Write-Host "🗑️  Next step: Delete the deployment" -ForegroundColor Yellow
        Write-Host "   az ml online-deployment delete --name diabetes-deploy-green --endpoint-name $ENDPOINT_NAME --resource-group $RESOURCE_GROUP --workspace-name $WORKSPACE_NAME --yes" -ForegroundColor Gray
    }
    "status" {
        Show-Status
    }
    default {
        Write-Host "❌ Invalid option: $Action" -ForegroundColor Red
        Write-Host ""
        Show-Usage
        exit 1
    }
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host '   1. Monitor your endpoint in Azure ML Studio' -ForegroundColor Gray
Write-Host '   2. Check logs for any errors' -ForegroundColor Gray
Write-Host '   3. Test predictions to ensure quality' -ForegroundColor Gray
Write-Host '   4. Use .\deployment\manage-traffic.ps1 status to check current allocation' -ForegroundColor Gray
