import pygame
import requests
from io import BytesIO
import threading
import time
import paho.mqtt.client as mqtt
import requests, re
import urllib, os

current_media = {}
prev_url = ""

IMDB_KEY = " eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZWNlMmQzM2RlOGQzY2U2MGEwMDI2YjcxOTQ1Zjk5NSIsIm5iZiI6MTczNjY0ODU5Ni43Nywic3ViIjoiNjc4MzI3OTQxMzZlMTU3Y2YyN2IxY2U5Iiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.2saEcfF4A0bx80s11Pcze88F50-Icaogp_badqPrX_8"
os.system("DISPLAY=:0 unclutter -idle 0 &")
def split_title_and_year(input_string):
    # Use a regex pattern to extract the title and optional year
    match = re.match(r"^(.*?)\s*(?:\((\d{4})\))?$", input_string)
    if match:
        title, year = match.groups()
        return title.strip(), year  # `year` will be `None` if not present
    else:
        return input_string.strip(), None  # Return the input and `None` if no match

def get_poster(title):
    global current_media
    if " |" in title:
        title = title.split(" |")[0]
    title, year = split_title_and_year(title)
    url = f"https://api.themoviedb.org/3/search/multi?query={urllib.parse.quote(title)}&include_adult=false&language=en-US"
    if year is not None:
        url+f'&primary_release_year={year}'

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {IMDB_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if (len(data["results"]) == 0):
        current_media['poster_path'] = None
        return
    
    url = "https://image.tmdb.org/t/p/w500/"+data["results"][0]["poster_path"]

    
    current_media['poster_path'] = "https://image.tmdb.org/t/p/w500/"+data["results"][0]["poster_path"]
    current_media['overview'] = "https://image.tmdb.org/t/p/w500/"+data["results"][0]["overview"]
    #current_media['name'] = "https://image.tmdb.org/t/p/w500/"+data["results"][0]["name"]
    
# Global variable to store the current image URL
#current_image_url = "https://m.media-amazon.com/images/I/81vj15-NuoL._AC_UF894,1000_QL80_.jpg"
lock = threading.Lock()  # Lock to manage thread-safe access to `current_image_url`

# def display_image_fullscreen():
#     global current_media, prev_url, image_data
#     # Initialize Pygame
#     pygame.init()

#     def set_fullscreen():
#         screen = pygame.display.set_mode((1080, 1920), pygame.FULLSCREEN)
#         return screen

#     screen = set_fullscreen()

#     # Set up the display (1080x1920 fullscreen)
#     pygame.display.set_caption("poster")

#     running = True
#     while running:
#         #print(current_media)
#         #with lock:
#         image_url = current_media.get("poster_path", None)

#         if (image_url is None ):
#             #os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --off")
#             #screen = set_fullscreen()
#             if (image_url is None):
#                 pass
#                 #screen.fill((0,0,0))    
#                 #pygame.display.update()    
#             time.sleep(1)
#             continue  
        
#         try:
#             #time.sleep(2)
#             #screen = set_fullscreen()
#             #if not pygame.display.get_surface():
#             #screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#             #screen = pygame.display.set_mode((1080, 1920), pygame.FULLSCREEN)
#             print(image_url)
#             # Download the image from the web
#             #if image_url != prev_url:
#             response = requests.get(image_url)
#             prev_url = image_url
#             image_data = BytesIO(response.content)
#             image = pygame.image.load(image_data)

#             target_width = 1080
#             target_height = 1920
#             original_width, original_height = image.get_size()


#             # Calculate the aspect ratio of the original image
#             aspect_ratio = original_width / original_height

#             # Determine the new dimensions while maintaining the aspect ratio
#             if target_width / target_height > aspect_ratio:
#                 # Scale based on target height
#                 new_height = target_height
#                 new_width = int(target_height * aspect_ratio)
#             else:
#                 # Scale based on target width
#                 new_width = target_width 
#                 new_height = int(target_width / aspect_ratio )

#             # Scale the image to the new dimensions
#             scaled_image = pygame.transform.scale(image, (new_width, new_height))

#             # Optionally, you can center the image if needed
#             x_offset = (target_width - new_width) // 2
#             y_offset = (target_height - new_height) // 2
#             fade_duration = 1;
#             step_size = fade_duration/255
#             # for i in range(0, 255, 1):
#             #     screen.fill((0,0,0))    
#             #     scaled_image.set_alpha(int(i)  )  
#             #     screen.blit(scaled_image, (x_offset, 250))
#                 #pygame.display.update()    
           
#             # Display the image
#             screen.blit(scaled_image, (x_offset, 280))
            
#             font = pygame.font.Font(None, 185)  # You can change the size of the text here

#             # Render the text (white color)
#             text = font.render('NOW PLAYING', True, (255, 255, 255))  # White color text

#             # Get the position for the text (e.g., centered over the image)
#             text_rect = text.get_rect(center=(target_width // 2, 140))

#             # Blit the text over the image
#             screen.blit(text, text_rect)
#             #screen = set_fullscreen()
#             pygame.display.flip()
#             pygame.display.update()    
#             #os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --on")
#             time.sleep(0.5)
#             os.system('wmctrl -r "window_title" -e 0,0,0,0,0')
#             # if not pygame.display.get_surface():
#             #     screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#         except Exception as e:
#             print(f"Error fetching image: {e}")

#         # # Check for quit events
#         # for event in pygame.event.get():
#         #     if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
#         #         running = False
#         #     elif event.type == pygame.QUIT:
#         #         running = False

#         # # Refresh every 2 seconds (adjust as needed)
#         time.sleep(0.1)

#     # Quit Pygame
#     pygame.quit()

def mqtt_listener():
    global current_image_url

    def on_connect(client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe("current/movie")  # Replace with your topic

    def on_message(client, userdata, msg):
        title = msg.payload.decode()
        get_poster(title)
        if 'poster_path' in current_media and current_media['poster_path']:
           #client.publish("current/url", current_media['poster_path'])
           os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --on")
        else:
           os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --off")
        
    # Initialize MQTT client
    client = mqtt.Client()
    client.username_pw_set("mqtt_user", "mqtt_pass")
    client.on_connect = on_connect
    client.on_message = on_message

    connected = False
    while not connected:
        try:
        # Connect to the broker
            broker_address = "10.6.0.19"  # Replace with your MQTT broker address
            client.connect(broker_address, 1883, 60)
            connected = True
        except Exception as e:
            print(e)
            time.sleep(1)
        


    # Start the MQTT client loop
    client.loop_forever()
    # while True:
    #     if 'poster_path' in current_media and current_media['poster_path']:
    #        #client.publish("current/url", current_media['poster_path'])
    #        os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --on")
    #     else:
    #        os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --off")
    #     time.sleep(0.1)
def manage_backlight():
    while True:
        if 'poster_path' in current_media and current_media['poster_path']:
            os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --o")
        else:
            os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --off")
    
def main():
    # Create and start threads
    image_thread = threading.Thread(target=manage_backlight, daemon=True)
    mqtt_thread = threading.Thread(target=mqtt_listener, daemon=True)

    image_thread.start()
    mqtt_thread.start()
    time.sleep(1)
    os.system("DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 wlr-randr --output HDMI-A-1 --off")

    # Keep the main thread alive
    #image_thread.join()
    mqtt_thread.join()

main()
