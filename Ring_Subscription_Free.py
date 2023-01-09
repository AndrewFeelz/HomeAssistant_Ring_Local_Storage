import hassapi as hass
import datetime
import time
import os

#CONTSTANTS
PATH_TO_DIRECTORY= self.args["storage_location"]
DAYS_IN_A_MONTH= [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

class ring_doorbell_video_download(hass.Hass):

    def initialize(self):
        
        #Once A Day Storage Clean
        dailyTimer = datetime.time(7, 00, 0)
        self.run_daily(self.clean_Storage, dailyTimer)

        #Action for doorbell activity
        self.log("Initial Doorbell Video download setup")
        self.ring_camera = self.get_entity("camera.front_door")
        self.front_door_cam_action = self.get_entity("sensor.front_door_last_activity")
        #if not correct, use "sensor.front_door_last_motion"
        self.handle = self.front_door_cam_action.listen_state(self.video_event, self.ring_camera, attribute="video_url")


    def video_event(self, entity, attribute):
        self.log("Action Detected")
        #Waits for 10 seconds for Ring Server Delay
        time.sleep(10)

        #Get Current Day
        x = datetime.datetime.now()
        current_day = str(x.day) + '.' + str(x.month) + '.' + str(x.year) + ' ' + str(x.hour) + ":" + str(x.minute) + ":" + str(x.second) + "," + str(x.microsecond)
        current_day_obj = datetime.datetime.strptime( current_day,'%d.%m.%Y %H:%M:%S,%f')
        

        
        url = self.get_state(entity, attribute)
        subdir_name= "Ring_Weekly_Storage"
        filename = '{}.mp4'.format(current_day_obj)
        #filename = filename.replace(":", "-")
        #filename = filename.replace(" ", "_")

        if url:
            self.call_service("downloader/download_file", 
                url=url,
                subdir=subdir_name,
                filename=filename)

            self.log("Doorbell Video Downloaded", "INFO")
        else:
            self.log("No URL Provided for Doorbell Video", "WARNING")


    def log_notify(self, msg, level):
        self.log(msg, level)
        self.call_service("notify/notify", message=msg)
        
        
    def clean_Storage(self):
        self.log("Storage Clean Has Commenced", "INFO")
        files_perged = 0
        
        #Get the date a week ago
        x = datetime.datetime.now()
        if(x.day <= 7):
            past_month = x.month-1
            
            if (past_month == 0):
                past_month = 11
                day_in_prevoius_month = DAYS_IN_A_MONTH[x.month - (past_month - 1)]
                year_needed = x.year - 1
            else:
                day_in_prevoius_month = DAYS_IN_A_MONTH[x.month - (past_month - 1)]
                year_needed = x.year

            cutoff_day = day_in_prevoius_month - abs(x.day - 7)
            cutoff_day = str(cutoff_day) + '.' + str(past_month) + '.' + str(year_needed) + ' 00:00:00,00'
            cutoff_day_obj = datetime.datetime.strptime( cutoff_day,'%d.%m.%Y %H:%M:%S,%f')
        else:
            cutoff_day = str(x.day - 7) + '.' + str(x.month) + '.' + str(x.year) + ' 00:00:00,00'
            cutoff_day_obj = datetime.datetime.strptime( cutoff_day,'%d.%m.%Y %H:%M:%S,%f')
        
        for filename in os.listdir(PATH_TO_DIRECTORY):
            f = os.path.join(PATH_TO_DIRECTORY,filename)

            if os.path.isfile(f):
                filename = filename[:-4]
                filedate_obj = datetime.datetime.strptime( filename,'%d.%m.%Y %H:%M:%S,%f')
                if (filedate_obj < cutoff_day_obj):
                    os.remove(f) 
                    files_perged += 1
            else:
                self.log("Error in deleting file " + f + "", "WARNING")
        
        #Find a way to msg this
        self.log("Storage Clean Has Finished. " + str(files_perged) + " have been deleted.", "INFO")
        
        
        
