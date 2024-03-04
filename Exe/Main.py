
from tkinter import *
from tkinter import  filedialog
from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox as mb
from Exploration import Explore
import multiprocessing
from DistanceToObject import Distance
from Annotate import annotate
import Annotate
from ObjectDetection import creat_array
import numpy as np
from threading import Thread
from queue import Queue
from StressAnalysis import stress
import pandas as pd
from DistanceMoved import calculate_distance
import os

import tensorflow as tf
my_devices = tf.config.experimental.list_physical_devices(device_type='CPU')
tf.config.experimental.set_visible_devices(devices= my_devices, device_type='CPU')




# TODO: Help List
#TODO: slow boot up



def choose_file():
    global files
    f = filedialog.askopenfilenames(parent=video_tab, title='Choose one or more file(s)')
    if f:
        files = f
    if files:
        video_list.delete(0, 1000)
        annotate_button["state"] = "normal"
        for index, i in enumerate(files):
            video_list.insert(index, i.split("/")[-1])


def output_loc():
    global out_loc
    out_loc = filedialog.askdirectory(parent=video_tab, title='Choose the output location')
    ouput_entry.delete(0, "end")
    ouput_entry.insert(0, out_loc)


# def validate(input):
#     return input.isdigit()


def show_data():
    Label(root, text=Annotate.final_data).pack()


