from datetime import datetime
import requests
import configparser
import shutil
import sys
import json
import os

certificate = 'API_Data/Sanofi_root.pem'
folder = None
failed_lst = {'rds': [], 'cl': []}

# Get API Information
config = configparser.ConfigParser()
config.read('API_Data/API Info.txt')

# User Input Function
def map_userInp(type, domain_lst=[]):
    try:
        env = ["DEV", "UAT", "PROD"]
        inp = int(input("\nEnter your choice: "))

        if type == 1:
            return env[inp - 1]
        else:
            return domain_lst[inp - 1]["key"]
            
    except Exception as e:
        print("Error in getting user input: ", e)
        sys.exit(-1)

# Get the Access Token
def get_access_token(token_url, grant_type, client_id, client_secret):
    try:
        response = requests.post(token_url, data={
            'grant_type': grant_type,
            'client_id': client_id,
            'client_secret': client_secret
        }, verify=certificate)

        response_data = response.json()
        if response.status_code == 200:
            return response_data['access_token']
        else:
            raise Exception(f"Error obtaining access token: {response_data}")
        
    except Exception as e:
        print("Error in Accessing token: ", e)
        sys.exit(-1)

# Make the API Request
def api_request(request_type, access_token, api_url, codelist_id = 0):
    try:
        if request_type == "GET":
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(api_url, headers=headers,verify=certificate)
        elif request_type == "POST":
            headers = {
                'Authorization': f'Bearer {access_token}', 
                'Content-Type': 'application/json',
                'Accept': 'application/octet-stream'
            }

            payload = {
                "delimiter": "COMMA",
                "codepage": "UTF8",
                "decimalSeparator": "COMMA",
                "thousandSeparator": "DOT",
                "dateFormat": "ISO",
                "filename": "testdata.csv",
                "containerType": "codelist",
                "containerId": f"{codelist_id}",
                "excludeParentId": True,
                "pageSize": 10000,
                "page": 0,
                "repeatHeaders": False,
                "addLabelsForReferenceAttribute": True
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload), verify=certificate)

        if response.status_code == 200:
            return response.json() if request_type == 'GET' else response.text
        else:
            print("ERROR")
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print("Error in making API Request: ")
        return None
        # sys.exit(-1)

# Make the API Request in recover mode
def recover_asset(url):
    for i in range(2):
        data = api_request('GET', access_token, url)
        if data:
            return data
        else:
            print(f"Failed !!!, Trying Again...\n")
    
    return None
        
# Get all the domain names
def get_domain_list():
    try:
        enums_data = api_request('GET', access_token, api_url + '/enums')
        domain_lst = enums_data['domain']
        
        if domain_lst:
            return domain_lst
        else:
            raise Exception("Fetching domains failed !!!")
    except Exception as e:
        print("Error in getting domains: ", e)
        sys.exit("-1")

# Get the RDS by selected domain
def get_rds_by_domain():
    try:
        rds = api_request('GET', access_token, api_url + "/rds")
        ref_lst = []
        for ds in rds:
            if 'domain' in ds.keys() and ds['domain'] == domain:
                ref_lst.append(ds['id'])
        
        if ref_lst:
            return ref_lst
        else:
            print("Invalid Domain !!!")
            raise Exception("Error in getting RDS: ")
        
    except Exception as e:
        print("Error in getting RDS: ", e)
        sys.exit(-1)

# Get the codelists from the ref_lists
def get_codelists(ref_lst):
    try:
        codelists = []
        for i, ref_id in enumerate(ref_lst, 1):
            try:
                data = api_request('GET', access_token, api_url+f"/rds/{ref_id}/codelists")
                for cl in data:
                    codelists.append({
                        'id': cl['id'],
                        'name': cl['name']
                    })
                print(f"---> Codelists For Reference Data Set: {ref_id} fetched Successfully. [{i}/{len(ref_lst)}]")
            except Exception as e:
                print(f"Error in fetching the codelist for {ref_id}. Error Desc: ", e)
                print("\n-----Entering in the Recovery Mode for getting CodeLists:------------------------------------------\n")
                data = recover_asset(api_url+f"/rds/{ref_id}/codelists")
                if data:
                    for cl in data:
                        codelists.append({
                            'id': cl['id'],
                            'name': cl['name']
                        })
                    print(f"---> Codelists For Reference Data Set: {ref_id} Recovered Successfully. [{i}/{len(ref_lst)}]")
                else:
                    failed_lst['rds'].append(ref_id)
                    print(f"Unable to Fetch the data for Reference ID: {ref_id}. Please get the data manually")
                print("\n-----Exiting the Recovery Mode:---------------------------------------------------------\n")
        
        if codelists:
            return codelists
        else:
            raise Exception("No Codelists found !!!")
        
    except Exception as e:
        print("Error occured while fetching code lists for each rds: ", e)
        sys.exit(-1)

