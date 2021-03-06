**Restart docker container automatically on boot: https://docs.docker.com/engine/reference/run/#restart-policies-restart**

Testing options:
- Continue trying to get pytest to work on my own. probably have trouble with application context and request context
- Try getting pytest-flask to work
- Switch back to unittest, which worked well for smog, also uses XUnit style applicable to other languages

## Design concerns
- Deploy playbook should run database migration upgrade at the end to apply any schema changes (or should I do that manually?)
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
- Let users change their own password
- Recent Events table shows "Monitor Created" at the bottom even when that is not a recent event. Move this timestamp to another part of the page?
- Will a sender name keep Gmail from marking my stuff as spam?
- View all events and checks
- "Monitor edited" should be an event.
- Immediately check monitor after creation
- Fix recaptcha validation failure message "The response parameter is missing."
- Don't let user create a duplicate monitor
- How to deal with Splash loading 404 pages? Notify user page is missing?

## To do - security
- Publish a canary
- Splash should use HTTPS if the web server supports it
- Programatically enforce a user's ability to only view his/her own monitors, checks, screenshots

## To do - refactor/cleanup
- Consider using http://pytest-flask.readthedocs.org/en/latest/features.html for tests
- Remove dryscrape from project
- Refactor "screenshot" to "image"
- One PostgreSQL container for both dev and testing databases

## Done
- When user tries to access their monitor and isn't logged in, direct them to login page, then to their monitor
- Postfix should be configured to send TLS email
- Use TLS and dkim to send email
- Piwik not working. Fix piwik
- Check_daemon not checking new monitors very quickly
- View for all events and checks, either across all monitors or for a specific monitor
- Redesign dashboard
- Restrict number of monitors user can create
- Implement logging for check_daemon
- "To be sure that you receive notifications, add notify@dontmoderate.me to your trusted senders list."
- Don't bother people with recaptcha when editing existing monitors or creating new ones. Add recaptcha back in if I have a spam/bot problem.
- Pretty up/down icons
- Forward info@dontmoderate.me to me
- testing should happen against a postresql database, prob running in a container
- "Report problem"/"contact site owner" button, view with form that emails me
- Email user when event occurs, include link to monitor
- captcha on registration page
- Re-send activation email if user tries to log into an account that is not activated
- Registration form should email the user their password salt (perhaps base64-encoded) and make them activate their account
- Write a couple of views to CRUD monitors
- Let user reset password. reset_tokens model with random token and user ID. Email user token, if they can provide token to web site then they can reset password.
- Deleting monitors should delete checks, it does in test but not in production
- Automatically prepend "http://" or "https://" in form input for URL
- check_daemon logging should report full stack trace
- Set captcha keys
- Learn user's time zone and show timestamps in it

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