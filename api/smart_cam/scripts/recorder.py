import cv2
import threading
import time


class Video_Recorder:
    """This class defines a video recorder or a camera.
    The objects of this class can be called as camera objects.
    The objects of this class can record videos from an android device,
    read the video feed from the link provided by corressponding app on
    the android device and save the video in required folders."""

    def __init__(self, link, cam_name, stop_key, save_as):
        """This method/constructor sets up the base for camera object.
        It takes in a link/URL from where the object reads the video feed.
        Sets up arguments for cv2 functions.
        It takes in name of camera and a stop key for that camera,
        also it creates a thread for that camera.
        Also we pass a save_as argument in which our video is saved"""

        self.feed_link = link
        self.capture_object = cv2.VideoCapture(link)
        self.fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        self.stop_key = stop_key
        self.name = cam_name
        self.out_file_name = save_as
        self.output = cv2.VideoWriter(self.out_file_name, self.fourcc, 20.0, (300, 300))
        self.cam_thread = threading.Thread(target=self.start_rec)
        self.enabled = True

    def start_rec(self):
        """This method ensures that the program keeps reading video
        feed from the link/URL and keep saving it to the output,
        when finally the key to stop the recording is pressed."""

        while self.capture_object.isOpened():
            self.ret, self.frame = self.capture_object.read()
            if not self.ret:
                self.ret, self.frame = self.reconnect_procedure(3)
                if not self.ret:
                    self.failed_connection()
                    break
                else:
                    self.reconnection_success()
            self.frame = cv2.resize(self.frame, (300, 300))
            self.output.write(self.frame)
            cv2.imshow(self.name, self.frame)
            if cv2.waitKey(1) == ord(self.stop_key) or not self.enabled:
                self.stop_recording()
                break

    def reconnecting(self):
        """Creates and returns a Video capture object"""
        self.capture_object = cv2.VideoCapture(self.feed_link)
        return self.capture_object

    def reconnect_procedure(self, attempts):
        """Takes an attempts argument, and tries to reconnect
        that many times. Displays status of connection and finally
        returns the ret,frame which we pass to self.ret and self.frame."""

        while attempts > 0:
            print("Unable to connect", self.name, "Trying to reconnect...")
            ret, frame = self.reconnecting().read()
            attempts -= 1
            if not ret:
                print("Connection attempt failed, trying again...")
                time.sleep(5)
                continue
            else:
                return ret, frame
        return ret, frame

    def failed_connection(self):
        """Displays total failure message and calls stop_recording function"""

        print("All connection attempts failed, sorry !!")
        self.stop_recording()

    def reconnection_success(self):
        """Prints success message"""

        print("Connected, congratulations !!")

    def stop_recording(self):
        """Releases the capture object and output and destroys windows
        when stop key is pressed. In a way, this function winds up everything."""
        print("Stopping recording")
        self.capture_object.release()
        self.output.release()
        cv2.destroyAllWindows()

    def start_thread(self):
        """Starts a thread for a single object."""

        self.cam_thread.start()

    def join_thread(self):
        """Ends the thread for a single object."""

        self.cam_thread.join()

    def start_rec_original(self):
        while self.capture_object.isOpened():

            self.ret, self.frame = self.capture_object.read()
            if not self.ret:
                print("Unable to connect", self.name, "Trying to reconnect...")
                self.ret, self.frame = self.reconnect_procedure(3)
                if not self.ret:
                    print("All connection attempts failed, sorry !!")
                    self.capture_object.release()
                    self.output.release()
                    cv2.destroyAllWindows()
                    break
                else:
                    print("Connected, congratulations !!")

            self.frame = cv2.resize(self.frame, (300, 300))
            self.output.write(self.frame)
            cv2.imshow(self.name, self.frame)
            if cv2.waitKey(1) == ord(self.stop_key):
                self.capture_object.release()
                self.output.release()
                cv2.destroyAllWindows()
                break


# ----------------------------utilities------------------------------------------
def start_all_threads(list_of_cams):
    """Starts the threads of list of camera objects passed."""

    for th in list_of_cams:
        th.cam_thread.start()


def join_all_threads(list_of_cams):
    """Ends the threads of list of camera objects passed."""

    for th in list_of_cams:
        th.cam_thread.join()
