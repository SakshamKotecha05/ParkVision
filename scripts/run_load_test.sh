#!/usr/bin/env bash
# scripts/run_load_test.sh — start the local API, wait healthy, run locust.
# Target is ALWAYS localhost — never a public URL.
set -uo pipefail

REPO_ROOT="/Users/sak/Desktop/MSI WORK/GriDLocK/Round2_gsd"
cd "${REPO_ROOT}" || { echo "FATAL: cannot cd ${REPO_ROOT}" >&2; exit 1; }

API_PORT=8000
UVICORN_PID=""
cleanup() {
  if [ -n "${UVICORN_PID}" ] && kill -0 "${UVICORN_PID}" 2>/dev/null; then
    kill -TERM "${UVICORN_PID}" 2>/dev/null; wait "${UVICORN_PID}" 2>/dev/null
  fi
}
trap cleanup EXIT INT TERM

mkdir -p artifacts
echo "Starting api.main:app on :${API_PORT}..."
/opt/anaconda3/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port "${API_PORT}" \
  > artifacts/run_load_test_uvicorn.log 2>&1 &
UVICORN_PID=$!

ACTIVE_HOST=""
for i in $(seq 1 20); do
  if ! kill -0 "${UVICORN_PID}" 2>/dev/null; then
    echo "FATAL: uvicorn died early. See artifacts/run_load_test_uvicorn.log" >&2; exit 1
  fi
  CODE=$(curl -s -o /tmp/pv_health.json -w "%{http_code}" "http://localhost:${API_PORT}/health" 2>/dev/null)
  if [ "${CODE}" = "200" ] && grep -q '"artifacts_loaded":[ ]*true' /tmp/pv_health.json 2>/dev/null; then
    ACTIVE_HOST="http://localhost:${API_PORT}"; echo "API healthy (try ${i})"; break
  fi
  sleep 0.5
done
[ -z "${ACTIVE_HOST}" ] && { echo "FATAL: API never healthy." >&2; exit 1; }

echo "Running locust headless: -u 50 -r 1.67 -t 90s against ${ACTIVE_HOST}"
/opt/anaconda3/bin/python -m locust -f locustfile.py --headless \
  --host "${ACTIVE_HOST}" -u 50 -r 1.67 -t 90s --csv artifacts/load_test_raw
LOCUST_EXIT=$?

if [ -f artifacts/load_test_results.json ]; then
  echo ""; echo "=== artifacts/load_test_results.json ==="
  /opt/anaconda3/bin/python -c "
import json
r = json.load(open('artifacts/load_test_results.json'))
a = r['aggregate']
print(f\"Aggregate: {a['num_requests']} req, {a['rps']:.2f} rps, p50={a['p50_ms']}ms, p95={a['p95_ms']}ms, fail={a['fail_ratio']:.4f}\")
for n, e in r['by_endpoint'].items():
    print(f\"  {n}: {e['rps']:.2f} rps, p50={e['p50_ms']}ms, p95={e['p95_ms']}ms, n={e['num_requests']}\")
"
fi
exit "${LOCUST_EXIT}"
