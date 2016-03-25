## Design concerns
What happens when someone feeds a malicious URL? Sandbox the renderer somehow? Use splash in a docker container that runs as a non-privileged user and is destroyed/re-created frequently?

## To do
- Write a couple of views to CRUD monitors
- Implement background worker deque to perform checks
- Create valid urls like 'http://reddit.com' from things like 'reddit.com'. Just require user to enter a valid URL, validate with WTForms.
- Validate URL in WTForm, then clean it up another way later (in model)
- Registration form should email the user their password salt (perhaps base64-encoded) and make them activate their account
- "Check now" button places request at the front of the work queue (so we actually need a deque)
- How to deal with loading 404 pages?
- Don't let a user view another user's monitors

- Where to place code to "email user a notification if their monitor changes state"?

## Ideas
- How to handle "probable" but not exact matches? Match percentage?
- Screenshot should highlight text of concern with a red box

## Challenges
- User feeding malicious URLs e.g. containing malware
- URLs change, pagination