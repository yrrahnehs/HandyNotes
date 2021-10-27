import os
import os.path
import threading
import tkinter.messagebox
import tkinter.simpledialog
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE
from tkinter import *

from pynput.keyboard import Listener, Key

checking = False
pressed = False
found = False
lock = threading.Lock()
url = ""
root = Tk()
root.title("Handy Notes")


# checks key pressed
def on_press(key):
    global root, lock, found, url, pressed, p1
    if key == Key.f9:
        lock.release()
        root.after(10)
        root.deiconify()
        return False
    if key == Key.f8:
        pressed = True
        # gets the active chrome tab URL
        cmd = "osascript -e 'tell app \"Chrome\"' -e 'get URL of active tab of window 1' -e 'end tell'"
        pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        urls = pipe.readlines()

        # the url of the active tab website
        url = str(urls[0])[2:-3]

        # if the url of the tab is in the xml file
        error = False
        for site in treeroot:
            if str(url) in (site.attrib['url']):
                found = True
                # if filename is found, open
                if os.path.exists(site.attrib['name']):
                    os.system('open -t {0}'.format(site.attrib['name']))
                    break
                # else remove it from the xml file, and update the file
                else:
                    treeroot.remove(site)
                    tree.write("filenames.xml")
                    error = True
                    break
            else:
                found = False

        if error == True:
            show_error_messagebox()

        if found == False:
            show_simple_dialogue()


# shows an error message box if the file is not found
def show_error_messagebox():
    global lock, root
    lock.release()
    lock.acquire()
    tkinter.messagebox.showerror(title="File Not Found", message="The file name was not found")


# dialogue box for a new note
def show_simple_dialogue():
    global lock, root, url, found
    root.after(100)
    USER_INP = (tkinter.simpledialog.askstring(title="Enter a Title", prompt="Title of the Note :"))
    root.after(50)
    title = (str(USER_INP))
    lock.release()

    # if user inputs no title
    if len(title) == 0:
        # checks to see if a file called "untitled" exists
        untitled_title = False
        for site in treeroot.findall("site"):
            if "untitled.txt" in site.attrib["name"]:
                untitled_title = True

        # loops to see if untitled1 to untitledX exists, then gives out
        # the latest untitled text file number
        iteration = 1
        for j in range(1, len(treeroot.findall("site"))):
            for site in treeroot.findall("site"):
                if ("untitled" + str(j) + ".txt") in site.attrib["name"]:
                    iteration = j + 1
                    break

        # if untitled is not found, title will be untitled
        if not untitled_title:
            title = "untitled"
        else:
            title = "untitled" + str(iteration)

    title = title.replace(" ", "_")
    # sets filename to whichever is the title
    filename = (title + ".txt")

    child = ET.SubElement(treeroot, "site")
    child.tail = "\n"
    child.set("url", url)
    child.set("name", filename)
    tree = ET.ElementTree(treeroot)
    tree.write("filenames.xml")

    with open(filename, 'w') as f:
        f.write(url)
        f.close()

    os.system('open -t {0}'.format(filename))
    found = False
    lock.acquire()


# help screen
def show_help_screen():
    tkinter.messagebox.showinfo(title="HELP", message="Press the Start button, then press F8 to taking notes\n\n"
                                                      "Press F9 once you are done taking notes to exit")


# starts listener
def start_listener():
    with Listener(on_press=on_press) as listener:
        listener.join()


# Starts a keyboard listener thread
def listener_thread():
    global root, checking, p1
    p1 = threading.Thread(target=start_listener)
    p1.start()
    root.after(10)
    root.withdraw()
    lock.acquire()


if __name__ == '__main__':
    # if xml file exists, set tree to it, else make a new xml file named filenames
    if os.path.exists("filenames.xml"):
        tree = ET.parse('filenames.xml')
    else:
        file = open("filenames.xml", "w")
        file.write("<websites>\n</websites>")
        file.close()
        tree = ET.parse('filenames.xml')

    treeroot = tree.getroot()

    # setting up root window at center of screen
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - h
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # sets up the buttons on root window
    startbutton = Button(text="START", command=listener_thread)
    startbutton.place(relx=0.5, rely=0.4, anchor=CENTER)
    helpbutton = Button(text=" HELP ", command=show_help_screen)
    helpbutton.place(relx=0.5, rely=0.6, anchor=CENTER)
    quitbutton = Button(text=" QUIT ", command=quit)
    quitbutton.place(relx=0.5, rely=0.8, anchor=CENTER)

    root.mainloop()
