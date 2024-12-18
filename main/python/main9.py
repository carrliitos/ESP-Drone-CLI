from espdrone import Espdrone

def main():
  drone = Espdrone()
  try:
    # Connect to the drone
    drone.open_link(drone.link_uri)
    
    # Example: Check connection
    if drone.is_connected():
      print("Drone connected successfully!")
      drone.run()
    
  except Exception as e:
    print(f"Error: {e}")
  finally:
    # Disconnect the drone
    print("Disconnecting..")
    drone.close_link()

if __name__ == "__main__":
  main()
