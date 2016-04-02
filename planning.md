I have a minimum functional prototype. What now?
- Write tests

## Design concerns
- If user associated with a monitor is manually deleted from DB, or monitor associated with a check is deleted from DB, things go wrong. Delete all "child" objects when deleting user or monitor.
- Is HAR better than image?
- What happens when someone feeds a malicious URL? Sandbox the renderer somehow? Use splash in a docker container that runs as a non-privileged user and is destroyed/re-created frequently?
- Place sensitive stuff (like SECRET_KEY, recaptcha keys, and mail server) in environment variables?

## Tests to write
- Creating user account with duplicate email address
- Trying to view someone else's monitor/check
- Trying to log in with wrong password
- Password reset workflow

## To do - features/usability
- Get Gmail to not mark my messages as spam
- account settings page so we can set time zone and change our own password
- "To be sure that you receive notifications, add notify@dontmoderate.me to your trusted senders list."
- "Report problem"/"contact site owner" button, view with form that emails me
- Forward info@dontmoderate.me to me
- Learn user's time zone and show timestamps in it
- Immediately check monitor after creation
- Automatically prepend "http://" or "https://" in form input for URL
- Fix recaptcha validation failure message "The response parameter is missing."
- Don't show recaptcha on edit monitor page
- Don't let user create a duplicate monitor
- "Check now" button places request at the front of the work queue (so we actually need a deque)
- How to deal with Splash loading 404 pages? Notify user page is missing?

## To do - security
- Publish a canary
- Postfix should be configured to send TLS email
- Consider everything that application could send via email. Don't send anything sensitive via email.
- Set captcha keys
- Splash should use HTTPS if the web server supports it
- Don't let a user view another user's monitors, checks, or screenshots

## To do - refactor/cleanup
- testing should happen against a postresql database, prob running in a container
- check_daemon logging should report full stack trace
- Consider using http://pytest-flask.readthedocs.org/en/latest/features.html for tests
- Remove dryscrape from project
- Refactor "screenshot" to "image"
- Implement logging for check_daemon

## Done
- Email user when event occurs, include link to monitor
- captcha on registration page
- Re-send activation email if user tries to log into an account that is not activated
- Registration form should email the user their password salt (perhaps base64-encoded) and make them activate their account
- Write a couple of views to CRUD monitors
- Let user reset password. reset_tokens model with random token and user ID. Email user token, if they can provide token to web site then they can reset password.

## Extended Features
- only accept strong passwords, perhaps use python-zxcvbn
- private Atom feed of events for a monitor
- To create monitor, you drag JavaScript sliders over the text to make a selection
- How to handle "probable" but not exact matches? Match percentage?

## Ideas
- Limit # of monitors
- Monitors are tripped and then must be reset, like a circuit breaker
- Store the last few screenshots
- "URL" field in "Your Monitors" table of dashboard should be shortened to "site" which only shows domain
- Privacy policy and terms of use. Do we snoop on your monitors or not?
- Monitor someone's twitter feed every time they tweet, if they delete a tweet we still have it
- Monitor can have a range of possible statuses rather than binary up/down which may be more informative to user, e.g. page not found, site is down, server not found. For now, binary up/down. Page is down if 404.