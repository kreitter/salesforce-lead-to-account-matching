import os
from simple_salesforce import Salesforce
from fuzzywuzzy import fuzz
import pandas as pd
from dotenv import load_dotenv
import json

load_dotenv()  # take environment variables from .env.

sf = Salesforce(username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'))

# Query Leads and Accounts using Bulk API
lead_job = sf.bulk.Lead.query("SELECT Id, Company, Email, Status FROM Lead")
account_job = sf.bulk.Account.query("SELECT Id, Name, Website FROM Account")

leads = lead_job
accounts = account_job

# Convert to DataFrames
leads_df = pd.DataFrame(leads).drop(columns='attributes')
accounts_df = pd.DataFrame(accounts).drop(columns='attributes')

# Standardize data
leads_df['Company'] = leads_df['Company'].str.lower().str.strip()
leads_df['Email'] = leads_df['Email'].str.lower().str.strip()
accounts_df['Name'] = accounts_df['Name'].str.lower().str.strip()
accounts_df['Website'] = accounts_df['Website'].str.lower().str.strip()

# Perform lead-to-account matching
threshold = 85

for _, lead in leads_df.iterrows():
    # Skip the lead if the status is 'Closed - Converted'
    if lead['Status'] == 'Closed - Converted':
        print(f"Lead {lead['Id']} is already converted, skipping...")
        continue

    lead_company = lead['Company']
    lead_email_domain = lead['Email'].split('@')[1]
    max_score = -1
    best_match_account_id = None

    for _, account in accounts_df.iterrows():
        account_name = account['Name']
        account_website = account['Website']

        # Add check for None
        if account_website is not None:
            account_website = account_website.replace('www.', '')

        score_company = fuzz.token_sort_ratio(lead_company, account_name)
        score_email_website = fuzz.token_sort_ratio(lead_email_domain, account_website) if account_website else 0

        score = max(score_company, score_email_website)

        if score > max_score:
            max_score = score
            best_match_account_id = account['Id']

    if max_score >= threshold:
        # Convert Lead and link to matched Account
        lead_conversion = {
            'leadId': lead['Id'],
            'convertedStatus': 'Closed - Converted',  # Adjust this value to match a valid status in your Salesforce instance
            'accountId': best_match_account_id,
            'doNotCreateOpportunity': 'true'  # This prevents creating an Opportunity during conversion
        }
        # get the base_url, remove the '/services/data/vXX.0/' part and add the Apex REST service path
        sf_instance_url = sf.base_url.split('/services')[0]
        conversion_endpoint = "/services/apexrest/LeadConvert"
        endpoint_url = sf_instance_url + conversion_endpoint
        # make the POST request
        sf._call_salesforce('POST', endpoint_url, data=json.dumps(lead_conversion))
        print(f"Lead {lead['Id']} converted and linked with Account {best_match_account_id}")
    else:
        print(f"No suitable match found for Lead {lead['Id']}")