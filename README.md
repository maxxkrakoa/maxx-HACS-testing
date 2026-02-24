# Maxx HACS Testing

Example Home Assistant integration for testing HACS distribution.

## Features
- Electricity usage sensor
- Water usage sensor
- Designed for easy extension to REST API

## Installation
1. Install via HACS (Custom Repository)
2. Restart Home Assistant
3. Add integration via UI

## Manual Update Trigger
If you need to force an immediate fetch of new data outside of the regular 30-minute interval, you can use the built-in Home Assistant action.
1. Go to **Developer Tools** > **Actions**
2. Search for the `Maxx HACS Testing: Update data` action (`maxx_hacs_testing.update_data`)
3. Click **Perform action**

## Debugging
To see the raw output of the API server calls and any errors encountered during data retrieval, you can enable debug logging for the integration in your Home Assistant `configuration.yaml` file:
```yaml
logger:
  default: info
  logs:
    custom_components.maxx_hacs_testing: debug
```
