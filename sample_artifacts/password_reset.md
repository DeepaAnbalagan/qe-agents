# Password Reset

A user can reset their password using a token delivered by email.

Requirements:
- A valid token and valid password should reset the password.
- An invalid token must be rejected.
- An expired token must be rejected.
- Passwords shorter than 8 characters must be rejected.
- The reset endpoint is POST /reset-password.

The system should return HTTP 200 for a successful reset and HTTP 400 for invalid requests.

Security note: the token should not be reusable.
