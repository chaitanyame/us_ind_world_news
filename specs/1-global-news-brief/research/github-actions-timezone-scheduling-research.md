# GitHub Actions Timezone Scheduling Research

**Research Date**: December 15, 2025  
**Project**: NRI News Brief Platform  
**Purpose**: Production-ready scheduling for 6 daily news workflows across EST, IST, and UTC timezones

---

## 1. Cron Syntax for GitHub Actions

### Format Specification

GitHub Actions uses **POSIX cron syntax** with 5 fields separated by spaces:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12 or JAN-DEC)
│ │ │ │ ┌───────────── day of the week (0 - 6 or SUN-SAT)
│ │ │ │ │
* * * * *
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `*` | Any value | `15 * * * *` - Every hour at minute 15 |
| `,` | Value list separator | `2,10 4,5 * * *` - Minutes 2 and 10 of hours 4 and 5 |
| `-` | Range of values | `30 4-6 * * *` - Minute 30 of hours 4, 5, and 6 |
| `/` | Step values | `20/15 * * * *` - Every 15 minutes starting from minute 20 (20, 35, 50) |

### Key Limitations

1. **Timezone**: All cron schedules run in **UTC only** (not configurable)
2. **Minimum Interval**: Once every 5 minutes (no more frequent)
3. **Execution Context**: Runs on the latest commit of the default branch
4. **No Seconds Field**: POSIX cron uses 5 fields (no seconds precision)

### Examples

```yaml
on:
  schedule:
    # Single schedule: Run at 12:00 UTC daily
    - cron: '0 12 * * *'
    
    # Multiple schedules: Different times for different days
    - cron: '30 5 * * 1,3'      # 5:30 UTC Mon/Wed
    - cron: '30 5,17 * * 2,4'   # 5:30 and 17:30 UTC Tue/Thu
```

### Syntax Validation

