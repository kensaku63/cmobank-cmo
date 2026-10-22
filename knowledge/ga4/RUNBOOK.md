# GA reader on this Mac

This Agent's repository supplies `.agents/plugins/ga4-reader/mcp.json`. It launches the unmodified official googleanalytics/google-analytics-mcp at commit `75c0e1be8322e5eaa5c2e3ef7e79cf4760060f9a` over stdio. The source of the local configuration package is `plugins/ga4-reader`. No host-wide MCP registration is needed. A running Session's tool inventory is not hot-reloaded by committing this file: the next Session must confirm the injected tool list. During the current Session, `read.py` starts and calls the same official MCP through its stdio protocol.

The default ADC location is `$HOME/.config/aachat-ga-reader/application_default_credentials.json`. `GOOGLE_APPLICATION_CREDENTIALS` can override the path in this Agent's child process. Never display/copy/commit the file, token, authorization headers, source credentials, or MP API secret. The current file is impersonated-service-account ADC, mode 0600. This is **not OS isolation between Agents sharing the same macOS user**. A separate OS identity or isolated runtime with a private credential mount is required to satisfy that acceptance condition; the repository configuration only limits which Agent is configured to launch this MCP.

`uv` is the declared runtime dependency. From this directory:

```sh
uv run read.py property
uv run read.py dimensions
uv run read.py report --request queries/connection-report.json
uv run read.py metadata
uv run read.py funnel --request queries/seven-day-funnel.json --dry-run
uv run read.py funnel --request queries/seven-day-funnel.json
```

Property is fixed in the reader; do not select the first account search result. Normal reports use official MCP `run_report`, not a replacement MCP. The pinned MCP does not preserve the funnel time constraint, so funnels use Data API REST. REST preserves response fields unknown to an SDK; the exact request is echoed with the result for comparison. A successful HTTP request with empty rows is a connection check, not instrumentation acceptance. `failed` exits nonzero with null data. No unbounded retries occur.

Both MCP `isError=true` and a top-level `error` in any JSON text content or structuredContent fail closed with exit 1, empty stdout and `status=failed,data=null` on stderr. The official server's observed 503 reauthentication failure uses `isError=false` with JSON text `error`; exit 0 from older reader versions was not evidence of success. Raw upstream error text is not echoed. Successful empty rows remain unchanged and must not be confused with a failed read. Offline regression from the Agent repository root: `python3 -m unittest discover -s knowledge/ga4 -p test_read.py -v`.

The helper unsets GOOGLE_CLOUD_QUOTA_PROJECT and REST uses credentials.with_quota_project(None). The provided ADC has no quota project. This matches the successful service-account authentication path: an explicit x-goog-user-project previously caused USER_PROJECT_DENIED. Do not grant serviceusage.services.use merely to work around a header the configuration does not require. If an explicit quota project becomes necessary, obtain authorization and validate that separate permission. Do not edit shared gcloud settings or the ADC.

If human ADC renewal is needed, use gcloud auth application-default login with impersonation and analytics.readonly/cloud-platform scopes, **without the ACCOUNT positional argument**; the human chooses kensaku@aachat.io in the browser. gcloud 589.0.0 failed ID-token verification when ACCOUNT was supplied. Preserve the private credential location and do not ask for the MP secret.

The human runs the following on the reader Mac and completes browser login/consent; ask only for completion status, never an authorization code, URL, token or credential content. `CLOUDSDK_CONFIG` is command-local, so the shared gcloud configuration is unchanged. Do not replace the service account with the human's direct GA access or add edit scope.

```sh
(umask 077
 env -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_QUOTA_PROJECT CLOUDSDK_CONFIG="$HOME/.config/aachat-ga-reader" gcloud auth application-default login --impersonate-service-account=aachat-analytics-reader@trim-mile-511903-c8.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform --disable-quota-project
)
```

After renewal, verify the impersonated service-account identity, ADC mode 0600 and absence of quota project without printing credentials. Re-read property (Asia/Tokyo), dimensions and metadata before reports. Browser login completion alone is not reader recovery. Current collection dates, excluded days and the recovery evidence belong to the Project's `ga4-operations.md` and `ga4-reader-recovery-20261021.md`; do not infer current availability from historical connection evidence.

Before regular analysis:

1. Confirm property/timezone, reporting identity in GA, custom dimensions (surface, request_kind, artifact_kind, measurement_version), formal start date, excluded validation dates, and published hostname/path allowlists. `dimensions` and `metadata` must show required custom dimensions before using customEvent filters.
2. Prepare explicit dates in saved queries. Check each dimension/metric combination via Data API `checkCompatibility` (`uv run read.py compatibility --request <REST-body.json>`). Core report request files use MCP snake_case; compatibility/funnel use REST camelCase. In funnel steps, use funnelEventFilter with nested funnelParameterFilterExpression and raw eventParameterName; do not copy Core customEvent field filters into funnelFieldFilter.
3. Request stable order on every dimension. Advance offset by returned row count until row_count is covered. Stop at 100 total API calls for one report; reaching the bound means incomplete. Never infer raw completeness or recovery of (other) from pagination. Zero returned rows with a larger row_count is an incomplete read.
4. Preserve request, retrieval time and response in a private report location. Return property, JST period, Web/consent coverage, filters, identity (or unverified), quota class, and quality metadata. Distinguish absent fields from false: sampling_metadatas, subject_to_thresholding, data_loss_from_other_row, data_truncation_reasons, schema_restriction_response, empty_reason. The MCP/protobuf conversion may materialize default fields; report that fact rather than assuming all fields were present on the wire.
5. State delivery status unverified unless the responsible operator supplies the operational record. Do not retrieve individual product identifiers. Delete non-identifying saved reports after 14 months.

