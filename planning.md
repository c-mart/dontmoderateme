## Design concerns
What happens when someone feeds a malicious URL? Sandbox the renderer somehow? Use splash in a docker container that runs as a non-privileged user and is destroyed/re-created frequently?

Things user may want to do:
- View recent events (and their screenshots)
- Manage monitors (view, create new, edit existing, delete)
- View all events and checks for a monitor

Dashboard should show recent events, recently created monitors, and their status

##Tests to write
- Creating duplicate user accounts
- Creating account with password confirm field that doesn't match

## To do
- Automatically prepend "http://" or "https://" in form input for URL
- "help, something is broken" button
- Fix recaptcha validation failure "The response parameter is missing."
- Don't show recaptcha on edit monitor page
- Don't let user create a duplicate monitor
- Set captcha keys
- Flask should send encrypted email
- let user change password
- reset password function
- "Contact site administrator" form
- Write a couple of views to CRUD monitors
- Implement background worker deque to perform checks
- Create valid urls like 'http://reddit.com' from things like 'reddit.com'. Just require user to enter a valid URL, validate with WTForms.
- "Check now" button places request at the front of the work queue (so we actually need a deque)
- How to deal with loading 404 pages?
- Don't let a user view another user's monitors, checks, or screenshots

- Where to place code to "email user a notification if their monitor changes state"?

## Done
- captcha on registration page
- Re-send activation email if user tries to log into an account that is not activated
- Registration form should email the user their password salt (perhaps base64-encoded) and make them activate their account

## Extended Features
- only accept strong passwords, perhaps use python-zxcvbn
- Atom feed of events

## Ideas
- Privacy policy. Do we snoop on your monitors or not?
- How to handle "probable" but not exact matches? Match percentage?
- Screenshot should highlight text of concern with a red box
- To create monitor, you drag JavaScript sliders over the text to make a selection

## Challenges
- User feeding malicious URLs e.g. containing malware
- URLs change, pagination