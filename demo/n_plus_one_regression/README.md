# N+1 Query Regression Demo

This intentionally small scenario demonstrates the core SRE Incident Assistant workflow.

## Expected reasoning

Before deployment, the /orders request was around 188 ms.

After deployment:
- latency reaches 4.82 s
- database query count reaches 51 for the request
- the log reports database pool waiting/timeouts
- the latest code contains a database call inside the order loop

The intended RCA is an N+1 database query regression introduced by the latest application change.

## Demo flow

1. Upload incident.log.
2. Provide a GitHub repository containing this scenario.
3. Run the investigation.
4. Review the evidence IDs supporting the RCA.
5. Export the Markdown incident report.