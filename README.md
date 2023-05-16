# Salesforce Lead-to-Account Matching Script

This is a Python script that uses the Salesforce API to match leads to accounts based on fuzzy matching of the company name and email domain.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Setup

1. Create a Salesforce Apex REST service for converting leads:
    a. Log in to Salesforce.
    b. Click on the App Launcher (grid icon on the top left), search for 'Apex Classes', and select it.
    c. Click 'New' to create a new Apex class.
    d. In the new class dialog, enter the class name (e.g., LeadConvertService) and the below code.

        ```
        @RestResource(urlMapping='/LeadConvert/*')
        global with sharing class LeadConversionService {

            @HttpPost
            global static String convertLead(String leadId, String convertedStatus, String accountId, Boolean doNotCreateOpportunity) {
                Database.LeadConvert leadConvert = new Database.LeadConvert();
                leadConvert.setLeadId(leadId);
                leadConvert.setAccountId(accountId);
                leadConvert.setConvertedStatus(convertedStatus);
                leadConvert.setDoNotCreateOpportunity(doNotCreateOpportunity);
                
                Database.LeadConvertResult leadConvertResult = Database.convertLead(leadConvert);
                if (leadConvertResult.isSuccess()) {
                    return 'Lead converted successfully: ' + leadConvertResult.getContactId();
                } else {
                    return 'Error converting lead: ' + leadConvertResult.getErrors();
                }
            }
        }
        ```

    e. Click 'Save'.

2. Clone this repository to your local machine.

```
git clone https://github.com/kreitter/salesforce-lead-to-account-matching.git
```

3. Ensure that you have the required Python libraries installed. You can install them using pip:

```
pip install simple-salesforce fuzzywuzzy pandas python-dotenv
```

4. Set up the environment variables. Rename the .env.example to .env and fill in your Salesforce credentials:

```
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
```

## Usage

Run the script using a Python interpreter:

```
python lead_to_account_matching.py
```

## Running the Script

To run the script:

```
python sf_l2a_matching.py
```

This script queries all Leads and Accounts from your Salesforce instance, standardizes the data, and performs lead-to-account matching using fuzzy string matching. If a suitable match is found for a Lead, the Lead is converted and linked to the matched Account. The script will print out the results of the lead-to-account matching, including any leads that are converted and linked to accounts.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the terms of the MIT license.

## Contact

David Kreitter | david.kreitter@gmail.com | [www.kreitter.com](https://www.kreitter.com) | [LinkedIn](https://www.linkedin.com/in/dkreitter/)