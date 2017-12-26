import time
import urllib.request
import os
import random
import winsound
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------  USER INPUT ------------------------ #

email_input = ''                             # Your FB email address/username
password_input = ''                          # Your FB password. Don't worry, your data is safe. :)
group_id = '1477319032584253'                # The group id/name, whose member's collage is to be made.

folder = 'E:\Python\Personal Projects\Collage'
''' The folder where the images of the group members are stored. Do note that all the images 
in this folder will be used in the collage. So do not keep any images apart from the group member pictures here. '''

shuffle = 'YES'                                             # Replace 'YES' with 'NO' to not shuffle the image order.
output = 'my_collage.png'                                   # Name of the output collage.
width = 900                                                 # Dimensions of the collage
init_height = 72

# -------------------- DO NOT CHANGE ------------------ #

url = 'https://www.facebook.com'
count = 0
name = 1

# --------------- INITIALIZE CHROMEDRIVER ---------------- #

driver = webdriver.Chrome('E:\Python\chromedriver.exe')
driver.get(url)

try:
    WebDriverWait(driver, 15).until(  # Explicit wait to ensure that page has fully loaded
        EC.presence_of_element_located((By.LINK_TEXT, "dummy text"))
    )
except:
    pass

# --------------- LOGIN TO FACEBOOK --------------- #

email = driver.find_element_by_id('email')
pword = driver.find_element_by_id('pass')

email.send_keys(email_input)
pword.send_keys(password_input)
pword.send_keys(Keys.RETURN)

# --------------- ENTER YOUR FACEBOOK GROUP ------------------ #

driver.get('https://www.facebook.com/groups/' + group_id + '/members')

try:
    WebDriverWait(driver, 15).until(  # Explicit wait to ensure that page has fully loaded
        EC.presence_of_element_located((By.LINK_TEXT, "dummy text"))
    )
except:
    pass

# ----------------- REACH THE BOTTOM MOST PART OF THE GROUP MEMBERS PAGE ------------------ #

lastHeight = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(15)
    newHeight = driver.execute_script("return document.body.scrollHeight")
    if newHeight == lastHeight:
        break
    lastHeight = newHeight

# ---------------- DOWNLOAD THE IMAGES AND MOVE THEM TO A DESIRED LOCATION ------------------ #


def download_and_move(src):
    full_name = str(name) + ".png"
    time.sleep(10)
    try:
        urllib.request.urlretrieve(src, full_name)
    except:
        time.sleep(10)
        urllib.request.urlretrieve(src, full_name)

    os.rename("E:\Python\Personal Projects\\" + full_name, "E:\Python\Personal Projects\Collage\\" + full_name)
    # Moves the downloaded images to a user defined folder which should contain only the downloaded images.

# ----------------- FIND ALL THE IMAGES ---------------- #

l = driver.find_element_by_id('groupsMemberSection_recently_joined')
for i in l.find_elements_by_css_selector('._s0._4ooo.img'):
    link = i.get_attribute('src')
    download_and_move(link)
    name += 1
    count += 1
print(count)

# -------------------- MAKE COLLAGE ----------------------- #


def make_collage(images, filename, width, init_height):

    if not images:
        print('No images for collage found!')
        return False

    margin_size = 2

    # Run until a suitable arrangement of images is found
    while True:
        images_list = images[:]                    # Copy images to images_list
        coefs_lines = []
        images_line = []
        x = 0

        while images_list:
            img_path = images_list.pop(0)          # Get first image and resize to `init_height`
            img = Image.open(img_path)
            img.thumbnail((width, init_height))

            # When `x` will go beyond the `width`, start the next line
            if x > width:
                coefs_lines.append((float(x) / width, images_line))
                images_line = []
                x = 0

            x += img.size[0] + margin_size
            images_line.append(img_path)

        coefs_lines.append((float(x) / width, images_line))    # Finally add the last line with images

        # Compact the lines, by reducing the `init_height`, if any with one or less images
        if len(coefs_lines) <= 1:
            break

        if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
            init_height -= 10                                  # Reduce `init_height
        else:
            break

    out_height = 0                                             # Get output height
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            out_height += int(init_height / coef) + margin_size

    if not out_height:
        print('Height of collage could not be 0!')
        return False

    collage_image = Image.new('RGB', (width, int(out_height)), (35, 35, 35))
    # Put images to the collage
    y = 0

    for coef, imgs_line in coefs_lines:
        if imgs_line:
            x = 0
            for img_path in imgs_line:
                img = Image.open(img_path)
                k = (init_height / coef) / img.size[1]

                if k > 1:
                    img = img.resize((int(img.size[0] * k), int(img.size[1] * k)), Image.ANTIALIAS)
                else:
                    img.thumbnail((int(width / coef), int(init_height / coef)), Image.ANTIALIAS)

                if collage_image:
                    collage_image.paste(img, (int(x), int(y)))
                x += img.size[0] + margin_size
            y += int(init_height / coef) + margin_size
    collage_image.save(filename)
    return True

# Get images
files = [os.path.join(folder, fn) for fn in os.listdir(folder)]
images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg', '.jpeg', '.png')]
# print(images)                         # Uncomment to see the image list.

if not images:
    print('No images for making collage! Please select other directory with images!')
    exit(1)

if shuffle == 'YES':
    random.shuffle(images)

print('Making collage...')
res = make_collage(images, output, width, init_height)                 # Make the collage.
if not res:
    print('Failed to create collage!')
    exit(1)

# --------------- SOUND ALERT ON PROCESS COMPLETION -------------- #

print('Collage is ready!')
frequency = 2500
duration = 2000         # In milliseconds.
winsound.Beep(frequency, duration)