# Get values from codelists
def get_values_from_codelists(codelists):
    try:
        content_lst = []
        for i, cl in enumerate(codelists,1):
            try:
                data = api_request('POST', access_token, api_url + "v3/export", codelist_id=cl['id'])
                cl['content'] = data
                content_lst.append(cl)
                print(f"---> Code Values For Codelist: {cl['id']} fetched Successfully. [{i}/{len(codelists)}]")
            except Exception as E:
                print(f"Error occured while fetching code values for codelist {cl}. Error Desc: ", e)
                print("\n-----Entering in the Recovery Mode for getting Code Values:------------------------------------------\n")
                data = recover_asset('POST', access_token, api_url + "v3/export", codelist_id=cl['id'])
                if data:
                    cl['content'] = data
                    content_lst.append(cl)
                    print(f"---> Code Values for Codelist: {cl['id']} Recovered Successfully. [{i}/{len(codelists)}]")
                else:
                    failed_lst['cl'].append(cl)
                    print(f"Unable to Fetch the data for Codelist: {cl['id']}. Please get the data manually")
                print("\n-----Exiting the Recovery Mode:---------------------------------------------------------\n")

        if content_lst:
            return content_lst
        else:
            raise Exception("Error in fetching values of codelist !!!")

    except Exception as e:
        print("Error in getting values from codelist: ", e)
        sys.exit(-1)

# Generate the CSV Files of each code list in the folder
def generate_csv_file(content_lst):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        for i, codelist in enumerate(content_lst, 1):
            file_name = f"{folder}/{codelist['name']}.csv"
            csv_content = codelist['content']

            with open(file_name, mode='a', newline='', encoding='utf-8') as file:
                file.write(csv_content)

            print(f"---> CSV File '{file_name}' Generated Successfully. [{i}/{len(content_lst)}]")
    except Exception as e:
        print("Error in Generating CSV File: ", e)
        sys.exit(-1)

# Generate the ZIP file and remove the folder
def generate_zip_file():
    try:
        shutil.make_archive(folder, 'zip', folder)
        print(f"\n===> '{folder}.zip' Generated Successfully\n")

        # Removing the folder after zipping
        shutil.rmtree(folder)
        print(f"\n===> Folder '{folder}' removed successfully.\n")
            
    except Exception as e:
        print("Error in generating the zip file: ", e)
        sys.exit(-1)

if __name__ == "__main__":

    print("\n\t\tWelcome the the Export Automation Script :)\n")

    # User Input For Environment
    print("Please select the environment by entering the corresponding number:\n1 - DEV\n2 - UAT\n3 - PROD")
    environment_name = map_userInp(1)

    print("\n===> Export Started...")

    # Setup of API variables
    client_id = config[environment_name]['Client_id']
    client_secret = config[environment_name]['Client_secret']
    api_url = config[environment_name]['API Base path for V1']
    token_url = config[environment_name]['Auth access token url']
    grant_type = 'client_credentials'

    # Get Token
    access_token = get_access_token(token_url, grant_type, client_id, client_secret)
    print("\n===> Initial Setup Successful...")

    # Get all domain list
    domain_lst = get_domain_list()

    # User Input For domain 
    print("\nPlease select the domain by entering the corresponding number:")
    for i, dmn in enumerate(domain_lst, 1):
        print(f"{i} - {dmn['label']} - ({dmn['key']})")
        
    domain = map_userInp(2, domain_lst)
    folder = f"{domain}-codelists-{environment_name}-{datetime.today().strftime('%Y-%m-%d')}"
    
    # Get rds by domain
    ref_lst = get_rds_by_domain()
    print("\n===> Fetching of RDS Successful...\n")

    # Get the CodeLists from the selected reference lists
    codelists = get_codelists(ref_lst)
    print("\n===> Fetching of Codelists Successful...\n")

    # Export data of each codelists
    content_lst = get_values_from_codelists(codelists)
    print("\n===> Fetching of Code Values Successful...\n")
    
    # Creating CSV Files
    generate_csv_file(content_lst)
    print("\n===> All CSV Files Generated Successfully...\n")

    # Creating Zip file and removing folder
    generate_zip_file()
    print("\n===> Export Completed Successfully...\n")

    failed_rds = failed_lst["rds"]
    failed_cl = failed_lst['cl']

    if failed_rds or failed_cl:
        print("\n!!!!!!!! Additional Information !!!!!!!!!!!\n\n")
        print("Add the following data manually from Informatica R360: \n")
        if failed_rds:
            print("Failed Reference Data Set IDs: ")
            for i, rid in enumerate(failed_rds):
                print(f"{i+1}. {rid}")
        
        print()
        if failed_cl:
            print("Failed Codelists: ")
            for i, cl in enumerate(failed_cl):
                print(f"{i+1}. {cl['id']} - {cl['name']}")
    
    print("\nEND\n")