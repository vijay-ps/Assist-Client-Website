import pyaudiowpatch as pyaudio

def list_devices():
    p = pyaudio.PyAudio()
    print("Scanning for WASAPI Loopback devices...\n")
    
    try:
        # Get WASAPI host API info
        wasapi_info = None
        for i in range(p.get_host_api_count()):
            api = p.get_host_api_info_by_index(i)
            if api["name"] == "Windows WASAPI":
                wasapi_info = api
                break
        
        if not wasapi_info:
            print("WASAPI not found on this system.")
            return

        # Iterate through all devices
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            
            # Check if device belongs to WASAPI
            if dev["hostApi"] == wasapi_info["index"]:
                # Check if it is a loopback device
                # Loopback devices usually appear as input devices with "Loopback" in the name 
                # OR they are output devices that we can record from via loopback flag (handled by pyaudiowpatch)
                
                print(f"Index: {dev['index']}")
                print(f"Name: {dev['name']}")
                print(f"Sample Rate: {dev['defaultSampleRate']}")
                print(f"Channels: {dev['maxInputChannels']} (In) / {dev['maxOutputChannels']} (Out)")
                
                if dev["isLoopbackDevice"]:
                     print("Type: LOOPBACK DEVICE (Target this!)")
                else:
                    print("Type: Standard Device")
                print("-" * 30)
                
    finally:
        p.terminate()

if __name__ == "__main__":
    list_devices()
