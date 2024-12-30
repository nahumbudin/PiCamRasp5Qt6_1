import operator
import subprocess

from netifaces import interfaces, ifaddresses, AF_INET
from flask import Flask, render_template, send_from_directory, request
import os
import time

import globals

host_name = "localHost"
server_port = 5000


def get_host_wlan_ip():
    host_ip_str = "localHost"
    for iface_name in interfaces():
        address = [i['addr'] for i in ifaddresses(iface_name).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
        host_ip_str = str(address[0])
        if not host_ip_str.startswith("127.") and iface_name.startswith("wl"):
            break

    return host_ip_str


def get_wifi_ssd():
    connected_ssid = os.popen("sudo iwgetid -r").read().removesuffix('\n')
    return connected_ssid


def web_server_service():
    app = Flask(__name__, static_folder='static')

    images_folder = globals.DEFAULT_IMAGES_DIR
    entries_per_page = 32

    def get_directory_content(directory_path):
        content = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                item_type = 'directory'
            elif item.endswith(('.jpg', '.jpeg')):
                item_type = 'image'
            else:
                item_type = 'file'

            content.append({'name': item, 'type': item_type, 'path': item_path})

        content.sort(key=operator.itemgetter('name'))

        return content

    @app.route('/')
    def image_explorer():
        images_dir = images_folder

        entries = get_directory_content(images_dir)

        page = int(request.args.get('page', 1))  # Get the page number from the query parameters
        start_index = (page - 1) * entries_per_page
        end_index = start_index + entries_per_page

        total_entries = len(entries)
        total_pages = -(-total_entries // entries_per_page)  # Ceiling division to calculate total pages

        images = entries[start_index:end_index]

        return render_template('image_explorer.html', images=images, page=page, total_pages=total_pages)

    @app.route('/images/<path:filename>')
    def get_image(filename):
        image_directory = images_folder
        return send_from_directory(image_directory, filename)

    @app.route('/get-directory')
    def get_directory():
        directory_path = request.args.get('path')
        print("get-directory", directory_path)

        entries = get_directory_content(directory_path)

        page = int(request.args.get('page', 1))  # Get the page number from the query parameters
        start_index = (page - 1) * entries_per_page
        end_index = start_index + entries_per_page

        total_entries = len(entries)
        total_pages = -(-total_entries // entries_per_page)  # Ceiling division to calculate total pages

        images = entries[start_index:end_index]

        print(images)

        return render_template('image_explorer.html', images=images, page=page, total_pages=total_pages)

    host_name = get_host_wlan_ip()


    app.run(host=host_name, port=server_port, debug=True)


if __name__ == "__main__":
    web_server_service()
    print("Flask started")
