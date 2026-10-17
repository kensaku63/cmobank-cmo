# Connection evidence — 2026-10-17

Executed from cmobank-cmo.kensaku63 Session f5477d3e-973c-41c3-b8a8-c39784efabc9 on the user Mac. No Google settings or collection writes were made.

- Official MCP stdio initialization + tools/call succeeded at fixed commit 75c0e1be8322e5eaa5c2e3ef7e79cf4760060f9a.
- get_property_details at 03:35:31 UTC: properties/559259561, display_name aachat, time_zone Asia/Tokyo.
- get_custom_dimensions_and_metrics at 03:35:34 UTC: both arrays empty. Required custom dimensions have not been confirmed present.
- run_report at 03:35:36 UTC, JST inclusive 2026-10-10..16, eventName/eventCount, eventName ordering, offset 0, limit 10000, no event/surface filter: rows=[], row_count=0. Core quota consumed 1; returned daily remaining 199898. metadata: data_loss_from_other_row=false, sampling_metadatas=[], data_truncation_reasons=[]; subject_to_thresholding/schema_restriction_response/empty_reason absent. Reporting identity and delivery state unverified. This is a connectivity query before the formal start, not all registrations=0.
- REST CLI getMetadata succeeded at 03:38:27 UTC. This preserves raw JSON metadata; no customEvent:surface/measurement_version entries were present.
- Timed funnel CLI was actually called. Core customEvent filters in funnelFieldFilter failed HTTP 400 unsupported field. Switched to the official nested funnelEventFilter/funnelParameterFilterExpression with raw eventParameterName and preserved 604800s. That request failed HTTP 400 INVALID_ARGUMENT: measurement_version is not supported in this property. No filter was removed to manufacture a result. Rerun after required GA metadata/events become available. Six-day/exact-seven-day/seven-day-plus fixtures and GA exploration comparison remain unexecuted.
- No quota-project header used; no additional IAM grants. The current ADC has no quota_project_id. Credentials and tokens were never printed or committed.

The Agent repository MCP configuration is separate evidence from runtime tool injection. Direct stdio execution in this Session is proven; the next Session's injected tool list is not yet verified. OS-level isolation from other Agents under the same macOS account is not achieved. MP validation, actual collection and general-user enablement were not executed.
