import sys
import requests.utils
import bs4
import getpass

s = requests.Session()


def main():
    login()
    print("Gathering list of locations...")
    # Get Locations
    res = s.get("https://graph.api.smartthings.com/location/list")
    res.raise_for_status()
    location_rows = bs4.BeautifulSoup(res.text, "html.parser").find('tbody').findAll('tr')
    location_dict = {}
    for row in location_rows:
        location_link = row.find('a')
        location_dict[location_link.contents[0].strip()] = location_link['href'].split(":443/location/")[0]
    location_keys = list(location_dict.keys())
    chosen_option = choose_number_option("Choose a location to gather data from", location_keys)
    server = location_dict[chosen_option]
    print("Hosting Server:", server)
    print("Gathering device list for", "[" + chosen_option + "]")

    # Get Devices
    res = s.get(location_dict[chosen_option] + "/device/list")
    res.raise_for_status()
    device_page = bs4.BeautifulSoup(res.text, "html.parser")
    device_rows = device_page.find('tbody').findAll('tr')
    device_dict = {}
    for row in device_rows:
        device_link = row.find('a')
        device_dict[device_link.contents[0].strip()] = device_link['href']
    device_keys = list(device_dict.keys())
    chosen_option = choose_number_option("Choose a device to gather data from", device_keys)
    print("Gathering device information for", "[" + chosen_option + "]")

    # Gather Device Information
    res = s.get(server + device_dict[chosen_option])
    res.raise_for_status()

    full_device_page = bs4.BeautifulSoup(res.text, "html.parser")
    report_table_html = full_device_page.findAll('tr', {'class': 'fieldcontain'})
    for item in report_table_html:
        if "Current States" in item.getText():
            data_items = item.findAll('li', {'class': 'property-value'})

    for item in data_items:
        data_type = item.find('a').contents[0].title()
        try:
            data_value = float(item.find('strong').contents[0].split(" ")[0])
        except ValueError:
            data_value = item.find('strong').contents[0].split(" ")[0]
        print(data_type, "=", data_value)
    return


def choose_number_option(text, options):
    print(" ")
    for index, option in enumerate(options): print("[" + str(index) + "]", option)
    entry = input(text + ": ")
    while not entry.isdigit() or int(entry) > len(options) - 1:
        print("!!! Unexpected input !!!\n")
        entry = input(text + ": ")

    print(" ")
    return options[int(entry)]


def login():
    print()
    login_data = {
        "username": input("SmartThings Email: "),
        "password": getpass.getpass('SmartThings Password: ')  # This will not work within PyCharm Console
    }
    r = s.post("https://auth-global.api.smartthings.com/sso/authenticate", data=login_data)
    if r.status_code == 401:
        print("Error! Credentials must not be correct - try again.")
        login()
    else:
        r.raise_for_status()
    return


if __name__ == '__main__':
    main()
    input("\nPress Enter To Quit...")
    sys.exit()
