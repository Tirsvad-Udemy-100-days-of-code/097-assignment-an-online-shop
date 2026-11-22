**English** · [Dansk](Step-03-Registration-and-Login-da) · [Bahasa Malaysia](Step-03-Registration-and-Login-ms)

# Step 3: Registration and login

Visitors can now register, sign in and sign out, and the shop has an admin role.

![Step 3](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/raw/branch/main/docs/screenshots/step-03.png)

## Password hashing

A password is never stored. The shop stores a salted `scrypt` hash made with `hashlib.scrypt`, in the form `scrypt$n$r$p$salt$key`. The cost parameters travel inside the hash, so they can be raised later without breaking old accounts. Checking a password compares the hashes with `hmac.compare_digest`, which takes the same time whether or not they match. When the email is unknown the shop still hashes the password against a dummy hash, and both failures show one message, so an attacker cannot tell which part was wrong.

## Sessions

Flask's signed session cookie keeps the user signed in. It is `HttpOnly` so scripts cannot read it, `SameSite=Lax`, and it expires after seven days. The key comes from `SHOP_SECRET_KEY`. Login clears the old session first, so a session id set before login is never reused (session fixation).

## CSRF

Every form carries a hidden `csrf_token`. A request that changes state (POST, PUT, PATCH, DELETE) without the matching token is refused with 403. Logout is a POST for the same reason. After login the shop only follows a `next` address that is a local path, so a link cannot send a user to another site.

## Admin

The admin account is created at start from `SHOP_ADMIN_EMAIL` and `SHOP_ADMIN_PASSWORD`; there is no default password in the code. `/admin` sends visitors who are not signed in to the login page, answers 403 to customers and shows the page to the admin.

## What I learned

- Hash with a slow, salted function and compare in constant time.
- The same error for every failed login gives an attacker less to work with.
- A security rule written as one guard that every request passes is easier to test than a check in each page.
