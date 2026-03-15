# Home Assistant Brunata Online

This is a Home Assistant integration that connects to the Brunata API to fetch your household's utility consumption data.

## Features
- Electricity usage sensor (fetches daily values)
- Water usage sensor (fetches daily values)
- Integrates securely with your Brunata online account

## Installation
1. Install via HACS (Custom Repository)
2. Restart Home Assistant
3. Add integration via UI

## Manual Update Trigger
If you need to force an immediate fetch of new data outside of the regular 30-minute interval, you can use the built-in Home Assistant action.
1. Go to **Developer Tools** > **Actions**
2. Search for the `Home Assistant Brunata Online: Update data` action (`brunata_online.update_data`)
3. Click **Perform action**

## Debugging
To see the raw output of the API server calls and any errors encountered during data retrieval, you can enable debug logging for the integration in your Home Assistant `configuration.yaml` file:
```yaml
logger:
  default: info
  logs:
    custom_components.brunata_online: debug
```
