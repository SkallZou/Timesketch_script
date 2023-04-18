import random
from timesketch_api_client import search
from timesketch_api_client import client
from timesketch_import_client import importer
from datetime import datetime

def main():

    tsServer = ""
    tsUser = ""
    tsSecret = ""
    print("[+] Connecting to {0}...".format(tsServer))
    tsClient = client.TimesketchApi(tsServer, tsUser, tsSecret)
    dateNow = datetime.now()
    time = dateNow.strftime("%d/%m/%Y %H:%M:%S")
    quit = False


    while(quit==False):
        # Menu
        print("[+] Connected.")
        print("[#] 1. Create Sketch\n[#] 2. Update Sketch\n[#] 3. Delete Sketch\n[?] Please enter value:")
        choice = input()
        if choice == "1":
            randomNumber = random.randint(1, 9999)
            tsClient.create_sketch("Investigation - {0} ".format(randomNumber), "Incident on {0}".format(time))

            # Get the last sketch
            sketch_dic = dict((x.id, x) for x in tsClient.list_sketches())
            newIncident = tsClient.get_sketch(list(sketch_dic)[0])
            print("[+] Created Investigation: [{0}] - {1}".format(newIncident.id, newIncident.name))

            # Adding CSV data
            with importer.ImportStreamer() as streamer:
                streamer.set_sketch(newIncident)
                streamer.set_timeline_name("test timeline")
                streamer.set_timestamp_description("This is a test for creating a timeline")
                streamer.add_file("test.csv")

        elif choice == "2":
            # Check on current investigation
            for sketch in tsClient.list_sketches():
                print("[{0}] - {1}".format(sketch.id, sketch.name))

        elif choice == "3":
            for sketch in tsClient.list_sketches():
                print("[{0}] - {1}".format(sketch.id, sketch.name))

            sketch_dic = dict((x.id, x) for x in tsClient.list_sketches())

            print("[?] Please indicate the sketch ID to delete")
            userRequest = input()
            try:
                sketchToDelete = sketch_dic.get(int(userRequest))
                sketchToDelete.delete()
                print("[!] Deleted - {0}".format(sketchToDelete.name))
            except:
                print("[!] Could not find the sketch ID")

        else:
            quit=True
            print("[!] Exited.")

if __name__ == '__main__':
    main()
