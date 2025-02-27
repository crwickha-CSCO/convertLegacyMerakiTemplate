# convertLegacyMerakiTemplate

Convert a legacy Meraki template to allow support for MG cellular gateways.

This script can run for multiple networks bound to different templates simultaneously. If it encounters an error, you can restart the script, and it will continue from where it left off.

## Prerequisites

Before running this script, you must add cellular gateway support to the templates.  
Refer to the [Meraki documentation](https://documentation.meraki.com/MG/MG_Best_Practices/MG_Templates_Best_Practices#section_8) for detailed instructions.

## Requirements

This script requires the following Python libraries:

- `meraki` (for interacting with the Meraki API)
- `time` (built-in Python library for handling delays)

To install the required dependency, run:

- pip install meraki

## Functionality

The script performs the following steps:

- Identifies networks with a specific tag that do not already include a cellular gateway.
- Adds an MG network to the identified networks.  
  *Ignores single-technology networks by default. If you want to support single-technology networks, you will need to modify the code to prevent splitting these networks and instead directly combine them with the new MG network.*

For each network:

1. Stores the network name, network ID, and network template.
2. Creates a new MG network and binds it to the same template as the original network.
3. Splits the network (retains the new split networks in a list).
4. Combines the split networks with the new MG network and restores the original network name.
5. Moves on to the next network.
6. Prints all processed networks and their product types.