def analyze():
    # detect_fn = detect_fn

    def output(data, name):

        out_name = ouput_entry.get() + "/" + file_name[-1] + "_" + name + ".csv"
        data.to_csv(out_name, index=False)

    def number(value):
        try:
            return float(value)
        except:
            return 0

    def final_output():
        len_index = len(file_index)

        print(f"Final Ourput {len_index}")

        final_explore[len_index, 0] = len_index

        if len_index < len(files) - 1:
            file_index.append(0)
            initiate_analysis(len(file_index))
        else:

            Final_result = pd.DataFrame(final_explore, columns=["File", "Novel Object Exploration (s)",
                                                                "Familiar Object Exploration (s)",
                                                                "Time on Thigmotaxis (s)", "Distance Moved (cm)",
                                                                "Average Speed (cm/s)"])

            Final_result.iloc[:, 0] = file_name
            print(Final_result)
            Final_result.iloc[:, 1:4] = final_explore[:, 1:4] / int(fps)

            Final_result.to_csv(ouput_entry.get() + "/" + "Final_Data.csv", index=False)
            analyze_button["state"] = ACTIVE

    def check_output_distance():
        try:

            data = pd.read_csv("fgasjbkdfji8723hbdfjhkjs.csv")
            # print("distance done")
            os.remove("fgasjbkdfji8723hbdfjhkjs.csv")

            output(data.sort_values(["Frame"]), "Distance_To_Novel_Familiar_Object")

            final_output()


        except:

            root.after(1000, check_output_distance)

    def check_output_stress():
        try:

            data = pd.read_csv("dfjhdfkjb3i746sdhfjshdfk.csv")
            # print("thig done")

            if isthgsig == 1:
                output(data.sort_values(["Frame Number"]), "Thigmotaxis_signal")

            os.remove("dfjhdfkjb3i746sdhfjshdfk.csv")
            final_explore[len(file_index), 3] = data["Inside Given Area"].sum()
            # print(final_explore)

            # Novel/Familiar Object
            if is_n_f_distance == 1:
                thread = Thread(target=Distance,
                                args=(path[-1], annotated_data, Image_annotate, number(pixle_to_cm_ratio)))
                thread.start()
                root.after(1000, check_output_distance)
            else:
                final_output()




        except:

            root.after(1000, check_output_stress)

    def check_output_exploration():
        try:
            data = pd.read_csv("dfjsdjhf5623jshdafjha.csv")
            print("Exploration Complete")
            # Exploration_data = Exp_queue.get()
            if is_expsig == 1:
                output(data.sort_values(["Frame Number"]), "exploration_signal")

            os.remove("dfjsdjhf5623jshdafjha.csv")
            final_explore[len(file_index), 1] = data["Novel"].sum()
            final_explore[len(file_index), 2] = data["Familiar"].sum()
            # print(final_explore)
            # speed and distance
            if is_speed == 1 or is_distance == 1:
                d = calculate_distance(annotated_data, path[-1]) / pixle_to_cm_ratio

                # print("done distance cal--Meter")
                if is_distance == 1:
                    final_explore[len(file_index), 4] = d
                if is_speed == 1:
                    # TODO: the speed may be inaccurate since the mouse could be stationary
                    s = annotated_data.count()[0] / 2 / int(fps)
                    final_explore[len(file_index), 5] = d / s
                    # print(final_explore)

            # Thgmotaxis
            if is_thig == 1 or isthgsig == 1:
                thread = Thread(target=stress, args=(annotated_data, Image_annotate, path[-1]))
                thread.start()
                root.after(1000, check_output_stress)
            elif is_n_f_distance == 1:

                thread = Thread(target=Distance,
                                args=(path[-1], annotated_data, Image_annotate, number(pixle_to_cm_ratio)))
                thread.start()
                root.after(1000, check_output_distance)
            else:
                final_output()


        except:

            root.after(1000, check_output_exploration)

    global queue
    queue = Queue()

    def check_output_annotation():
        global annotated_data

        if not queue.empty():
            print("Annotation Done.............")
            annotated_data = queue.get()

            # annotated_data.to_csv("testing.csv")
            if is_mouseLoc == 1:
                output(annotated_data, "video_annotation")

            Exp_queue = Queue()
            thread = Thread(target=Explore, args=(
            path[-1], annotated_data, Image_annotate, number(explore_def), number(exp_d), number(pixle_to_cm_ratio),
            number(object_standing), Exp_queue))
            thread.start()
            root.after(2000, check_output_exploration)

        else:
            root.after(1000, check_output_annotation)

    global path
    path = []
    global file_name
    file_name = []

    def initiate_analysis(file_index):

        path.append(files[file_index])

        file_name.append(path[-1].split("/")[-1])
        # Analyzer initiation

        thread = Thread(target=creat_array, args=(path[-1], detect_fn, video_cap, int(fps), queue))
        thread.start()
        # queue.put(pd.read_csv("IMG_4582.csv"))

        root.after(100, check_output_annotation)



    # Settings
    object_standing = obj_stand.get()
    explore_def = expl_def.get()


    if clicked.get() =="Manual Percentage":
        print("try to analyze percent")
        try:
            float(start.get())
            float(end.get())
            print("analyze percent done")
        except:
            mb.showerror("Invalid Video Cap", "The provided video cap is incorrect. Please try again.")
            return
    elif clicked.get() =="Manual Raw":
        try:
            int(start2.get())
            int(end2.get())
            int(start3.get())
            int(end3.get())
        except:
            mb.showerror("Invalid Video Cap", "The provided video cap is incorrect. Please try again.")
            return


    try:
        fps = i1.get()
        int(fps)
    except:
        mb.showerror("Invalid Rate of Analysis", "The provided rate of analysis incorrect. Please try again.")
        return
    try:
        exp_d = i2.get()
        float(exp_d)
    except:
        mb.showerror("Invalid Exploration Distance", "The provided exploration distance is incorrect. Please try again.")
        return






    global final_explore
    global pixle_to_cm_ratio
    final_explore = np.zeros((len(files), 6))
    pixle_to_cm_ratio = Annotate.pixle_to_cm_ratio

    Img_ann = Annotate.final_data


    # outputes general
    is_annot = annot.get()
    is_speed = speed.get()
    is_distance = Tdistance.get()
    is_thig = Thigmo.get()

    # outputs time series
    is_mouseLoc = mouseLoc.get()
    is_expsig = explSignal.get()
    isthgsig = ThigmoSignal.get()
    is_n_f_distance = N_f_distance.get()


    #Check is thigmotaxis area is identified
    if (is_thig ==1 or isthgsig==1) and Img_ann.shape[0]<3:
        answer = mb.askyesno("No Thigmotaxis Area Found.","No area for thigmotaxis is identified. The analysis will ignore the thigmotaxis analysis. Would you like to proceed?")
        if answer:
            is_thig=0
            isthgsig=0
        else:
            analyze_button["state"] = ACTIVE
            return

    analyze_button["state"] = DISABLED


    # TODO:  output if annotation data is needed MUST BE CHANGES LATER TO CORRECT FORMAT

    if is_annot == 1:
        out_name = ouput_entry.get() + "/" + "Image_annotations.csv"
        Img_ann.to_csv(out_name, index=False)

    # Changing the Img annotation from pd to np
    Image_annotate = np.empty((Img_ann.shape[0], 5))
    for index, i in Img_ann.iterrows():
        Image_annotate[index, 0] = 0 if i["type"] == "blue" else (
            1 if i["type"] == "green" else 2)  # 0: Novel, 1:Familiar, 2:thigmo
        Image_annotate[index, 1:] = i["xmin"], i["xmax"], i["ymin"], i["ymax"]
    Image_annotate = Image_annotate[np.argsort(Image_annotate[:, 0])]

    # Video cap for video annotation
    video_cap = np.empty((7))
    video_cap[0] = 0 if clicked.get() == "Automatic (beta)" else (1 if clicked.get() == "Manual Percentage" else 2)
    video_cap[1:] = number(start.get()), number(end.get()), number(start2.get()), number(end2.get()), number(
        start3.get()), number(end3.get())

    global file_index
    file_index = []

    initiate_analysis(len(file_index))


