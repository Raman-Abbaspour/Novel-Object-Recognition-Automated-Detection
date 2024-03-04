from tkinter import *
import pandas as pd
import numpy as np
from PIL import ImageTk, Image
from tkinter import messagebox as mb
from os import path
import cv2
import math
import random




def annotate(video_loc,out_loc,analyze_button):
    global final_data
    final_data = pd.DataFrame({"type": [], "xmin": [], "xmax": [], "ymin": [],
                               "ymax": []})  # Type of Box, ObjectLeft, ObjectRight, ObjectUP, ObjectDown

    randomVideo = random.choice(video_loc)
    try:
        video = cv2.VideoCapture(randomVideo)

    except:
        mb.showerror("Invalid video", "One or more videos cannot be read. Please try choosing other videos.")
        print("exception")
        return

    video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_FRAME_COUNT)//2)
    ret, img = video.read()

    if not path.exists(out_loc):
        mb.showerror("No such file or directory", "The output location is invalid. Please try again")
        return

    open_annotate_window(img,analyze_button)







def open_annotate_window(frame,analyze_button):




    def draw(w, color):
        # Hovering
        vertical_line = w.create_line(0, 0, 0, 0, dash=(3, 1), fill=color)
        horizontal_line = w.create_line(0, 0, 0, 0, dash=(3, 1), fill=color)
        w.bind("<Motion>", lambda event: draw_dashed_line(event, vertical_line, horizontal_line, "motion"))
        w.bind("<Leave>", lambda event: draw_dashed_line(event, vertical_line, horizontal_line, "leave"))


        tag = str(np.random.randint(-10000,0))
        w.bind("<Button-1>", lambda event: test(event, w,vertical_line,horizontal_line, name="start", color=color))
        w.bind("<B1-Motion>", lambda event: test(event, w,vertical_line,horizontal_line, name="motion"))
        w.bind("<ButtonRelease-1>", lambda event: test(event, w,vertical_line,horizontal_line, name="end", color=color, tag=tag))




    def draw_dashed_line(event,vertical_line,horizontal_line, action):
        if action =="motion":
            x,y = event.x, event.y
            w.coords(vertical_line, x,0,x,canvas_height)
            w.coords(horizontal_line, 0, y, canvas_width, y)
        else:
            w.coords(vertical_line,0,0,0,0)
            w.coords(horizontal_line,0,0,0,0)



    def undo():
        global black_thresh
        global final_data
        global is_novel
        global is_fam
        global is_distance
        w.delete(tags[-1])
        if colors[-1] == "green":
            buttons[1].configure(state="active")
            okay.pop(-1)

        elif colors[-1] == "blue":
            buttons[0].configure(state="active")
            okay.pop(-1)

        elif colors[-1] == "red":
            black_thresh +=1
            buttons[2].configure(state="active")
        else:
            size.place_forget()
            buttons[3].configure(state="active")
            okay.pop(-1)
        tags.pop(-1)
        colors.pop(-1)
        final_data = final_data.iloc[0:-1]

    def restart():
        global black_thresh
        global final_data
        black_thresh = 4
        for i in tags:
            w.delete(i)
        for i in buttons:
            i.configure(state="active")
        size.place_forget()
        size.delete(0, 'end')
        tags.clear()
        colors.clear()
        final_data=final_data.iloc[0:0]

    def cancel():
        global final_data
        final_data = final_data.iloc[0:0]
        master.destroy()

    def test(event, w,vertical_line,horizontal_line, name, tag=0, color="white"):
        global total_lenght
        global is_novel
        global is_fam
        global is_distance


        global black_thresh
        global final_data
        if name == "start":
            w.delete(vertical_line)
            w.delete(horizontal_line)
            x1, y1 = event.x, event.y
            if color != "black":
                myrect = w.create_rectangle(x1, y1, x1, y1, outline=color, width=2, tags="origin")
            else:
                myrect = w.create_line(x1, y1, x1, y1, fill=color, width=2, tags="origin")
            list.append(myrect)
            list.append(x1)
            list.append(y1)
            # print("start")
        if name == "motion":
            x2, y2 = event.x, event.y

            w.coords(list[0], list[1], list[2], x2, y2)

            # print("motion")
        elif name == "end":
            x2, y2 = event.x, event.y
            # print(tag)
            w.delete("origin")
            if color != "black":
                w.create_rectangle(list[1], list[2], x2, y2, outline=color, width=4, tags=tag)

            else:

                size.place(relx=0.02, rely=0.35)
                w.create_line(list[1], list[2], x2, y2,  fill=color, width=4, tags=tag)

            if color != "black":
                final_data = final_data.append({"type": color, "xmin": min(list[1],x2)*width_factor, "xmax": max(list[1],x2)*width_factor,
                                            "ymin": min(list[2],y2)*height_facotr, "ymax": max(list[2],y2)*height_facotr},
                                                     ignore_index=True)
            else:
                total_lenght = np.sqrt(((list[1]-x2)*width_factor)**2 + ((list[2]-y2)*height_facotr)**2)
                is_distance =True
                print(total_lenght)




            list.clear()
            tags.append(tag)
            colors.append(color)
            # print(min(list[1],x2))
            w.unbind("<Button-1>")
            w.unbind("<B1-Motion>")
            w.unbind("<ButtonRelease-1>")

            if color == "green":
                buttons[1].configure(state="disable")
                okay.append(1)

            elif color == "blue":
                buttons[0].configure(state="disable")
                okay.append(1)

            elif color == "red":
                black_thresh -= 1
                # open_annotate_window(draw(w, "black"))
                if black_thresh == 0:
                    buttons[2].configure(state="disable")
            else:
                buttons[3].configure(state="disable")
                okay.append(1)

            # print(final_data)

    def done():
        global pixle_to_cm_ratio
        try:
            if sum(okay) == 3:
                pass
            else:
                mb.showerror("Incomplete Data Entry", "One or more annotation is missing.")
            pixle_to_cm_ratio = total_lenght /float(size.get())
            # print(pixle_to_cm_ratio)
            analyze_button["state"]="normal"

            master.destroy()
        except:
            mb.showerror("Invalid Distance", "Please make sure the distance provided is correct.")




    frame_height, frame_width, _ = frame.shape
    aspect_ratio = frame_width / frame_height

    global img
    img = frame
    global tags
    global height_facotr
    global width_factor
    global buttons
    buttons = []
    global black_thresh
    black_thresh = 4

    global okay
    okay=[]

    list = []
    tags = []
    colors = []


    canvas_height = 900
    canvas_width = math.floor(canvas_height * aspect_ratio)
    height_facotr = frame_height/canvas_height
    width_factor = frame_width/canvas_width

    # The new window
    master = Toplevel()
    master.geometry("1780x920")
    master.title("Annotation")
    master.resizable(False, False)

    #Canvas
    w = Canvas(master,
               width=canvas_width,
               height=canvas_height,
               bg="white")
    w.place(anchor = NW, relx =0.1 ,rely=0 )
    img = ImageTk.PhotoImage(Image.fromarray(img).resize((canvas_width,canvas_height)))
    w.create_image(0, 0, image=img, anchor=NW,tags= "image")

    #Buttons
    b1 = Button(master, text="Novel Object", command=lambda: draw(w, "blue"))
    b2 = Button(master, text="Familiar Object", command=lambda: draw(w, "green"))
    b3 = Button(master, text="Thigmotaxis", command=lambda: draw(w, "red"))
    b4 = Button(master, text="Distance", command=lambda: draw(w, "black"))
    b5 = Button(master, text="Undo", command=undo).place(relx=0.02, rely=0.4)
    b6= Button(master, text="Restart", command=restart).place( relx =0.02 ,rely=0.5 )

    size = Entry(master, width=20)
    size.insert(0, "Length in cm")

    buttons.append(b1)
    buttons.append(b2)
    buttons.append(b3)
    buttons.append(b4)

    b1.place( relx =0.02 ,rely=0.04 )
    b2.place(relx =0.02 ,rely=0.14 )
    b3.place(relx =0.02 ,rely=0.24 )
    b4.place(relx=0.02, rely=0.3)

    b6 = Button(master, text="Done", command=done)

    b6.place( relx =0.02 ,rely=0.7 )
    exit = Button(master, text="Cancel", command=cancel).place( relx =0.02 ,rely=0.9 )


    master.mainloop()