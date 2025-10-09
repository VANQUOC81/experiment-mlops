# ============================================================
# BLUE-GREEN TRAFFIC MANAGEMENT SCRIPT (PowerShell)
# ============================================================
# This script helps manage traffic allocation between blue and green deployments
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
    Write-Host "Usage: .\deployment\manage-traffic.ps1 {blue-100|green-100|blue-90|blue-75|blue-50|status}" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\deployment\manage-traffic.ps1 blue-100     # All traffic to blue (rollback)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 green-100    # All traffic to green (full switch)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 blue-90      # 90% blue, 10% green (test green)" -ForegroundColor Gray
    Write-Host "  .\deployment\manage-traffic.ps1 status       # Show current traffic allocation" -ForegroundColor Gray
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
    
    # Check if both deployments exist if we're allocating traffic to green
    if ($GreenPercent -gt 0) {
        Write-Host "🔍 Checking if green deployment exists..." -ForegroundColor Cyan
        az ml online-deployment show `
            --name diabetes-deploy-green `
            --endpoint-name $ENDPOINT_NAME `
            --resource-group $RESOURCE_GROUP `
            --workspace-name $WORKSPACE_NAME 2>$null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Green deployment does not exist!" -ForegroundColor Red
            Write-Host "💡 Deploy green first: az ml online-deployment create --file src/deployment-green.yml" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "✅ Green deployment exists" -ForegroundColor Green
    }
    
    # Update traffic allocation
    $trafficString = "diabetes-deploy-blue=$BluePercent,diabetes-deploy-green=$GreenPercent"
    
    az ml online-endpoint update `
        --name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --traffic $trafficString
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Traffic updated successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to update traffic" -ForegroundColor Red
        exit 1
    }
}

function Show-Status {
    Write-Host "📊 Current Traffic Allocation:" -ForegroundColor Yellow
    
    # Get current traffic allocation
    $trafficInfo = az ml online-endpoint show `
        --name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --query "traffic" -o json
    
    Write-Host $trafficInfo
    
    # Get deployment status
    Write-Host "`n🚀 Deployment Status:" -ForegroundColor Yellow
    az ml online-deployment list `
        --endpoint-name $ENDPOINT_NAME `
        --resource-group $RESOURCE_GROUP `
        --workspace-name $WORKSPACE_NAME `
        --query "[].{Name:name, Status:provisioning_state, Traffic:traffic_percent}" `
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

Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Monitor your endpoint in Azure ML Studio" -ForegroundColor Gray
Write-Host "   2. Check logs for any errors" -ForegroundColor Gray
Write-Host "   3. Test predictions to ensure quality" -ForegroundColor Gray
Write-Host "   4. Use '.\deployment\manage-traffic.ps1 status' to check current allocation" -ForegroundColor Gray
