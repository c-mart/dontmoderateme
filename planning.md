I have a minimum functional prototype. What now?
- Write tests
- Deploy. We need four containers: flask app, check_daemon, splash, and postgres. Our config should live somewhere private. We also need to learn to use Docker Compose.

Password Reset
- Model to store tokens with user IDs
- Button on login page to reset password
- View to request password reset, sends email
- View to process password reset, forwards to prompt user to change password

...so I also need a change password view

## Design concerns
- Do we need to daemonize check_daemon if it will run in a docker container, or not?
- Would it be smart or dumb to store large (hundreds of KB) base64-encoded images in database? Store images in database for now, move them somewhere else later. Switch to SQLAlchemy-imageattach?
- Is HAR better than image?
- What happens when someone feeds a malicious URL? Sandbox the renderer somehow? Use splash in a docker container that runs as a non-privileged user and is destroyed/re-created frequently?
- Place sensitive stuff (like SECRET_KEY, recaptcha keys, and mail server) in environment variables?

## Tests to write
- Creating duplicate user accounts
- Creating account with password confirm field that doesn't match

## To do - features/usability
- "To be sure that you receive notifications, add notify@dontmoderate.me to your trusted senders list."
- "Report problem"/"contact site owner" button, view with form that emails me
- Let user reset password. reset_tokens model with random token and user ID. Email user token, if they can provide token to web site then they can reset password.
- Learn user's time zone and show timestamps in it
- Immediately check monitor after creation
- Automatically prepend "http://" or "https://" in form input for URL
- Fix recaptcha validation failure message "The response parameter is missing."
- Don't show recaptcha on edit monitor page
- Don't let user create a duplicate monitor
- "Check now" button places request at the front of the work queue (so we actually need a deque)
- How to deal with Splash loading 404 pages? Notify user page is missing?

## To do - security
- Set captcha keys
- Flask should send TLS-encrypted email if email server supports it
- Splash should use HTTPS if the web server supports it
- Don't let a user view another user's monitors, checks, or screenshots

## To do - refactor/cleanup
- Remove dryscrape from project
- Refactor "screenshot" to "image"
- Implement logging for check_daemon

## Done
- Email user when event occurs, include link to monitor
- captcha on registration page
- Re-send activation email if user tries to log into an account that is not activated
- Registration form should email the user their password salt (perhaps base64-encoded) and make them activate their account
- Write a couple of views to CRUD monitors

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