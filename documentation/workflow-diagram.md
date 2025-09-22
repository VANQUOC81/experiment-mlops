# MLOps Workflow Execution Diagram

## Complete CI/CD Pipeline Flow

```mermaid
graph TD
    A[Push to main] --> B[Development Job Starts]
    B --> C[Submit Azure ML Dev Job]
    C --> D[Poll Azure ML Status Every 30s]
    D --> E{Azure ML Dev Complete?}
    E -->|❌ Failed| F[GitHub Actions FAILS ❌]
    E -->|⏳ Running| D
    E -->|✅ Success| G[GitHub Actions SUCCESS ✅]
    G --> H[Production Job Waits for Approval]
    H --> I[Manual Approval Required]
    I --> J[Submit Azure ML Prod Job]
    J --> K[Poll Azure ML Prod Status Every 30s]
    K --> L{Azure ML Prod Complete?}
    L -->|❌ Failed| M[GitHub Actions FAILS ❌]
    L -->|⏳ Running| K
    L -->|✅ Success| N[Complete Pipeline SUCCESS ✅]
    
    style A fill:#e1f5fe
    style F fill:#ffebee
    style M fill:#ffebee
    style G fill:#e8f5e8
    style N fill:#e8f5e8
    style I fill:#fff3e0
```

## Key Features

- **True Success Validation**: GitHub Actions only succeeds when actual Azure ML training completes
- **Automatic Polling**: Checks Azure ML job status every 30 seconds
- **Fail-Fast**: Stops pipeline immediately if any Azure ML job fails
- **Manual Approval**: Production requires human approval before training
- **End-to-End Tracking**: Full visibility from code commit to model training completion

## Status Meanings

| Status | Description |
|--------|-------------|
| **Completed** | Azure ML job finished successfully |
| **Failed** | Azure ML job encountered an error |
| **Running** | Azure ML job is still training |
| **Canceled** | Azure ML job was manually stopped |
| **NotStarted** | Azure ML job hasn't begun execution |

This diagram shows the enhanced workflow that ensures the production job only runs when the experiment job's **Azure ML training** (not just submission) completes successfully.