def select(tab):
    tabControl.select(tab)


def create_box(value):
    def forget():
        start_raw.place_forget()
        end_raw.place_forget()
        end_raw2.place_forget()
        start_raw2.place_forget()
        start_p.place_forget()
        end_p.place_forget()
        start.place_forget()
        end.place_forget()
        start2.place_forget()
        end2.place_forget()
        start3.place_forget()
        end3.place_forget()

    if value == "Automatic (beta)":
        forget()
        return
    elif value == "Manual Percentage":
        forget()
        #Text
        start_p.place(relx=0.5, rely=0.54)
        end_p.place(relx=0.5, rely=0.6)
        #Entry
        start.place(relx=0.7, rely=0.54)
        end.place(relx=0.7, rely=0.6)

    else:
        forget()
        #text min
        start_raw.place(relx=0.5, rely=0.54)
        end_raw.place(relx=0.5, rely=0.6)
        #text sec
        start_raw2.place(relx=0.7, rely=0.54)
        end_raw2.place(relx=0.7, rely=0.6)

        #Entry Min
        start2.place(relx=0.6, rely=0.54)
        end2.place(relx=0.6, rely=0.6)
        #Entry Sec
        start3.place(relx=0.8, rely=0.54)
        end3.place(relx=0.8, rely=0.6)

# Load saved model and build the detection function
def get_model(PATH_TO_SAVED_MODEL):
    global detect_fn
    detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
    print("done")



