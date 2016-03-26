## Performing Checks
Every check_interval period of time, all monitors should be checked
A monitor is stale when its last check occurred more then check_interval ago

Background process (check_daemon.py) does this.
While True:
    Query database for monitors that are due to be checked
    If any monitors are due to be checked:
        perform a check
        store check in database
    Sleep for a minute
For each monitor returned by the query, a check is run and stored in the database


## Design concerns
Would it be smart or dumb to store large (hundreds of KB) base64-encoded images in database? Store images in database for now, move them somewhere else later. Switch to SQLAlchemy-imageattach?
Is HAR better than image?
What happens when someone feeds a malicious URL? Sandbox the renderer somehow? Use splash in a docker container that runs as a non-privileged user and is destroyed/re-created frequently?
Place sensitive stuff (like SECRET_KEY, recaptcha keys, and mail server) in environment variables?

##Tests to write
- Creating duplicate user accounts
- Creating account with password confirm field that doesn't match

## To do
- Remove dryscrape from project
- Automatically prepend "http://" or "https://" in form input for URL
- "help, something is broken" button
- Fix recaptcha validation failure message "The response parameter is missing."
- Don't show recaptcha on edit monitor page
- Don't let user create a duplicate monitor
- Set captcha keys
- Flask should send encrypted email
- let user change password
- reset password function
- "Contact site administrator" form
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
- Write a couple of views to CRUD monitors


## Extended Features
- only accept strong passwords, perhaps use python-zxcvbn
- Atom feed of events

## Ideas
- "URL" field in "Your Monitors" table of dashboard should be shortened to "site" which only shows domain
- Privacy policy. Do we snoop on your monitors or not?
- How to handle "probable" but not exact matches? Match percentage?
- Screenshot should highlight text of concern with a red box
- To create monitor, you drag JavaScript sliders over the text to make a selection

## Challenges
- User feeding malicious URLs e.g. containing malware
- URLs change, pagination