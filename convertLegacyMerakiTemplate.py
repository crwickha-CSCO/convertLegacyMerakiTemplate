# convertLegacyMerakiTemplate
# 
# This script automates the conversion of legacy Meraki templates to support MG cellular gateways.
# It processes multiple networks simultaneously and can be restarted if interrupted.
#
# Prerequisites:
# - Ensure that cellular gateway support is added to the templates.
# - Refer to the Meraki documentation: 
#   https://documentation.meraki.com/MG/MG_Best_Practices/MG_Templates_Best_Practices#section_8
#
# Requirements:
# - Python 3.x
# - Meraki Python SDK
#   Install dependencies using:
#   pip install meraki
#
# Functionality:
# 1. Retrieves all networks within the organization.
# 2. Filters networks based on a specified tag (`TAG_FILTER`), excluding:
#    - Networks that already have a cellular gateway.
#    - Networks that are single-product (e.g., only wireless or security appliances).
# 3. For each eligible network:
#    - Retrieves its current configuration template.
#    - Creates a temporary MG (cellular gateway) network.
#    - Binds the temporary MG network to the same template.
#    - Splits the original network into separate product-type networks.
#    - Checks if an MG network already exists—if so, skips merging.
#    - Combines the split networks with the newly created MG network.
#    - Restores the original network name.
# 4. Outputs a list of all processed networks and their new product types.
#
# Notes:
#   update API_KEY="your_api_key_here" 
#   update ORG_ID="your_org_id_here)" 
# - The script includes a brief delay (`time.sleep(1)`) between API calls to prevent rate limits.
# - Modify the script if additional logic is needed for specific network conditions.
#
# Usage:
# Run the script with:
# python convertLegacyMerakiTemplate.py
#
# Author: Craig Wickham
# Date: Mar 17, 2025


import meraki
import time

# Meraki API Key
API_KEY = 'your_api_key_here'
ORG_ID = 'your_org_id_here'
TAG_FILTER = 'update'

# Initialize the Meraki dashboard
dashboard = meraki.DashboardAPI(API_KEY, output_log=False, print_console=False)

print(f"Gathering networks tagged with '{TAG_FILTER}' that don't already include product type: cellularGateway and not a single product network\n")

# Get all networks in the organization
# Meraki by default has a perPage of 1000. If you want to run the script against more then 1000 networks you can use the below perPage=5000
# networks = dashboard.organizations.getOrganizationNetworks(ORG_ID, perPage=5000)
networks = dashboard.organizations.getOrganizationNetworks(ORG_ID)

# Filter networks based on TAG_FILTER, exclude those with "cellularGateway", and ignore networks with only one product type
filtered_networks = [
    {"id": net["id"], "name": net["name"]}
    for net in networks
    if TAG_FILTER in net.get('tags', []) 
    and "cellularGateway" not in net.get('productTypes', [])
    and len(net.get('productTypes', [])) > 1
]

# Process each network individually
final_networks = []
for net in filtered_networks:
    original_network_id = net["id"]
    original_network_name = net["name"]

    print(f"Processing network: {original_network_name} (ID: {original_network_id})")

    # Retrieve original network details to get template ID
    original_details = dashboard.networks.getNetwork(original_network_id)
    template_id = original_details.get("configTemplateId")

    # Create a temporary cellularGateway-only network
    temp_network = dashboard.organizations.createOrganizationNetwork(
        ORG_ID,
        name=f"Temp_Cellular_{original_network_name}",
        productTypes=["cellularGateway"],
        timeZone=original_details["timeZone"]
    )

    temp_network_id = temp_network["id"]

    # Bind the temporary network to the same template
    if template_id:
        dashboard.networks.bindNetwork(temp_network_id, template_id)

    # Split the original network
    split_result = dashboard.networks.splitNetwork(original_network_id)

    split_network_ids = [net['id'] for net in split_result['resultingNetworks']]

    # Combine split networks with the temporary cellularGateway network
    combined_network = dashboard.organizations.combineOrganizationNetworks(
        ORG_ID,
        name=original_network_name,
        networkIds=split_network_ids + [temp_network_id]
    )

    # Store the combined network information
    final_networks.append({
        "name": combined_network["resultingNetwork"]["name"],
        "id": combined_network["resultingNetwork"]["id"]
    })

    print(f"Successfully processed network: {original_network_name}\n")

    # Sleep briefly to avoid hitting rate limits
    time.sleep(1)

# Print the final network details after processing
print("All networks processed successfully:")
for net in final_networks:
    details = dashboard.networks.getNetwork(net["id"])
    product_types = ", ".join(details.get("productTypes", []))
    print(f"Network Name: {net['name']}, Product Types: {product_types}")
