# Table of Contents

- [Description](#description)
- [Running](#running)
- [Testing](#testing)
- [Architecture](#architecture)
- [Scheduled events](#scheduled-events)
  - [Alternatives](#alternatives)
- [Data push improvements](#data-push-improvements)
- [Configuration](#configuration)
- [Error response](#error-response)
- [Logging, tracing](#logging-tracing)
- [JWT token handling](#jwt-token-handling)
- [Databox](#databox)

# Description

* Extract data from `SiStat` and push metrics to `databox`.
* Data comes from three sources, fourth source is calculated from previous ones.
* All four sources are pushed to `databox` as metrics with units.

# Running
Python >=3.10 is used.

Run data parser/pusher using `databox` python API:
```shell
python3 databox_main.py
```

# Testing

Run all the tests that starts with **test**:

```shell
python3 -m unittest discover
```

Run single test:
```shell
python3 -m unittest discover -s test -p 'test_response.py'
```
```shell
python3 -m unittest discover -s test -p 'test_*'
```
```shell
python3 -m unittest discover -s test -p '*helper.py'
```

# Architecture

We want to parallelize as much as possible. First we retrieve data from different source. Each source is retrieved in parallel for greater performance. We use async implementation. Asynchronous implementation uses a single thread and an event loop (It monitors tasks and I/O operations, scheduling tasks to run when they are ready) to manage multiple concurrent operations (we can see it in the logs). Instead of blocking and waiting for an I/O operation to complete, the task yields control back to the event loop. The event loop then handles other tasks until the I/O operation is ready, at which point the original task is resumed. Since we have a lot of I/O operations (Network requests - wait for results) this should be the best way to handle retrieval and push data. Asyncio excels at handling concurrent I/O operations without the overhead of multiple threads.

# Scheduled events

The best way to optimize data retrieval and push is, if service support event based data retrieval. In this case we don't need to schedule the request and push, because we get the data/event as it is provided by th third party service. When data is pushed from third party provider (Web socket, RPC, libp2p, redis pub/sub,..) we can get it, parse it and push it to `databox`.

## Alternatives

1. `Scheduling Libraries`: For more complex scheduling requirements (e.g., running tasks at specific times of day, cron-like schedules), using a dedicated scheduling library is recommended. It provides more advanced features like job persistence, scheduling based on time zones, and more.
2. `Circuit Breaker`: For increased resilience, we could implement a circuit breaker pattern. This would prevent the application from continuously trying to fetch metrics from a failing endpoint, giving the endpoint time to recover.
3. `Exponential Backoff`: In case of repeated failures, implementing an exponential backoff strategy would be beneficial. This means increasing the time between retries exponentially (e.g., 1 second, 2 seconds, 4 seconds, etc.) to avoid overwhelming the failing endpoint.
4. `Rate Limiting`: If the metrics endpoint has rate limits, we should implement rate limiting in application to avoid exceeding those limits.

# Data push improvements

Since network is not 100% relabelled, we can use in-memory data structure before we push to `databox` (this can also be used in python, java, C#,.. databox libraries). We can use Queue data structure - this is more usable when we have streaming or more frequent retrieval of data. If we have error when pushing data to databox, we still have this data in Queue memory - data is not lost, just waits for next iteration to be pushed. We can implement Queue facade that is able to flush (push to databox) inserted elements in configurable batches transparently, while elements are being added from third party sources. This can be configurable:

| Setting                   | Type     | Value   | Description                                                                                                        |
|---------------------------|----------|---------|--------------------------------------------------------------------------------------------------------------------|
| `capacity`                | integer  | `10000` | Queue capacity in max number of stored elements. If queue gets full, new submissions are rejected using `HTTP 429` |
| `batch-size`              | integer  | `100`   | Maximum number of queue elements to flush in a single flush iteration                                              |
| `flush-every`             | integer  | `250`   | flush queue every specified number of inserted elements, this parameter should be `>= batch-size`                  |
| `periodic-flush-interval` | duration | `10s`   | Do periodic queue flush every specified amount of time                                                             |

We can support for async flushes that block (or non block - depends on situation - can be configurable) while `insertion` remains non-blocking.

# Configuration

Configuration can be:
- static (current in the project)
- hot reloadable (for high availability systems)

Fields that are sensitive in configuration must be stored in secure storage (best in the claud). Also, retrieval must be secured or better encrypted using standard encryption/decryption.

# Error response

Error needs to be displayed in standard way (https://developers.databox.com/responses-errors/). Latest standard is `RFC7807`, described here: https://www.rfc-editor.org/rfc/rfc7807.html. It defines Problem detail object where standard error is described. Also timestamp is recommended for additional time monitoring (recommended if we have server to server communication). Important: Errors messages should not be descriptive - this can give hacker attacking vector (check which system is used and find system vulnerability). Instead, descriptive error should be placed in internal logs (or logs from internal systems) that are not visible from 'outsiders'.     

# Logging, tracing

Logging should be 'in one place' especially in modern microservice environment (e.g. `graylog` - https://graylog.org/) where we have multiple instances of same or different services. This simplifies debugging on tha system and between systems (we can use identifier between systems).

Tracing is useful when we want to check for bottlenecks in our system. We can use `jaeger` (distributed tracing platform - https://www.jaegertracing.io/).
Every function/method can be marked as tracing, and then we can check detailed timings. With detail timings we can easily detect where bottlenecks are 

# JWT token handling

Handling JWT (JSON Web Token) expiration and refreshing on a `403 Forbidden` error is a common and important aspect of secure web applications. Here's a typical flow:

1. **Initial Authentication:**
* The user provides their credentials (username/password, etc.).
* The server authenticates the user.
* Upon successful authentication, the server generates a JWT (typically an access token and optionally a refresh token).
* The server sends both tokens back to the client (e.g., in the response body or as HTTP-only cookies).
2. **Subsequent Requests:**
* The client stores the tokens (e.g., in local storage, session storage, or HTTP-only cookies).
* For subsequent requests to protected resources, the client includes the access token in the `Authorization` header (usually as a Bearer token): Authorization: `Bearer <access_token>`.
3. **Access Token Expiration and 403 Error:**
* The access token has a limited lifespan (e.g., 15 minutes, 30 minutes, 1 hour).
* When the access token expires, the server will return a `403 Forbidden` error (or sometimes a 401 Unauthorized, depending on the specific implementation) for requests to protected resources.
4. **Refresh Token Handling (on 403):**
* **Client-Side Intercept/Middleware**: The client-side code (e.g., in a browser using JavaScript, in a mobile app, or in a **backend service**) intercepts the 403 error.
* **Check for Refresh Token**: The client checks if it has a valid refresh token stored.
* **Request New Access Token**: If a refresh token is present, the client makes a request to a dedicated refresh token endpoint on the server. This request typically includes the refresh token (e.g., in the request body or as an HTTP-only `cookie`).
* **Server-Side Refresh Logic**:
  * The server receives the refresh token.
  * It validates the refresh token (signature, expiration, etc.).
  * If the refresh token is valid:
    * The server generates a new access token (and optionally a new refresh token).
    * The server sends the new tokens back to the client.
  * If the refresh token is invalid (expired, revoked, etc.):
    * The server returns an error (e.g., 401 Unauthorized). This usually means the user needs to re-authenticate (go back to step 1).
* **Client Updates Tokens**: The client receives the new tokens and updates its stored tokens.
* **Retry Original Request**: The client retries the original request that resulted in the 403 error, now using the new access token.


### Flow Diagram:
```text
+------------------+     +------------------+     +---------------+     +--------------------+
| Client (Request) | --> | Server (Validate | --> | Server (403)  | --> | Client (Intercept  |
| (Access Token)   |     | Access Token)    |     |               |     | 403, Check Refresh |
+------------------+     +------------------+     +---------------+     +--------------------+
      ^                       |
      |                       V
      |     +-----------------+      +------------------+     +-----------------+
      |     | Client (Refresh | -->  | Server (Validate | --> | Server (New     |
      +-----+ Token Request)  |      | Refresh Token)   |     | Access/Refresh) |
            | (Refresh Token) |      |                  |     +-----------------+
            +-----------------+      +------------------+           ^
                  |                                                 |
                  +-------------------------------------------------+
                        |
                        V
                  +------------------+
                  | Client (Retry    |
                  | Original Request |
                  | (New Access)     |
                  +------------------+
```

* **Refresh Token Storage:** Refresh tokens should be stored securely. HTTP-only cookies are generally the most secure option for browsers. For mobile apps, secure storage mechanisms provided by the operating system should be used.
* **Refresh Token Rotation:** Rotating refresh tokens (issuing a new refresh token each time one is used) adds an extra layer of security. If a refresh token is compromised, it will only be valid for a short time.
* **Revocation:** The server should have a mechanism to revoke refresh tokens (e.g., if a user logs out or their account is compromised).
* **Refresh Token Expiration:** Refresh tokens should also have an expiration time, although it's usually longer than the access token's lifespan.
* **Security:** Protect the refresh token endpoint from abuse (e.g., rate limiting).

# Databox

Databox app:
- `sasostor@gmail.com`

Dashboard:
- https://app.databox.com/datawall/e297a4f03a6b722781e33ed3ecfc92235bb2380675a1e7a