Before production enablement the product operator must configure the MP secret, consent ownership, GA settings, validation browser/account, internal exclusions, monitoring retention/notifications, deletion owner and follow-up process. The reader cannot set these with Viewer. Deletion requests use Admin API submitUserDeletion under a separate edit identity; request acceptance is not deletion completion. The reader has no deletion authority. Track the responsible owner, receipt time, follow-up date and official completion evidence outside this read-only account before collection begins.

Official references: https://github.com/googleanalytics/google-analytics-mcp and https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1alpha/properties/runFunnelReport .

## Growth read requests and funnel response limits

`queries/growth-{journey,content,signup,first-request,first-result}.json` are verified request examples for the partial validation interval 2026-10-21 19:20–19:28 JST, not formal reporting dates. They reuse Core run_report with event/surface/version filters. The minute filter uses an exact in-list on dateHourMinute; BetweenFilter is rejected for dimensions. Replace dates AND minute values for a new partial interval; use whole days only after the Project's collection/acceptance conditions are met. Run `report --request <file>` after checking the same dimensions/metrics/filter through REST checkCompatibility. All five examples returned normal empty rows; that does not establish zero activity, parameter receipt, or instrumentation acceptance.

The verified duration metric is `customEvent:elapsed_seconds` (sum in seconds). A request also including `averageCustomEvent:elapsed_seconds` and `countCustomEvent:elapsed_seconds` returned HTTP 400 even though checkCompatibility reported COMPATIBLE. Do not use that combination as a working query or turn its failure into zero. Do not divide duration sum by all events to infer a mean when duration availability is unknown. Current evidence and start-date prerequisites live in Project `ga4-reader-recovery-20261021.md`.

The observed v1alpha funnel HTTP body itself repeats table metric headers (8 headers/4 values) and visualization headers (2 activeUsers headers/1 value). Decode/save round-trip preserves it; do not deduplicate or zip/truncate the table. The official funnel visualization has only one metric, activeUsers. For the existing standard two-step request, its values can be reported only after verifying: dimensionHeaders is solely funnelStepName; every metric header is activeUsers/TYPE_INTEGER; exactly two unique expected step names; each row has exactly one dimension and one nonnegative integer metric value; step2 <= step1. Compute the defined period-limited completion as visualization step2/step1, null for zero denominator. Preserve the original response and flag header redundancy. Table completion/abandonment metrics remain withheld. If any invariant fails, withhold the funnel result rather than guessing column positions. Empty metadata stays quality information not obtained. This is not mature cohort retention.

Semantic reference: https://developers.google.com/analytics/devguides/reporting/data/v1/funnels (Funnel visualization and raw response). The reader remains a raw-response adapter; this bounded interpretation does not modify Google's payload.

## Dashboard sync (Project Database + HTML)

`dashboard_sync.py` stores GA reports (definitions in `dashboard_definitions.json`), the product daily aggregate artifact (kensaku63/aachat `analytics-daily-usage.yml`, downloaded with `gh`) and operator growth JSON into the aachat-analytics Project Database. Contract: Project `docs/analytics-database-dashboard-spec.md`; operations: `docs/ga4-operations.md`. A Project Trigger runs `uv run dashboard_sync.py run --project-root <Project root>` daily at 09:00 JST; use `${AA_WS_DIR:-$PWD}` because Trigger Sessions may lack AA_WS_DIR. GA end date is JST today minus 3; before the formal start there is nothing to fetch and 0 runs is normal. On reader failure it records `ga_unavailable` runs instead of zeros. Changing a report's meaning requires a new `definition_version`; the sync refuses a changed hash under the same version. Project DB migrations cannot create VIEWs, so the HTML selects the latest `ok/empty` run per window_key with a CTE. Offline tests: `python3 -m unittest discover -s knowledge/ga4 -p 'test_*.py'`.

To change whether a report counts as formal, append a row to `analytics_coverage` (never edit or delete earlier rows); the latest `recorded_at` covering a day wins and the HTML re-evaluates it on every load. Example used on 2026-10-22 for P01–P03 after the owner confirmed the external audience (Ask ec088ebe): one INSERT per report/variant with `state='accepted'`, `valid_from` = first covered date, a reason code and the evidence ref. Use `--params` for Japanese text; a multi-row `--sql` literal insert with Japanese notes was rejected while single-row parameterized inserts succeeded.
