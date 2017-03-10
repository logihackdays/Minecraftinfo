"""
logi_arx.py : Defines the exported functions for the API

Logitech Gaming Arx Control SDK

Copyright (C) 2011-2015 Logitech. All rights reserved.
Author: Tom Lambert
Email: devtechsupport@logitech.com
"""
import ctypes
import os
import platform
import time
import json

# DLL Definitions
#
LOGI_ARX_ORIENTATION_PORTRAIT  = 0x01
LOGI_ARX_ORIENTATION_LANDSCAPE = 0x10

LOGI_ARX_EVENT_FOCUS_ACTIVE         = 0x01
LOGI_ARX_EVENT_FOCUS_INACTIVE       = 0x02
LOGI_ARX_EVENT_TAP_ON_TAG           = 0x04
LOGI_ARX_EVENT_MOBILEDEVICE_ARRIVAL = 0x08
LOGI_ARX_EVENT_MOBILEDEVICE_REMOVAL = 0x10

LOGI_ARX_DEVICETYPE_IPHONE         = 0x01
LOGI_ARX_DEVICETYPE_IPAD           = 0x02
LOGI_ARX_DEVICETYPE_ANDROID_SMALL  = 0x03
LOGI_ARX_DEVICETYPE_ANDROID_NORMAL = 0x04
LOGI_ARX_DEVICETYPE_ANDROID_LARGE  = 0x05
LOGI_ARX_DEVICETYPE_ANDROID_XLARGE = 0x06
LOGI_ARX_DEVICETYPE_ANDROID_OTHER  = 0x07

CALLBACK_DEFINITION = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_void_p)

global arx_dll
global on_callback
global callback_ref

class arxAppCallbackMessage(ctypes.Structure):
    """ creates a struct to match arxAppCallbackMessage. """
    _fields_ = [
        ('eventType', ctypes.c_int),
        ('eventValue', ctypes.c_int),
        ('eventArg', ctypes.c_wchar * 120)
    ]

class logiArxCbContext(ctypes.Structure):
    """ creates a struct to match logiArxCbContext. """
    _fields_ = [
        ('arxCallBack', CALLBACK_DEFINITION),
        ('arxContext', ctypes.c_void_p)
    ]

def callback_wrapper(event_type, event_value, event_arg, context):
    on_callback(event_type, event_value, event_arg, context)

def default_callback(event_type, event_value, event_arg, context):
    print ('\n[Arx] default_callback called with: event_type = {event_type}, event_value = {event_value}, event_arg = {event_arg}, context = {context}'.format(
        event_type = event_type, event_value = event_value, event_arg = event_arg, context = context))

# Required Globals
#
class SDKNotFoundException:
    pass
    #print("SDK not found")

def load_dll(path_dll = None):
    if not path_dll:
        bitness = 'x86' if platform.architecture()[0] == '32bit' else 'x64'
        subpath_dll = (r'/Logitech Gaming Software/SDK/Arx Control/{}/LogitechGArxControl.dll').format(bitness)
        subpath_lgs = os.environ['ProgramW6432'] if os.environ['ProgramW6432'] else os.environ['ProgramFiles']
        path_dll = subpath_lgs + subpath_dll
    if os.path.exists(path_dll):
        try:
            print("load dll")
            return ctypes.cdll.LoadLibrary(path_dll)
        except:
            print("load dll fail")
    else:
        raise SDKNotFoundException('The SDK DLL was not found.')

try:
    arx_dll = load_dll()
except SDKNotFoundException as exception_sdk:
    print("sdk not found")
    arx_dll = None
    on_callback = None
except:
    print("Unknown Error")

# Wrapped SDK Functions
#
def logi_arx_init(identifier, friendly_name, py_callback_function = None):
    """ initializes the applet on the app with the given friendly_name. """
    if arx_dll:
        global on_callback
        global callback_ref
        on_callback   = py_callback_function if py_callback_function else default_callback
        callback_ref  = ctypes.byref(CALLBACK_DEFINITION(callback_wrapper))
        identifier    = ctypes.c_wchar_p(identifier)
        friendly_name = ctypes.c_wchar_p(friendly_name)
        print("load arx_init")
        return bool(arx_dll.LogiArxInit(identifier, friendly_name, callback_ref))
    else:
        return False

