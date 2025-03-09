# Home-Assistant Custom Components

Custom Components for Home-Assistant (http://www.home-assistant.io)

# Salus Thermostat Climate Component

My device is RT301i, it is working with it500 thermostat, the ideea is simple if you have a Salus Thermostat and you are able to login to salus-it500.com and controll it from this page, this custom component should work.
Component to interface with the salus-it500.com.
It reads the Current Temperature, Set Temperature, Current HVAC Mode, Current Relay Mode.

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
