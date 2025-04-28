import time
import asyncio

async def job_apply(user_data, job_query, num_applies):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from dotenv import load_dotenv
    import generators.resume_generate as resume_generate
    import generators.cover_letter_generate as cover_letter_generate
    import os
    import time
    import shutil

    # Load credentials
    load_dotenv()
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')

    # Setup Chrome WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def upload_file(file_path, file_type):
        """Uploads a file if the respective section is found."""
        try:
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-hook='s3-upload-input']"))
            )
            file_input.send_keys(file_path)
            print(f"Uploaded {file_type}")
            time.sleep(5)
        except TimeoutException:
            print(f"{file_type} upload input not found, skipping.")
        except Exception as e:
            print(f"Error uploading {file_type}: {e}")

    # Track company occurrences
    company_count = {}

    try:
        driver.get("https://app.joinhandshake.com/login")

        # Login process
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email-address-identifier")))
        email_input.send_keys(EMAIL)
        email_input.send_keys(Keys.RETURN)

        sso_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'sso-button')]"))
        )
        sso_button.click()

        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_input = driver.find_element(By.ID, "password")

        email_input.send_keys(EMAIL)
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)

        print("Login successful! Please enter your PIN manually within 15 seconds.")
        time.sleep(10)

        try:
            trust_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "trust-browser-button"))
            )
            trust_button.click()
            print("Clicked 'Yes, this is my device' button.")
        except Exception:
            print("No 'Yes, this is my device' button found.")

        # Navigate to job postings
        WebDriverWait(driver, 10).until(EC.url_contains("uconn.joinhandshake.com"))
        driver.get("https://uconn.joinhandshake.com/stu/postings")
        time.sleep(2)
        driver.get(f"https://app.joinhandshake.com/stu/postings?page=1&per_page={num_applies}&query={job_query.replace(' ', '%20')}")

        applied_count = 0
        jobs_applied = []
        postings = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@data-hook='jobs-card']"))
        )

        time.sleep(5)

        for posting in postings:
            if applied_count >= num_applies:
                break

            job_link = posting.get_attribute("href")
            driver.execute_script("window.open(arguments[0]);", job_link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(5)

            # Extract job details
            posting_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-content"]/div[2]/div/div[1]/div/div/div/div[1]/h1'))).text

            posting_company = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-content"]/div[2]/div/div[1]/div/div/div/div[1]/div[1]/div/a[1]'))).text

            posting_headline = f"{posting_name} @ {posting_company}"
            print(posting_headline)

            try:
                # Click "More" button to view full description
                more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-to-content"]/div[2]/div/div[1]/div/div/div/div[2]/div[3]/div/div/div/button'))
                )
                more_button.click()
                print("Clicked 'More' button to view full description.")
                time.sleep(2)
            except Exception as e:
                print(f"Failed to click 'More' button: {e}")

            posting_description = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-content"]/div[2]/div/div[1]/div/div/div/div[2]/div[3]'))
            ).text

            # Apply button
            try:
                apply_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-to-content"]/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div/div/button[2]'))
                )
                if apply_btn.text.lower() == "apply externally":
                    print(f"Skipping external application: {posting_headline}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                else:
                    apply_btn.click()
                    time.sleep(6)
            except Exception:
                print(f"Error during applying for the job: {posting_headline}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            time.sleep(2)

            # Define paths for documents
            company_count[posting_company] = company_count.get(posting_company, 0) + 1
            count_suffix = f"_{company_count[posting_company]}" if company_count[posting_company] > 1 else ""

            resume_path = f"C:\\Users\\allen\\Resumes AI\\Resume_{posting_company}{count_suffix}.docx"
            cover_letter_path = f"C:\\Users\\allen\\Cover Letters AI\\Cover_Letter_{posting_company}{count_suffix}.docx"

            original_transcript_path = f"C:\\Users\\allen\\Resume Trial\\UCONN First Sem Unoffical Transcript 2.pdf"
            transcript_path = f"C:\\Users\\allen\\Transcripts AI\\Transcript_{posting_company}{count_suffix}.pdf"

            # Save a copy of the transcript to the new location
            shutil.copy(original_transcript_path, transcript_path)

            # Generate Resume & Cover Letter
            await resume_generate.generate_resume(posting_description, resume_path, user_data)
            await cover_letter_generate.create_cover_letter(user_data, posting_name, posting_company, cover_letter_path)
            time.sleep(20)

            # Upload files if required
            try:
                headings = driver.find_elements(By.TAG_NAME, "h3")

                if any("Attach your resume" in h.text for h in headings):
                    print("Uploading resume...")
                    upload_file(resume_path, "Resume")
                if any("Attach your cover letter" in h.text for h in headings):
                    print("Uploading cover letter...")
                    upload_file(cover_letter_path, "Cover Letter")
                if any("Attach your transcript" or "Attach other required documents" in h.text for h in headings):
                    print("Uploading transcript...")
                    upload_file(transcript_path, "Transcript")

            except Exception as e:
                print(f"Error checking upload sections: {e}")

            time.sleep(10)

            # Submit application
            try:
                submit_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/reach-portal/div[3]/div/div/div/span/form/div[2]/div/span/div/button"))
                )
                submit_btn.click()
                print(f"Successfully applied to: {posting_headline}")
                jobs_applied.append(posting_headline)
                applied_count += 1
                time.sleep(3)
            except Exception as e:
                print(f"Error clicking submit button: {e}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        print(f"Successfully applied to {applied_count}/{len(postings)} jobs!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        time.sleep(5)
        driver.quit()