def logi_arx_add_file_as(file_path, file_name, mime_type = None):
    """ sends a file to the device from local a file_path and assigns a file_name to it. mime_type, if assigned, specifies the MIME type of the file. """
    if arx_dll:
        file_path = ctypes.c_wchar_p(file_path)
        file_name = ctypes.c_wchar_p(file_name)
        mime_type = ctypes.c_wchar_p(mime_type) if mime_type else ctypes.c_wchar_p('')
        print("load arx add file as")
        return bool(arx_dll.LogiArxAddFileAs(file_path, file_name, mime_type))
    else:
        return False

def logi_arx_add_content_as(content, size, file_name, mime_type = None):
    """ sends content to the device and saves it to a virtual file called file_name. mime_type, if assigned, specifies the MIME type of the file. """
    if arx_dll:
        content   = ctypes.c_void_p(content)
        size      = ctypes.c_int(size)
        file_name = ctypes.c_wchar_p(file_name)
        mime_type = ctypes.c_wchar_p(mime_type) if mime_type else ctypes.c_wchar_p('')
        print("load arx add content as")
        return bool(arx_dll.LogiArxAddContentAs(content, size, file_name, mime_type))
    else:
        return False

def logi_arx_add_utf8_string_as(string_content, file_name, mime_type = None):
    """ sends a UTF8 string to the device and saves it to a virtual file called file_name. mime_type, if assigned, specifies the MIME type of the file. """
    if arx_dll:
        string_content = ctypes.c_wchar_p(string_content)
        file_name      = ctypes.c_wchar_p(file_name)
        mime_type      = ctypes.c_wchar_p(mime_type) if mime_type else ctypes.c_wchar_p('')
        print("logi arx add utf 8 string")
        return bool(arx_dll.LogiArxAddUTF8StringAs(string_content, file_name, mime_type))
    else:
        return False

def logi_arx_add_image_from_bitmap(bitmap, width, height, file_name):
    """ compresses the image specified by the BGRA byte array bitmap (interpretting the array using width and height) into a png file with the name specified by file_name,
    then sends it over to the the device. note that the color bit order is BGRA rather than standard RGBA bit order. """
    if arx_dll:
        bitmap    = ctypes.c_char_p(bitmap)
        width     = ctypes.c_int(width)
        height    = ctypes.c_int(height)
        file_name = ctypes.c_wchar_p(file_name)
        print("logi arx add image from bitmap")
        return bool(arx_dll.LogiArxAddImageFromBitmap(bitmap, width, height, file_name))
    else:
        return False

def logi_arx_set_index(file_name):
    """ sets which of the sent files is the index. (first one to be displayed in the applet) """
    if arx_dll:
        file_name = ctypes.c_wchar_p(file_name)
        print("logi arx set index")
        return bool(arx_dll.LogiArxSetIndex(file_name))
    else:
        return False

def logi_arx_set_tag_property_by_id(tag_id, prop, new_value):
    """ change at runtime a prop (property) on the tag with the id tag_id from the old value to the new_value. """
    if arx_dll:
        tag_id    = ctypes.c_wchar_p(tag_id)
        prop      = ctypes.c_wchar_p(prop)
        new_value = ctypes.c_wchar_p(new_value)
        print("logi arx set tag property by id")
        return bool(arx_dll.LogiArxSetTagPropertyById(tag_id, prop, new_value))
    else:
        return False

def logi_arx_set_tags_property_by_class(tag_class, prop, new_value):
    """ change at runtime a prop (property) on the tag with the class tag_class from the old value to the new_value. """
    if arx_dll:
        tag_class = ctypes.c_wchar_p(tag_class)
        prop      = ctypes.c_wchar_p(prop)
        new_value = ctypes.c_wchar_p(new_value)
        print("logi arx set tag property by class")
        return bool(arx_dll.LogiArxSetTagsPropertyByClass(tag_class, prop, new_value))
    else:
        return False

def logi_arx_set_tag_content_by_id(tag_id, new_content):
    """ change at runtime the content (innerHTML) of a tag with the id tag_id from the old content to the new_content. """
    if arx_dll:
        tag_id      = ctypes.c_wchar_p(tag_id)
        new_content = ctypes.c_wchar_p(new_content)
        print("logi arx set tag content by id")
        return bool(arx_dll.LogiArxSetTagContentById(tag_id, new_content))
    else:
        return False

def logi_arx_set_tags_content_by_class(tag_class, new_content):
    """ change at runtime the content (innerHTML) of a tag with the class tag_class from the old content to the new_content. """
    if arx_dll:
        tag_class   = ctypes.c_wchar_p(tag_class)
        new_content = ctypes.c_wchar_p(new_content)
        print("logi arx set tag content by class")
        return bool(arx_dll.LogiArxSetTagsPropertyByClass(tag_class, new_content))
    else:
        return False

