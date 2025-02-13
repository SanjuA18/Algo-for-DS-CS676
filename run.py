from test import rate_url_validity

user_prompt = "I have just been on an international flight, can I come back home to hold my 1-month-old newborn?"
url_to_check = "https://www.bhtp.com/blog/when-safe-to-travel-with-newborn/"

result = rate_url_validity(user_prompt, url_to_check)
print(result)