from dotenv import load_dotenv
import os
import requests
from dataclasses import dataclass

load_dotenv()

meraki_key = os.environ.get("MERAKI_API_KEY")
meraki_org_id = os.environ.get("MERAKI_ORG_ID")

@dataclass
class MerakiAp():
    serial: str
    name: str = None
    ether_mac: str = None
    network_id: str = None
    basic_service_sets: list = None
    two_four_ghz: list = None
    five_ghz: list = None

    def print_radio_name_pairs(self):
        for radio in self.two_four_ghz:
            print(f'{radio}    {self.name}')
        for radio in self.five_ghz:
            print(f'{radio}    {self.name}')

def get_meraki_devices(org_id, api_key):
    url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": f"{api_key}"
    }
    response = requests.request('GET', url, headers=headers)
    response.raise_for_status()
    return(response.json())

def get_wireless_device_status(org_id, api_key, serial):
    url = f"https://api.meraki.com/api/v1/devices/{serial}/wireless/status"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": f"{api_key}"
    }
    response = requests.request('GET', url, headers=headers)
    response.raise_for_status()
    return(response.json()['basicServiceSets'])    

devices = get_meraki_devices(org_id=meraki_org_id, api_key=meraki_key)

aps = {}
for device in devices:
    if 'MR' in device['model']:
        device_serial = device['serial']
        ap = MerakiAp(device_serial)
        ap.name = device['name']
        ap.ether_mac = device['mac']
        ap.network_id = device['networkId']
        aps.update({device_serial: ap})

for serial in aps.keys():
    two_four_radios = []
    five_radios = []
    bss = get_wireless_device_status(meraki_org_id, meraki_key, serial=serial)
    aps[serial].basic_service_sets = bss
    for ssid in aps[serial].basic_service_sets:
        if '2.4 GHz' in ssid['band']:
            two_four_radios.append(ssid['bssid'])
        if '5 GHz' in ssid['band']:
            five_radios.append(ssid['bssid'])
    aps[serial].two_four_ghz = two_four_radios
    aps[serial].five_ghz = five_radios

for ap in aps.values():
    ap.print_radio_name_pairs()