def logi_arx_get_last_error():
    """ each function returns a bool. to get detailed info on the last error code, call this function. """
    if arx_dll:
        print("logi arx get last error")
        return int(arx_dll.LogiArxGetLastError())
    else:
        return False

def logi_arx_shutdown():
    """ shuts down the applet on the app. """
    if arx_dll:
        arx_dll.LogiArxShutdown()
        print("logi arx shutdown")
        return True
    else:
        return False

def custom_callback(event_type, event_value, event_arg, context):
    if event_arg and event_arg == 'splash-icon':
        print ("Chest clicked !!!!")
            
print ('Setting up a Minecraft applet...')
n = 0
while (n != -1):
    os.system('cls')
    with open('C:/Users/ABC/AppData/Roaming/.minecraft/saves/Logi/stats/c8ffe9c4-02e5-4519-ad86-deec6eb79759.json') as data_file:
#with open('c8ffe9c4-02e5-4519-ad86-deec6eb79759.json') as data_file:
        data = json.load(data_file)
        data_file.close()
        print("Reading json file...")

    index = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1, target-densityDpi=device-dpi, user-scalable=no" />
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <font size="40"><h2 align="center">MineCraft Data Scratch</h2></font>
        
        <div class="polaroid" >
            <div class="container" >
                <font size="25"><p id ="number" ><strong>Loop number</strong></p></font>
            </div>
        </div>

        <div class="polaroid" >
          <img src="https://media-elerium.cursecdn.com/avatars/67/272/636163093083287938.png" alt="Norway" style="width:25%" id="splash-icon">
          <div class="container" >
            <font size="25"><p id ="number1" >WOWWWWWW</p></font>
          </div>
        </div>
    </body>
    </html>
    """
    
    css = """
    body  {
                background-image: url("https://lh4.ggpht.com/b3UXdRvHfNuMt3L4mHwI2iKYfWAvjFEaQSUzksKpPFlW8PYO3IpJTM5RgNhJ6rYRAdU=h800");
                background-size: cover;
            }
            body {margin:25px;}
            div.polaroid {
                width: 80%;
                background-color: white;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                margin-bottom: 25px;
            }

            div.container {
                text-align: center;
                padding: 10px 20px;
            }
    
    """
    add_string = ''
    add_string += "跳躍次數: "+str(data['stat.jump'])+"<br>"
    #print ("跳躍次數:",data['stat.jump'])
    add_string += "離開遊戲次數: "+str(data['stat.leaveGame'])+"<br>"
    #print ("離開遊戲次數:",data['stat.leaveGame'])
    add_string += "行走距離: "+str(data['stat.walkOneCm'])+"<br>"
    #print ("行走距離:",data['stat.walkOneCm'])
    add_string += "飛行距離: "+str(data['stat.flyOneCm'])+"<br>"
    #print ("飛行距離:",data['stat.flyOneCm'])
    add_string += "物品掉落總次數: "+str(data['stat.drop'])+"<br>"
    #print ("物品掉落總次數:",data['stat.drop'])
    add_string += "遊戲總時間: "+str(data['stat.playOneMinute'])+"<br>"
    #print ("遊戲總時間:",data['stat.playOneMinute'])
    add_string += "上次死亡之後生存的時間: "+str(data['stat.timeSinceDeath'])+"<br>"
    #print ("上次死亡之後生存的時間:",data['stat.timeSinceDeath'])
    #print(add_string)
#print (":",data['stat.mineBlock.minecraft.log'])
#print (":",data['stat.pickup.minecraft.log'])
#print (":",data['stat.pickup.minecraft.sapling'])
#print (":",data['stat.pickup.minecraft.dirt'])
#print (":",data['stat.drop.minecraft.log'])
#print (":",data['achievement.exploreAllBiomes'])
#print (":",data['stat.mineBlock.minecraft.tallgrass'])

    #f = open('index1.html','w')
    logi_arx_init("com.logitech.gaming.minecraft", "Minecraft", custom_callback)
    time.sleep(1)
    logi_arx_add_utf8_string_as(index, 'index.html', 'text/html')
    #f.write(index)
    #f.close()
    logi_arx_add_utf8_string_as(css, 'style.css', 'text/css')
    if(n == 0):
        logi_arx_set_index('index.html')
        n += 1
        time.sleep(3)
    else:
        logi_arx_set_tag_content_by_id("number","Loop number : "+str(n))
        logi_arx_set_tag_content_by_id("number1",add_string)
        n += 1
        time.sleep(3)