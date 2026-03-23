import time
from vmbpy import *

def frame_handler(cam: Camera, stream: Stream, frame: Frame):
    """This function is called by the VimbaC API when a frame has been received."""
    print(cam.AcquisitionStatus.get())

    if frame.get_status() == FrameStatus.Complete:
        print(f"Camera({cam.get_id()}) acquired Frame(id={frame.get_id()}, status={frame.get_status()})")
        # In a real application, you would copy or process the frame data here.
    else:
        print(f"Frame incomplete: {frame.get_status()}")
    
    # Requeue the frame for the next acquisition
    cam.queue_frame(frame)

def software_trigger_example():
    with VmbSystem.get_instance() as vmb:
        cams = vmb.get_all_cameras()
        if not cams:
            print("No cameras found. Abort.")
            return

        # Use the first camera
        cam = cams[0]
        with cam as cam_open:
            try:
                # Configure camera for software trigger
                # Ensure AcquisitionMode is not 'Continuous' for triggering to work as expected for single frames
                cam_open.ExposureAuto.set('Continuous') # Optional: Set exposure automatically
                cam_open.AcquisitionMode.set('Continuous') # Or 'SingleFrame' if only one frame per trigger needed

                # Set the trigger source to Software
                cam_open.TriggerSelector.set('FrameStart') # Select the trigger event to control
                cam_open.TriggerSource.set('Software') # Use software trigger as the source
                cam_open.TriggerMode.set('On') # Enable triggering

                # Start asynchronous acquisition
                # The frame_handler will be called for each received frame
                cam_open.start_streaming(handler=frame_handler, buffer_count=10)
                print("Camera streaming started. Waiting for triggers...")

                # Manually trigger frames in a loop
                for i in range(5):
                    time.sleep(.4) # Wait a second between triggers
                    print(f"--- Running software trigger {i+1}/5 ---")
                    # Execute the TriggerSoftware command
                    cam_open.TriggerSoftware.run()
                    # print(cam_open.AcquisitionStatus.get())
                    # Wait briefly for the frame to be acquired and handled
                
                print("Triggering finished.")
                time.sleep(2)
            except VmbFeatureError as e:
                print(f"Error setting camera features: {e}")
            finally:
                # Stop acquisition and streaming
                cam_open.stop_streaming()
                print("Camera streaming stopped.")

if __name__ == '__main__':
    software_trigger_example()
