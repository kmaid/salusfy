# Home Assistant Salus Thermostat Climate Component

A custom component for Home Assistant (https://www.home-assistant.io) that integrates with Salus thermostats through the salus-it500.com website via scraping.

This component works with Salus thermostats like the RT301i that connect to the IT500 system. If you can control your thermostat through the salus-it500.com website, this integration should work for you.

The component provides:

- Current Temperature
- Set Temperature
- Current HVAC Mode
- Current Relay Mode

## Maintenance Notice

This repository is now under new maintenance after the original author became unresponsive. The integration has been updated to:

- Use async methods for better performance
- Fix compatibility with Home Assistant 2025.3
- Address deprecation warnings
- Improve HACS integration

## Installation

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2. Click on HACS in the sidebar.
3. Go to "Integrations" tab.
4. Click the three dots in the top right corner and select "Custom repositories".
5. Add the URL of this repository and select "Integration" as the category.
6. Click "ADD".
7. Look for "Salus Thermostat" in the integrations tab and click on it.
8. Click "INSTALL" and then "INSTALL" again on the confirmation dialog.
9. Add the configuration to your `configuration.yaml` file (see configuration section below).
10. Restart Home Assistant.

## Configuration

To use this component in your installation, add the following to your configuration.yaml file:

### Example configuration.yaml entry

```
climate:
  - platform: salusfy
    username: "EMAIL"
    password: "PASSWORD"
    id: "DEVICEID"
```

![image](https://user-images.githubusercontent.com/33951255/140300295-4915a18f-f5d4-4957-b513-59d7736cc52a.png)
![image](https://user-images.githubusercontent.com/33951255/140303472-fd38b9e4-5c33-408f-afef-25547c39551c.png)

### Getting the DEVICEID

1. Loggin to https://salus-it500.com with email and password used in the mobile app(in my case RT301i)
2. Click on the device
3. In the next page you will be able to see the device ID in the page URL
4. Copy the device ID from the URL
   ![image](https://user-images.githubusercontent.com/33951255/140301260-151b6af9-dbc4-4e90-a14e-29018fe2e482.png)

### Known issues

salus-it500.com server is bloking the IP of the host, in our case the HA external IP. This can be fixed with router restart in case of PPOE connection or you can try to send a mail to salus support...

## Acknowledgements

- Original author: @floringhimie
- Async implementation: @Big-Szu
- Current maintainer: @kmaid