#Loading the Object Detection Model
if __name__ == "__main__":
    global detect_fn
    multiprocessing.freeze_support()

    # PROVIDE PATH TO MODEL DIRECTORY
    PATH_TO_MODEL_DIR ="my_mobilenet_model"

    # PROVIDE PATH TO LABEL MAP
    PATH_TO_LABELS ="label_map.pbtxt"

    # PROVIDE THE MINIMUM CONFIDENCE THRESHOLD

    MIN_CONF_THRESH = 0.5
    PATH_TO_SAVED_MODEL =   "saved_model"

    #
    # thread = Thread(target=get_model)
    # thread.start()
    multiprocessing.Process(target=get_model, args=[PATH_TO_SAVED_MODEL]).start()

    #GUI
    root=Tk()
    root.title("Mouse Vision")
    width= 650
    height=600
    button_height = 5
    button_width = 20
    root.geometry("650x800")

    root.resizable(False,False)
    tabControl = ttk.Notebook(root)

    video_tab = Frame(tabControl,width=width, height=height, bg = "#72B2E9")
    setting_tab= Frame(tabControl,width=width, height=height)
    output_tab= Frame(tabControl,width=width, height=height)

    tabControl.add(video_tab, text='Videos')
    tabControl.add(setting_tab, text='Setting')
    tabControl.add(output_tab, text='Output')


    tabControl.pack(pady=15,padx=15)


    #-----------------------------Video Tab--------------------------------
    open_videos = Button(video_tab, text="Choose Files", height = button_height, width= button_width, command=choose_file)
    annotate_button = Button(video_tab, text="Annotate", height = button_height, width= button_width, command=lambda: annotate(files,ouput_entry.get(),analyze_button) )
    # annotate_button["state"] = "disabled"

    ouput_entry = Entry(video_tab, width = 50)
    ouput_entry.insert(0, "Please type the output location or click the button bellow")
    output_button = Button(video_tab, text="Output Location", height = button_height, width= button_width, command=output_loc )

    video_list = Listbox(video_tab, bg = "gray", height = 20, width = 25)
    next_button = Button(video_tab, text = "Next", height = button_height, width= button_width, command = lambda: select(1))

    open_videos.grid(row= 0,column= 0, padx=50, pady=50)
    annotate_button.grid(row= 3,column= 0, padx=50, pady=50)
    output_button.grid(row= 2,column= 0, padx=50, pady=50)
    ouput_entry.grid(row= 1,column= 0, padx=20, pady=25)

    video_list.grid(row= 0,column= 1, padx=50, pady=50, rowspan=5)
    next_button.grid(row= 6,column= 1, padx=50, pady=25)


    #---------------------------Setting Tab-----------------------------------
    f1 = Label(setting_tab,text = "Analysis rate (frames/second):   ").place(relx = 0.02, rely = 0.04)
    f2 = Label(setting_tab,text = "Exploration:   ").place(relx = 0.02, rely = 0.14)
    f3 = Label(setting_tab,text = "Exploration Distance from object (cm): ").place(relx = 0.02, rely = 0.24)
    f4 = Label(setting_tab,text = "Size of chamber (cm):   ").place(relx = 0.02, rely = 0.34)
    f5 = Label(setting_tab,text = "Video Cap:   ").place(relx = 0.02, rely = 0.54)

    #Validate data
    # val = setting_tab.register(validate)

    #Frames/second
    i1= Entry(setting_tab, width= 10)
    i1.insert(0,"3")
    # i1.config(validate ="key", validatecommand =(val, '%P'))
    i1.place(relx = 0.4, rely = 0.04)

    #Exploration Definition
    expl_def=IntVar()
    expl_def.set(1)
    Radiobutton(setting_tab, text="Only Distance", variable = expl_def, value=0).place(relx = 0.2, rely = 0.14)
    Radiobutton(setting_tab, text="Distance and Direction", variable = expl_def, value=1).place(relx = 0.4, rely = 0.14)

    #Exploration Distance
    i2= Entry(setting_tab, width= 10)
    i2.insert(0,"2")
    # i2.config(validate ="key", validatecommand =(val, '%P'))
    i2.place(relx = 0.4, rely = 0.24)

    #Chamber size
    use_gpu = IntVar()
    use_gpu.set(0)
    Checkbutton(setting_tab, text="Use GPU for analysis (only for CUDA supported GPUs)", variable=use_gpu).place(relx=0.02,
                                                                                                         rely=0.34)

    #Include object standing
    obj_stand = IntVar()
    obj_stand.set(0)
    Checkbutton(setting_tab, text= "Include standing on object as exploration", variable =obj_stand ).place(relx = 0.02, rely = 0.44)


    #Video Starting point
    clicked = StringVar()
    clicked.set("Automatic (beta)")
    video_start= OptionMenu(setting_tab, clicked, "Automatic (beta)","Manual Percentage", "Manual Raw", command=create_box).place(relx = 0.2, rely = 0.54)

    start_raw = Label(setting_tab, text="Start (min): ")
    end_raw = Label(setting_tab, text="End (min): ")

    start_raw2 = Label(setting_tab, text="Start (sec): ")
    end_raw2 = Label(setting_tab, text="End (sec): ")

    start_p = Label(setting_tab, text="Ignore the first (%): ")
    end_p = Label(setting_tab, text="Ignore the last (%): ")

    start = Entry(setting_tab, width=10)
    # start.config(validate="key", validatecommand=(val, '%P'))
    end = Entry(setting_tab, width=10)
    # end.config(validate="key", validatecommand=(val, '%P'))

    start2 = Entry(setting_tab, width=10)
    # start2.config(validate="key", validatecommand=(val, '%P'))
    end2 = Entry(setting_tab, width=10)
    # end2.config(validate="key", validatecommand=(val, '%P'))

    start3 = Entry(setting_tab, width=10)
    # start3.config(validate="key", validatecommand=(val, '%P'))
    end3 = Entry(setting_tab, width=10)
    # end3.config(validate="key", validatecommand=(val, '%P'))

    #Next, back Button
    Button(setting_tab, text = "Next", height = 2, width= button_width, command = lambda: select(2)).place(anchor= "ne", relx = 0.98, rely = 0.9)
    Button(setting_tab, text = "Back", height = 2, width= button_width, command = lambda: select(0)).place(relx = 0.02, rely = 0.9)


    #---------------------------Output Tab-----------------------------------
    #Basic data
    Label(output_tab,text = "Basic data:").place(relx = 0.02, rely = 0.04)
    a = IntVar()
    a.set(1)
    Checkbutton(output_tab, text= "Novel/Familiar object exploration time", variable = a ,state= DISABLED).place(relx = 0.02, rely = 0.1)

    annot= IntVar()
    annot.set(0)
    Checkbutton(output_tab, text= "Annotation data (Recommended if exporting time-series data)", variable =  annot).place(relx = 0.02, rely = 0.15)

    speed= IntVar()
    speed.set(0)
    Checkbutton(output_tab, text= "Average speed", variable =  speed).place(relx = 0.02, rely = 0.2)

    Tdistance=IntVar()
    Tdistance.set(0)
    Checkbutton(output_tab, text= "Total distance", variable = Tdistance ).place(relx = 0.02, rely = 0.25)

    Thigmo=IntVar()
    Thigmo.set(0)
    thig = Checkbutton(output_tab, text= "Thigmotaxis", variable = Thigmo )
    # thig["state"]=DISABLED
    thig.place(relx = 0.02, rely = 0.3)

    #Time series data
    Label(output_tab,text = "Time-series data:").place(relx = 0.02, rely = 0.4)

    mouseLoc= IntVar()
    mouseLoc.set(0)
    Checkbutton(output_tab, text= "The data for mouse location at every frame", variable =  mouseLoc).place(relx = 0.02, rely = 0.5)

    explSignal=IntVar()
    explSignal.set(0)
    Checkbutton(output_tab, text= "Exploration signal (binary)", variable = explSignal ).place(relx = 0.02, rely = 0.55)

    ThigmoSignal=IntVar()
    ThigmoSignal.set(0)
    thigsig = Checkbutton(output_tab, text= "Thigmotaxis signal (binary)", variable = ThigmoSignal )
    # thigsig["state"]=DISABLED
    thigsig.place(relx = 0.02, rely = 0.6)

    N_f_distance=IntVar()
    N_f_distance.set(0)
    Checkbutton(output_tab, text= "Distance to Novel and Familiar Object", variable = N_f_distance ).place(relx = 0.02, rely = 0.65)


    #Back, analyse Button
    global analyze_button
    Button(output_tab, text = "Back", height = 2, width= button_width, command = lambda: select(1)).place(relx = 0.02, rely = 0.9)
    analyze_button = Button(output_tab, text = "Analyze", height = 2, width= button_width, state= DISABLED, command = analyze)
    analyze_button.place(anchor= "ne", relx = 0.98, rely = 0.9)




    root.mainloop()