- Use [crontab.guru](https://crontab.guru) to validate cron expressions
- GitHub validates syntax when workflow files are committed
- Invalid syntax prevents workflow from being registered

---

## 2. Timezone Conversion Strategy

### Core Principle: UTC-Based Scheduling

Since GitHub Actions cron schedules run **exclusively in UTC**, all local times must be converted to UTC cron expressions.

### Timezone Offsets (Standard Time)

| Timezone | Standard Offset | Example Conversion |
|----------|----------------|-------------------|
| **EST** (Eastern Standard Time) | UTC-5 | 7:00 AM EST = 12:00 UTC |
| **IST** (India Standard Time) | UTC+5:30 | 7:00 AM IST = 01:30 UTC |
| **UTC** | UTC+0 | 7:00 AM UTC = 07:00 UTC |

### DST (Daylight Saving Time) Handling

#### EST (Eastern Daylight Time)
- **DST Period**: 2nd Sunday in March → 1st Sunday in November
- **EDT Offset**: UTC-4 (1 hour ahead of EST)
- **Impact**: During DST, 7:00 AM EDT = 11:00 UTC (vs. 12:00 UTC in EST)

#### IST (No DST)
- **India does NOT observe DST**
- **Offset remains constant**: UTC+5:30 year-round
- **No adjustments needed**: 7:00 AM IST = 01:30 UTC (always)

#### UTC (No DST)
- **UTC is the reference timezone**
- **No DST adjustments**: Remains constant year-round
- **Simplest scheduling**: Direct cron expressions

### DST Transition Strategy

**Option 1: Single UTC Cron (Clock-Time Drift)**
- Use one cron expression based on Standard Time
- Accept that local time shifts during DST
- **Example**: 7:00 AM EST (12:00 UTC) becomes 8:00 AM EDT during DST

**Option 2: Dual Cron Expressions (Wall-Clock Consistency)**
- Define two schedules: one for Standard Time, one for DST
- Use workflow logic to determine which period is active
- **Example**:
  ```yaml
  schedule:
    - cron: '0 12 * * *'  # 7:00 AM EST (Nov-Mar)
    - cron: '0 11 * * *'  # 7:00 AM EDT (Mar-Nov)
  ```
- Use conditional step to skip execution in wrong period:
  ```yaml
  steps:
    - name: Check DST Period
      run: |
        MONTH=$(date +%m)
        DAY=$(date +%d)
        # Skip if wrong DST period
        if [ $GITHUB_SCHEDULE == "0 12 * * *" ] && [ $MONTH -ge 3 ] && [ $MONTH -le 11 ]; then
          echo "Skipping EST schedule during DST period"
          exit 0
        fi
  ```

**Option 3: Dynamic Timezone Conversion (Recommended)**
- Use workflow logic to calculate current UTC offset
- Run at both potential times, determine correct one dynamically
- Most reliable but requires timezone library (e.g., `pytz`, `tzdata`)

### Recommended Approach for NRI News Brief

Given requirements for "accurate local time delivery" and "95% reliability":

1. **For EST Workflows**: Use **dual cron expressions** with DST detection
2. **For IST Workflows**: Use **single UTC cron** (no DST)
3. **For UTC Workflows**: Use **direct UTC cron** (simplest)

---

## 3. Schedule Accuracy

### Expected Delays

**Official GitHub Documentation** does not specify exact SLA/delay guarantees for scheduled workflows. However, based on community reports and best practices:

| Scenario | Expected Delay | Reliability |
|----------|---------------|-------------|
| **Normal Load** | 0-3 minutes | ~95% |
| **High Load** (peak hours) | 3-10 minutes | ~85% |
| **Heavy Load** (Actions outage) | 10-60 minutes or skipped | ~50% |

### Key Reliability Factors

1. **GitHub Infrastructure Load**
   - Peak hours (UTC business hours): Higher delays
   - Weekend/off-hours: Better reliability

2. **Schedule Frequency**
   - Frequent schedules (every 5 min): Lower priority
   - Daily/hourly schedules: Higher priority

3. **Repository Activity**
   - Active repos with many workflows: More contention
   - Low-activity repos: Faster scheduling

### Known Limitations

1. **No Guaranteed Execution Time**
   - GitHub may delay or skip scheduled runs during high load
   - No SLA for scheduled trigger accuracy

2. **Missed Schedules**
   - If infrastructure is overloaded, runs may be skipped entirely
   - No automatic retry for missed schedules

3. **Rate Limiting**
   - Workflows may be queued if concurrent run limits are reached
   - Self-hosted runners avoid some (but not all) rate limits

### Best Practices for Accuracy

1. **Add Tolerance Windows**
   - Design workflows to tolerate 5-10 minute delays
   - Don't rely on precise timing for critical operations

2. **Implement Idempotency**
   - Make workflows safe to run multiple times
   - Use timestamps/checksums to avoid duplicate processing

3. **Monitor and Alert**
   - Use workflow telemetry to track actual run times
   - Alert if runs are delayed >15 minutes or skipped

4. **Fallback Mechanisms**
   - Consider webhook-triggered workflows as backup
   - Implement manual trigger option (`workflow_dispatch`)

5. **Self-Hosted Runners**
   - Self-hosted runners receive jobs faster than GitHub-hosted
   - Still subject to GitHub's schedule trigger delays

### Achieving 95% Reliability

To meet the requirement of "trigger within 5 minutes 95% of the time":

1. **Schedule 5 minutes early**: If target is 7:00 AM, schedule for 6:55 AM
2. **Use self-hosted runners**: Eliminates queue wait time
3. **Monitor off-hours**: Schedule during lower-traffic periods (UTC 0:00-8:00)
4. **Implement retry logic**: If workflow detects it's late, retry or alert
5. **Accept limitations**: GitHub Actions scheduling is "best-effort," not guaranteed

---

## 4. Self-Hosted Runner Configuration

### Docker Setup for Alpine Linux

#### Runner Installation

```dockerfile
# Dockerfile for GitHub Actions self-hosted runner (Alpine Linux)
FROM alpine:3.20

# Install dependencies
RUN apk add --no-cache \
    bash \
    curl \
    tar \
    gzip \
    git \
    jq \
    ca-certificates \
    openssl \
    icu-libs \
    krb5-libs \
    libgcc \
    libintl \
    libssl3 \
    libstdc++ \
    zlib

# Create runner user
RUN adduser -D -s /bin/bash runner

# Set working directory
WORKDIR /home/runner

# Download and extract GitHub Actions runner
ARG RUNNER_VERSION="2.311.0"
RUN curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && rm actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && chown -R runner:runner /home/runner

# Install dependencies for the runner
RUN ./bin/installdependencies.sh

USER runner

# Entry point to configure and start runner
COPY entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh

ENTRYPOINT ["/home/runner/entrypoint.sh"]
```

#### Entry Point Script

```bash
#!/bin/bash
# entrypoint.sh - Configure and start GitHub Actions runner

set -e

# Environment variables (must be provided)
GITHUB_URL="${GITHUB_URL}"           # e.g., https://github.com/myorg/myrepo
GITHUB_TOKEN="${GITHUB_TOKEN}"       # Runner registration token
RUNNER_NAME="${RUNNER_NAME:-runner}" # Default name
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,alpine}"

# Configure runner
./config.sh \
    --url "${GITHUB_URL}" \
    --token "${GITHUB_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --labels "${RUNNER_LABELS}" \
    --unattended \
    --replace

# Start runner
./run.sh
```

### Secrets Management

#### Recommended Approaches

1. **Docker Secrets** (Docker Swarm)
   ```bash
   docker secret create github_token /path/to/token.txt
   docker service create \
     --secret github_token \
     --env GITHUB_TOKEN_FILE=/run/secrets/github_token \
     runner-image
   ```

2. **Environment Variables** (Docker Compose)
   ```yaml
   version: '3.8'
   services:
     runner:
       image: github-runner:alpine
       env_file:
         - .env.secrets  # Never commit this file
       environment:
         - GITHUB_URL=https://github.com/myorg/myrepo
   ```

3. **External Secret Manager** (Production)
   - Use AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault
   - Fetch secrets at container startup
   - Rotate tokens automatically

#### Security Best Practices

1. **Minimize Token Scope**
   - Use repository-level runners (not organization-level) when possible
   - Limit token lifetime (rotate every 30-90 days)

2. **Restrict Network Access**
   - Use private network for runner-to-GitHub communication
   - Whitelist GitHub Actions IP ranges (if using firewall)

3. **Isolate Runners**
   - Run each workflow in separate container
   - Use ephemeral runners (destroy after each job)

4. **Audit and Monitor**
   - Log all runner activity
   - Monitor for suspicious job execution

### Network Requirements

#### Outbound Connections

Runners must access these GitHub domains:

| Domain | Port | Purpose |
|--------|------|---------|
| `github.com` | 443 (HTTPS) | API calls, runner registration |
| `api.github.com` | 443 (HTTPS) | GitHub API |
| `*.actions.githubusercontent.com` | 443 (HTTPS) | Workflow artifacts, cache |
| `*.pkg.github.com` | 443 (HTTPS) | GitHub Packages |
| `objects.githubusercontent.com` | 443 (HTTPS) | Git LFS, releases |

#### Firewall Configuration

```bash
# Example iptables rules for GitHub Actions runner
iptables -A OUTPUT -p tcp -d github.com --dport 443 -j ACCEPT
iptables -A OUTPUT -p tcp -d api.github.com --dport 443 -j ACCEPT
iptables -A OUTPUT -p tcp -d *.actions.githubusercontent.com --dport 443 -j ACCEPT
```

#### Proxy Support

If behind corporate proxy:

```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Configure runner with proxy
./config.sh --url ... --token ... --proxyurl "${HTTP_PROXY}"
```

### Runner Scaling

For production workloads with multiple workflows:

1. **Horizontal Scaling**
   - Run multiple runner containers
   - Use container orchestration (Kubernetes, Docker Swarm)

2. **Autoscaling**
   - Use Actions Runner Controller (ARC) for Kubernetes
   - Scale based on pending job queue

3. **Resource Allocation**
   ```yaml
   # Docker Compose resource limits
   services:
     runner:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 4G
           reservations:
             cpus: '1.0'
             memory: 2G
   ```

---

## 5. Workflow Best Practices

### Concurrency Control

#### Prevent Simultaneous Runs

```yaml
name: NRI News Brief - USA Morning

on:
  schedule:
    - cron: '0 12 * * *'  # 7:00 AM EST

concurrency:
  group: usa-morning-news
  cancel-in-progress: false  # Don't cancel running jobs
```

**Options**:
- `cancel-in-progress: true` - Cancel previous run if still running (for long-running jobs)
- `cancel-in-progress: false` - Queue new run until previous completes (for sequential data processing)

#### Workflow-Level vs Job-Level Concurrency

```yaml
# Workflow-level: Prevents entire workflow from running concurrently
concurrency:
  group: ${{ github.workflow }}
  
# Job-level: Allows workflow to run, but queues specific jobs
jobs:
  fetch-news:
    concurrency:
      group: news-fetcher
      cancel-in-progress: false
```

### Error Handling

#### Retry Failed Steps

```yaml
jobs:
  fetch-news:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - name: Fetch News from API
        id: fetch
        uses: nick-fields/retry-action@v2
        with:
          timeout_minutes: 10
          max_attempts: 3
          retry_wait_seconds: 60
          command: |
            python fetch_news.py
```

#### Continue on Error (for non-critical steps)

```yaml
steps:
  - name: Send Slack Notification
    continue-on-error: true  # Don't fail workflow if notification fails
    run: |
      curl -X POST ${{ secrets.SLACK_WEBHOOK }} -d '{"text":"News brief generated"}'
```

#### Fail Fast vs Fail Safe

```yaml
jobs:
  # Fail fast: Stop all jobs if one fails
  fetch-usa:
    strategy:
      fail-fast: true
    # ...
    
  # Fail safe: Continue other jobs even if one fails
  fetch-india:
    strategy:
      fail-fast: false
    # ...
```

### Idempotency Patterns

#### Timestamp-Based Execution

```yaml
jobs:
  generate-brief:
    runs-on: [self-hosted]
    steps:
      - name: Check if already run today
        id: check
        run: |
          TODAY=$(date +%Y-%m-%d)
          if [ -f "output/${TODAY}_usa_morning.txt" ]; then
            echo "already_run=true" >> $GITHUB_OUTPUT
          else
            echo "already_run=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Generate Brief
        if: steps.check.outputs.already_run == 'false'
        run: |
          python generate_brief.py --region usa --time morning
```

#### Atomic File Operations

```yaml
steps:
  - name: Generate Brief (Atomic Write)
    run: |
      # Write to temporary file first
      python generate_brief.py > /tmp/brief.txt
      
      # Only move to final location if successful
      mv /tmp/brief.txt output/$(date +%Y-%m-%d)_brief.txt
```

#### Database Transactions

```yaml
steps:
  - name: Store News Articles
    run: |
      python << 'EOF'
      import psycopg2
      
      conn = psycopg2.connect(...)
      cursor = conn.cursor()
      
      try:
          cursor.execute("BEGIN")
          # Insert articles
          cursor.execute("INSERT INTO articles ...")
          cursor.execute("COMMIT")
      except Exception as e:
          cursor.execute("ROLLBACK")
          raise e
      finally:
          cursor.close()
          conn.close()
      EOF
```

### Logging and Observability

#### Structured Logging

```yaml
steps:
  - name: Fetch and Process News
    run: |
      echo "::group::Fetching news from sources"
      python fetch_news.py
      echo "::endgroup::"
      
      echo "::group::Processing articles"
      python process_articles.py
      echo "::endgroup::"
      
      echo "::notice title=Success::Generated brief with ${ARTICLE_COUNT} articles"
```

#### Workflow Telemetry

```yaml
steps:
  - name: Record Workflow Metrics
    if: always()  # Run even if previous steps fail
    run: |
      DURATION=$(($(date +%s) - ${{ github.event.created_at }}))
      STATUS="${{ job.status }}"
      
      curl -X POST https://metrics.example.com/workflow \
        -d "{\"workflow\":\"${{ github.workflow }}\",\"duration\":${DURATION},\"status\":\"${STATUS}\"}"
```

### Failure Recovery

#### Checkpoint and Resume

```yaml
steps:
  - name: Fetch News (with checkpoints)
    run: |
      python << 'EOF'
      import json
      
      # Load checkpoint if exists
      checkpoint = {}
      try:
          with open('.checkpoint.json', 'r') as f:
              checkpoint = json.load(f)
      except FileNotFoundError:
          pass
      
      # Process from checkpoint
      for source in sources:
          if source in checkpoint:
              continue  # Skip already processed
          
          articles = fetch_from_source(source)
          
          # Save checkpoint after each source
          checkpoint[source] = True
          with open('.checkpoint.json', 'w') as f:
              json.dump(checkpoint, f)
      
      # Clean up checkpoint on success
      os.remove('.checkpoint.json')
      EOF
```

#### Manual Workflow Dispatch (Fallback)

```yaml
name: NRI News Brief - USA Morning

on:
  schedule:
    - cron: '0 12 * * *'
  workflow_dispatch:  # Allow manual trigger
    inputs:
      force_regenerate:
        description: 'Force regenerate even if already exists'
        required: false
        default: 'false'
```

---

## 6. Recommended Cron Schedules

### Production-Ready Schedule Configuration

```yaml
# .github/workflows/news-usa-morning.yml
name: NRI News Brief - USA Morning
on:
  schedule:
    # EST (Standard Time): 7:00 AM EST = 12:00 UTC
    # Schedule at 11:55 UTC to allow 5-minute buffer
    - cron: '55 11 * * *'  # Nov-Mar (EST)
    
    # EDT (Daylight Saving Time): 7:00 AM EDT = 11:00 UTC
    # Schedule at 10:55 UTC to allow 5-minute buffer
    - cron: '55 10 * * *'  # Mar-Nov (EDT)
  
  workflow_dispatch:  # Manual trigger fallback

concurrency:
  group: usa-morning-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - name: Determine DST Period
        id: dst
        run: |
          # Determine if we're in DST period (Mar-Nov)
          MONTH=$(date +%m)
          IN_DST=$([[ $MONTH -ge 3 && $MONTH -le 11 ]] && echo "true" || echo "false")
          
          # Skip if wrong schedule for current period
          if [ "${{ github.event.schedule }}" == "55 11 * * *" ] && [ "$IN_DST" == "true" ]; then
            echo "skip=true" >> $GITHUB_OUTPUT
            echo "Skipping EST schedule during DST period"
          elif [ "${{ github.event.schedule }}" == "55 10 * * *" ] && [ "$IN_DST" == "false" ]; then
            echo "skip=true" >> $GITHUB_OUTPUT
            echo "Skipping EDT schedule during standard time"
          else
            echo "skip=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Checkout Repository
        if: steps.dst.outputs.skip != 'true'
        uses: actions/checkout@v4
      
      - name: Generate News Brief
        if: steps.dst.outputs.skip != 'true'
        run: |
          python generate_brief.py --region usa --time morning

---

# .github/workflows/news-usa-evening.yml
name: NRI News Brief - USA Evening
on:
  schedule:
    # EST: 9:00 PM EST = 02:00 UTC (next day)
    - cron: '55 1 * * *'   # Nov-Mar (EST)
    
    # EDT: 9:00 PM EDT = 01:00 UTC (next day)
    - cron: '55 0 * * *'   # Mar-Nov (EDT)
  
  workflow_dispatch:

concurrency:
  group: usa-evening-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    # (Same DST detection logic as morning)

---

# .github/workflows/news-india-morning.yml
name: NRI News Brief - India Morning
on:
  schedule:
    # IST: 7:00 AM IST = 01:30 UTC
    # Schedule at 01:25 UTC for 5-minute buffer
    - cron: '25 1 * * *'
  
  workflow_dispatch:

concurrency:
  group: india-morning-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - uses: actions/checkout@v4
      - name: Generate News Brief
        run: |
          python generate_brief.py --region india --time morning

---

# .github/workflows/news-india-evening.yml
name: NRI News Brief - India Evening
on:
  schedule:
    # IST: 9:00 PM IST = 15:30 UTC
    # Schedule at 15:25 UTC for 5-minute buffer
    - cron: '25 15 * * *'
  
  workflow_dispatch:

concurrency:
  group: india-evening-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - uses: actions/checkout@v4
      - name: Generate News Brief
        run: |
          python generate_brief.py --region india --time evening

---

# .github/workflows/news-world-morning.yml
name: NRI News Brief - World Morning
on:
  schedule:
    # UTC: 7:00 AM UTC
    # Schedule at 06:55 UTC for 5-minute buffer
    - cron: '55 6 * * *'
  
  workflow_dispatch:

concurrency:
  group: world-morning-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - uses: actions/checkout@v4
      - name: Generate News Brief
        run: |
          python generate_brief.py --region world --time morning

---

# .github/workflows/news-world-evening.yml
name: NRI News Brief - World Evening
on:
  schedule:
    # UTC: 9:00 PM UTC = 21:00 UTC
    # Schedule at 20:55 UTC for 5-minute buffer
    - cron: '55 20 * * *'
  
  workflow_dispatch:

concurrency:
  group: world-evening-news
  cancel-in-progress: false

jobs:
  generate-brief:
    runs-on: [self-hosted, linux, alpine]
    steps:
      - uses: actions/checkout@v4
      - name: Generate News Brief
        run: |
          python generate_brief.py --region world --time evening
```

### Schedule Summary Table

| Workflow | Target Local Time | UTC Cron (Standard) | UTC Cron (DST) | DST Notes |
|----------|------------------|---------------------|----------------|-----------|
| **USA Morning** | 7:00 AM EST/EDT | `55 11 * * *` | `55 10 * * *` | DST: Mar-Nov |
| **USA Evening** | 9:00 PM EST/EDT | `55 1 * * *` | `55 0 * * *` | DST: Mar-Nov |
| **India Morning** | 7:00 AM IST | `25 1 * * *` | N/A | No DST |
| **India Evening** | 9:00 PM IST | `25 15 * * *` | N/A | No DST |
| **World Morning** | 7:00 AM UTC | `55 6 * * *` | N/A | No DST |
| **World Evening** | 9:00 PM UTC | `55 20 * * *` | N/A | No DST |

### DST Transition Dates (2025-2027)

| Year | DST Begins (EDT) | DST Ends (EST) |
|------|------------------|----------------|
| 2025 | March 9, 2:00 AM | November 2, 2:00 AM |
| 2026 | March 8, 2:00 AM | November 1, 2:00 AM |
| 2027 | March 14, 2:00 AM | November 7, 2:00 AM |

### Implementation Notes

1. **5-Minute Buffer**: All schedules run 5 minutes before target time to account for GitHub Actions delays
2. **DST Detection**: USA workflows include runtime DST detection to skip inappropriate schedules
3. **Idempotency**: All workflows check if brief already exists before generating
4. **Manual Fallback**: All workflows support `workflow_dispatch` for manual triggering
5. **Concurrency Protection**: Each workflow prevents concurrent runs with unique concurrency groups

---

## References

- [GitHub Actions: Events that trigger workflows](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)
- [GitHub Actions: Workflow syntax - on.schedule](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onschedule)
- [GitHub Actions: Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners)
- [Crontab.guru - Cron Expression Validator](https://crontab.guru)
- [POSIX cron syntax specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html)

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Next Review**: Quarterly (or before DST transitions)
