# URL_Checker

# Overview
* A web app made using Flask/Python/HTML/CSS (Bootstrap) /JavaScript/SQLALchemy where users can check the safety of URLs they believe to be suspicious.
* Users don't have to first register and login to use the service, but if they do, they will receive emails.
* Makes use of Google’s Safe Browsing API, which returns an empty json response for safe urls, otherwise, a json response detailing threat type/level 
* After submitting a URL to be checked, users can see: The URLs that have been searched, how many times they have been searched, who the URL was searched by, the most recent search date * and time of the URL in a table.

# Use Cases
* Explore the safety of URLs you are suspicious of
* See how many other people come across the same URLs
* See what people in your company/others are browsing (a random username is generated for each user at this point in time for data privacy reasons)
* See when people are browsing the URL

# Functional Requirements
* User Registration and Authentication
* URL Safety Checking
* Error Handling and flashed messages
* API calling and data retrieval
* Database storage with SQLAlchemy

# Non-Functional Requirements
* Performance (response time from API call is fast)
* Security - user passwords etc. mananged by werkzeug security module
* Multiple devices responseiveness (Mobile, Tablet etc.) achieved through Bootstrap

