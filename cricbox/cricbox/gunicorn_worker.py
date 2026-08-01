"""Custom gunicorn thread worker that bounds the response-write phase.

gunicorn's gthread worker (currently pinned to 26.0.0 — see pyproject.toml)
protects the *read* side of a connection with real timeouts
(DEFAULT_WORKER_DATA_TIMEOUT while waiting for a client to send data, a
bounded keepalive-body drain, etc.) but the *write* side has none:
gunicorn/util.py's write() ultimately calls sock.sendall(data) on a socket
that was set fully blocking (conn.sock.setblocking(True)) with no timeout
at all.

If a client's TCP connection goes half-dead mid-response (phone locks,
drops off wifi, a NAT/load balancer silently drops the connection),
sendall() can block until the kernel's own TCP retransmission timeout
gives up — which is minutes, not seconds. That's what eventually surfaces
as `TimeoutError: [Errno 110] Connection timed out`. Until then, the
worker thread handling that connection is unusable. With
`--workers 2 --threads 4` (8 total request-handling slots), it only takes
8 simultaneously-stalled clients to make the whole app unresponsive — and
gunicorn's own `--timeout` arbiter watchdog can't catch it, because the
dispatch loop that feeds the watchdog's heartbeat keeps running fine even
while individual worker threads are stuck.

This worker closes that gap by putting an explicit timeout on the socket
before handling each request. A stalled write then raises a normal,
catchable timeout instead of blocking indefinitely. gunicorn's existing
`ThreadWorker.handle()` already treats any exception from
`handle_request()` as "close this connection and free the thread" (see
its `except OSError` / `except Exception` handling), so no other
behaviour changes — a stalled client just gets disconnected instead of
tying up a thread forever.
"""

import os

from gunicorn.workers.gthread import ThreadWorker

# How long a single request's response write is allowed to stall before
# the connection is dropped and the thread freed. Generous enough not to
# punish a genuinely slow (but alive) client on a big page/asset; short
# enough that a handful of dead connections can't exhaust the thread pool.
# Override with GUNICORN_RESPONSE_TIMEOUT if needed.
RESPONSE_TIMEOUT = float(os.environ.get("GUNICORN_RESPONSE_TIMEOUT", "10"))


class TimeoutThreadWorker(ThreadWorker):
    """gthread worker with a bounded response-write timeout."""

    def handle_request(self, req, conn):
        conn.sock.settimeout(RESPONSE_TIMEOUT)
        return super().handle_request(req, conn)
