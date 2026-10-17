# aachat GA4 measurement plan

Property 559259561, Web stream measurement ID G-EJ63FSV4FN, timezone Asia/Tokyo. Reader identity: aachat-analytics-reader@trim-mile-511903-c8.iam.gserviceaccount.com, GCP project trim-mile-511903-c8. One production property and one stream only. Property identity setting (Observed) is still unverified.

The project source is `aachat/projects/aachat/aachat-analytics/docs/ga4-analytics-spec.md`. This directory is the reader configuration and analysis procedure; product instrumentation belongs in kensaku63/aachat.

- sign_up: successful new normal human account + personal team transaction, not login. GA-observed registrations, never all DB registrations.
- human_request_accepted: newly accepted direct human Web submission, start/follow_up; retries, Agent, scheduled, Workflow and Ask continuations excluded.
- artifact_viewed: visible content for one continuous second; category document/media only. A reopened display is a new instance.
- All three: surface=web, measurement_version=v1. Counts use eventCount; users use totalUsers for the entire requested period. Do not sum daily unique counts.
- Public pages: screenPageViews and userEngagementDuration / activeUsers (seconds per active user; zero denominator is null). Filter exact published paths and hostnames. Do not restrict engagement to page_view or require surface/version on automatic events.
- Traffic/entry: sessionSourceMedium + landingPage with sessions, separately from page statistics. Keep firstUserSourceMedium separate from sessionSourceMedium on sign_up. direct, (not set), (other) stay distinct.
- Funnel: two human_request_accepted events, closed, indirect, second within 604800s. Both steps apply surface/version parameter filters. Second-step activeUsers / first-step activeUsers, null for zero denominator. This is period-limited first-series completion, not next-day retention or a mature seven-day cohort.

Saved query dates are examples, not the formal collection start. Choose JST inclusive dates after the approved start date, excluding whole revalidation days. Default complete reporting window is 28 days ending JST three days ago. Mark the last two days and today as provisional. Never add user counts from split periods; funnels must use continuous intervals that do not cross excluded days.

Absent consent, unsupported Desktop/CLI/guest/automatic activity, thresholding and delivery failures are not zero activity. No reader access to product DB or MP secret is required.
