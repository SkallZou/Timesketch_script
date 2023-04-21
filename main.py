import random
from timesketch_api_client import client
from timesketch_import_client import importer
from timesketch_import_client import utils
from datetime import datetime
import configparser
import os
import pandas as pd

def main():

    config = configparser.ConfigParser()
    config.read("config.cfg")
    tsServer = config['LOCALHOST']['Server']
    tsUser = config['LOCALHOST']['User']
    tsSecret = config['LOCALHOST']['Password']

    print("[+] Connecting to {0}...".format(tsServer))
    tsClient = client.TimesketchApi(tsServer, tsUser, tsSecret, verify=False)
    print("[+] Connected.")
    dateNow = datetime.now()
    time = dateNow.strftime("%d/%m/%Y %H:%M:%S")
    quit = False

    while(quit==False):
        # Menu
        print("[#] 1. Create Sketch\n[#] 2. List Sketch\n[#] 3. Delete Sketch\n[#] 4. Quit\n[?] Please enter value:")
        choice = input()
        if choice == "1":
            # Create an investigation
            randomNumber = random.randint(1, 9999)
            tsClient.create_sketch("Investigation - {0} ".format(randomNumber), "Incident on {0}".format(time))

            # Get the last sketch
            sketch_dic = dict((x.id, x) for x in tsClient.list_sketches())
            newIncident = tsClient.get_sketch(list(sketch_dic)[0])
            print("[+] Created Investigation: [{0}] - {1}".format(newIncident.id, newIncident.name))
            # Get file from user
            path=os.path.abspath(os.curdir)
            print("Specify the file to analyze")
            file = input()
            file = path + "\\" + file
            filename, fileextension = os.path.splitext(file)

            with importer.ImportStreamer() as streamer:
                streamer.set_sketch(newIncident)
                streamer.set_timeline_name("Breach {0}".format(time))

                if fileextension == ".xlsx":
                    df = pd.read_excel(file)
                    if 'datetime' not in df.columns:
                        for column in df.columns:
                            if "time" in column:
                                time = column
                                break
                        df.rename(columns={time: 'datetime'}, inplace=True)

                    date = pd.to_datetime(df["datetime"], dayfirst=True, utc=True)
                    df["datetime"] = date
                    streamer.set_message_format_string('{Username:s} run {Path:s}')
                    streamer.set_timestamp_description("PowerShell Monitoring")
                    streamer.add_data_frame(df)

                elif fileextension == ".csv":
                    df = pd.read_csv(file, delimiter=';')
                    if 'datetime' not in df.columns:
                        for column in df.columns:
                            if "time" in column:
                                time = column
                                break
                        df.rename(columns={time: 'datetime'}, inplace=True)

                    date = pd.to_datetime(df["datetime"], dayfirst=True, utc=True)
                    df["datetime"] = date
                    df.columns = [column.replace(' ', '_') for column in df.columns]
                    streamer.set_message_format_string("{Username:s} - {Command_line:s}")
                    streamer.set_timestamp_description("EDRlog") # Determine the type of log according to the filename ?
                    streamer.add_data_frame(df)

        elif choice == "2":
            # Check on current investigation
            print("[#] --- List of investigations ---")
            for sketch in tsClient.list_sketches():
                print("    ID{0} - {1}".format(sketch.id, sketch.name))
            print("\n")

        elif choice == "3":
            userRequest=""
            while(userRequest not in ["exit()", "all()"]):
                print("[#] --- List of investigations ---")
                for sketch in tsClient.list_sketches():
                    print("     ID{0} - {1}".format(sketch.id, sketch.name))
                sketch_dic = dict((x.id, x) for x in tsClient.list_sketches())

                print("[?] Please indicate the sketch ID to delete\nType all() to delete all.\nType exit() to exit.")
                userRequest = input()
                if userRequest == "all()":
                    for sketch in tsClient.list_sketches():
                        sketch.delete()
                else:
                    try:
                        sketchToDelete = sketch_dic.get(int(userRequest))
                        sketchToDelete.delete()
                        print("[!] Deleted - {0}".format(sketchToDelete.name))
                    except:
                        if userRequest != "exit()":
                            print("[!] Could not find the sketch ID")

        else:
            quit=True
            print("[!] Exited.")

if __name__ == '__main__':
    main()
