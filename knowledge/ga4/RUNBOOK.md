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

The helper unsets GOOGLE_CLOUD_QUOTA_PROJECT and REST uses credentials.with_quota_project(None). The provided ADC has no quota project. This matches the successful service-account authentication path: an explicit x-goog-user-project previously caused USER_PROJECT_DENIED. Do not grant serviceusage.services.use merely to work around a header the configuration does not require. If an explicit quota project becomes necessary, obtain authorization and validate that separate permission. Do not edit shared gcloud settings or the ADC.

If human ADC renewal is needed, use gcloud auth application-default login with impersonation and analytics.readonly/cloud-platform scopes, **without the ACCOUNT positional argument**; the human chooses kensaku@aachat.io in the browser. gcloud 589.0.0 failed ID-token verification when ACCOUNT was supplied. Preserve the private credential location and do not ask for the MP secret.

Before regular analysis:

1. Confirm property/timezone, reporting identity in GA, custom dimensions (surface, request_kind, artifact_kind, measurement_version), formal start date, excluded validation dates, and published hostname/path allowlists. `dimensions` and `metadata` must show required custom dimensions before using customEvent filters.
2. Prepare explicit dates in saved queries. Check each dimension/metric combination via Data API `checkCompatibility` (`uv run read.py compatibility --request <REST-body.json>`). Core report request files use MCP snake_case; compatibility/funnel use REST camelCase. In funnel steps, use funnelEventFilter with nested funnelParameterFilterExpression and raw eventParameterName; do not copy Core customEvent field filters into funnelFieldFilter.
3. Request stable order on every dimension. Advance offset by returned row count until row_count is covered. Stop at 100 total API calls for one report; reaching the bound means incomplete. Never infer raw completeness or recovery of (other) from pagination. Zero returned rows with a larger row_count is an incomplete read.
4. Preserve request, retrieval time and response in a private report location. Return property, JST period, Web/consent coverage, filters, identity (or unverified), quota class, and quality metadata. Distinguish absent fields from false: sampling_metadatas, subject_to_thresholding, data_loss_from_other_row, data_truncation_reasons, schema_restriction_response, empty_reason. The MCP/protobuf conversion may materialize default fields; report that fact rather than assuming all fields were present on the wire.
5. State delivery status unverified unless the responsible operator supplies the operational record. Do not retrieve individual product identifiers. Delete non-identifying saved reports after 14 months.

Before production enablement the product operator must configure the MP secret, consent ownership, GA settings, validation browser/account, internal exclusions, monitoring retention/notifications, deletion owner and follow-up process. The reader cannot set these with Viewer. Deletion requests use Admin API submitUserDeletion under a separate edit identity; request acceptance is not deletion completion. The reader has no deletion authority. Track the responsible owner, receipt time, follow-up date and official completion evidence outside this read-only account before collection begins.

Official references: https://github.com/googleanalytics/google-analytics-mcp and https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1alpha/properties/runFunnelReport .
