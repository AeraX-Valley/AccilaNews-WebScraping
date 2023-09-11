from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np
import cv2
import time
import tensorflow as tf
import numpy as np

driver = webdriver.Chrome()
reloaded = tf.saved_model.load("accilanews_resnet_model_95")
driver.set_window_size(400, 400)
tick = 0

def predict(img, threshold = 85):
    # img_path = "dataset/test/Accident/test24_30.jpg"
    img = np.expand_dims(tf.keras.utils.img_to_array(img), axis=0)
    start_time = time.time()
    prediction, label = reloaded(img)
    print("--- %s seconds ---" % (time.time() - start_time))
    label = [i.numpy().decode("utf-8") for i in label]

    print(label)
    print(label[prediction.numpy().argmax()])
    acc_array = (prediction.numpy() * 100).flatten()
    print(acc_array)
    print("Threshold :",threshold)
    
    if acc_array[0] > threshold:
        print("Accident")
    else:
        print("Non Accident")

    print("")
    

while True:
    if tick % 30 == 0:
        print(tick)
        driver.get("http://www.bmatraffic.com/index.aspx")
        driver.get("http://www.bmatraffic.com/PlayVideo.aspx?ID=1629")
        image = driver.find_element(By.XPATH, '//*[@id="webcamera"]')

    image_url = image.get_attribute("src")
    # print(image_url)

    try:
        # resp = requests.get(image_url,stream=True)
        # arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        # img = cv2.imdecode(arr, -1)
        
        screenshot = driver.get_screenshot_as_png()
        nparr = np.frombuffer(screenshot, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (224, 224))
        predict(img)
        # print(img)
        # cv2.imshow('random_title', img)
        # key = cv2.waitKey(1)
        # if key == 27:  # Press 'Esc' key to exit
        #     break
        
    except Exception as exep:
        print(exep)

    tick += 1
    

    time.sleep(0.5)

    
