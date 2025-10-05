import math, json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path

path_to_json = Path(__file__).resolve().with_name("Biscuit Basher.json") #finds path for json file

path_to_cookie = Path(__file__).resolve().with_name("cookie.png") #finds path for cookie.png file

#import json file into dictionary's
with open(path_to_json, 'r') as file:
    Buttons = json.load(file)

    buildingButtons = Buttons['buildingButtons']
    upgradeButtons = Buttons['upgradeButtons']

#creating dictionary for story information on num of buildings amongst other things
Dict = {
    'building' : {},
    'upgrade' : {}
}

#preparing Dict for storing information
for building in buildingButtons:
    Dict['building'][building] = {'num' : 0}

for upgrade in upgradeButtons:
    Dict['upgrade'][upgrade] = {'level' : 0}

def resize_cookie_image(event): #function to allow the main "cookie" button to be scaleable
    new_width = min(root.winfo_height() / 1.25, root.winfo_width() / 1.25 - 230)
    new_height = new_width

    if new_width < 0 or new_height < 0:
        return

    resized_pil = original_pil_image.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)

    resized_tk = ImageTk.PhotoImage(resized_pil)

    cookie.config(image=resized_tk)
    cookie.image = resized_tk

def format_number_abbr(number): #basic formatting function e.g. 1,000 = 1K
    magnitude = 0
    formatted_number = number
    while abs(formatted_number) >= 1000:
        magnitude += 1
        formatted_number /= 1000
    try:
        return '{:0.2f}{}'.format(formatted_number, ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S'][magnitude])
    except:
        return '{:0.2e}'.format(number)

formattedCost = lambda a, b : format_number_abbr(int(math.ceil(a * 1.15 ** b))) #lambda function to format the cost of a building/upgrade easily

cost = lambda a, b : a*1.15**b #lambda function to calculate the cost of a building/upgrade

def button_click(building, type): #function for performing button actions
    global buildingButtons
    global biscuits
    global Bps
    global buildingButtons
    global Dict

    building = str(building)

    #if pressed button isn't cookie tries to get the next level of the building/upgrade
    if building != 'cookie': 
        try:
            level = str(Dict['upgrade'][building]['level'] + 1)
        except:
            print('No upgrade')

    #if button is cookie performs relevant actions
    if building == 'cookie': 
        level = str(Dict['upgrade']['Basher']['level']) #gets level for the current Basher upgrade level
        biscuits += 1 * upgradeButtons['Basher']['level'][level]['Bonus'] + totalBuildings * 0.1 * upgradeButtons['Basher']['level'][level]['bpsBonus'] #calculates and adds the correct amount of biscuits
        money.config(text=f"Biscuits\n{format_number_abbr(round(biscuits, 1))}\nBPS: {format_number_abbr(round(Bps, 1))}") #updates "money" text field to correct amount

    #if button is a building and player has correct amount of biscuits to buy performs relevant actions
    elif type == 'building' and biscuits >= cost(buildingButtons[building]['baseCost'], Dict['building'][building]['num']):
        biscuits -= cost(buildingButtons[building]['baseCost'], Dict['building'][building]['num']) #calculates cost of building then subtracts it from current biscuit count
        Dict['building'][building]['num'] += 1 #increments building count
        Dict['building'][building]['button'].config(text=f"{buildingButtons[building]['plural']} ({Dict['building'][building]['num']})\ncost: {formattedCost(buildingButtons[building]['baseCost'], Dict['building'][building]['num'])}") #updates building button text to show cost of next one and current amount of the building
        money.config(text=f"Biscuits\n{format_number_abbr(round(biscuits, 1))}\nBPS: {format_number_abbr(round(Bps, 1))}")
    
    #if button is a upgrade and player has correct amount of biscuits to buy performs relevant actions
    elif type == 'upgrade' and biscuits >= upgradeButtons[building]['level'][level]['Cost']:
        biscuits -= upgradeButtons[building]['level'][level]['Cost'] #calculates cost of upgrade then subtracts it from current biscuit count
        Dict['upgrade'][building]['level'] += 1 #increments upgrade level by 1

        #checks if current level is less than the maximum
        if int(level) < upgradeButtons[building]['maxLevel']:
            level = str(Dict['upgrade'][building]['level'] + 1) #sets level variable to the next available upgrade level
            Dict['upgrade'][building]['button'].config(text=f"{upgradeButtons[building]['level'][level]['name']}\nCost: {format_number_abbr(upgradeButtons[building]['level'][level]['Cost'])}", state=tk.DISABLED) #updates button text to next upgrade level name and cost
        else:
            Dict['upgrade'][building]['button'].config(text=f"{upgradeButtons[building]['level'][level]['name']}", state=tk.DISABLED) #else disables upgrade button and removes cost text

def auto(): #function for calculating how many biscuits are earned by existing buildings
    global buildingButtons
    global biscuits
    global Bps
    global totalBuildings

    #sets variables to zero
    biscuitsEarned = 0
    Buildings = 0

    for i in buildingButtons: #recursively goes through list of buildings
        #tries to calculate how many biscuits are earned
        try:
            biscuitsEarned += Dict['building'][i]['num'] * buildingButtons[i]['gives'] * upgradeButtons[i]['level'][level]['Bonus']
        except: #if it fails when trying to account for upgrade bonus fallsback to calculate off of building num and how much it gives
            biscuitsEarned += Dict['building'][i]['num'] * buildingButtons[i]['gives']
        
        #checks if the building is not a basher
        if building != 'Basher':
            level = str(Dict['upgrade']['Basher']['level']) #sets level variable

            Buildings += Dict['building'][building]['num'] #increments building count by how many of current building are owned
            biscuitsEarned += Dict['building'][building]['num'] * 0.1 * upgradeButtons['Basher']['level'][level]['bpsBonus'] #calculates Bps Bonus if it applies currently

    biscuits += biscuitsEarned / 1000 #adds earned biscuits to current biscuit count

    Bps = biscuitsEarned #sets Bps variable

    totalBuildings = Buildings #sets the totalBuilding variable

    money.config(text=f"Biscuits\n{format_number_abbr(round(biscuits, 1))}\nBPS: {format_number_abbr(round(Bps, 1))}") #updates current text Biscuit and Bps counts

    #unlocks upgrade button if correct amount of buildings are owned
    for i in Dict['upgrade']:
        level = str(Dict['upgrade'][i]['level'] + 1)

        if Dict['upgrade'][i]['level'] < upgradeButtons[i]['maxLevel'] and Dict['building'][i]['num'] >= upgradeButtons[i]['level'][level]['unlock']:
            Dict['upgrade'][i]['button'].config(state=tk.NORMAL)

    root.after(1, auto) #automatically re-runs function every 1 microsecond

if __name__ == '__main__':
    #defining variables
    root = tk.Tk()

    biscuits = 0

    totalBuildings = 0

    Bps = 0

    #importing cookie.png
    original_pil_image = Image.open(path_to_cookie)
    original_width, original_height = original_pil_image.size

    cookieimage = ImageTk.PhotoImage(original_pil_image)

    #configuring tkinter window defaults
    root.resizable(1, 1)
    root.minsize(900, 600)
    root.geometry('900x600')

    s = ttk.Style()
    s.configure('TFrame', background='chocolate3', highlightcolor='chocolate3', highlightthickness=3, borderwidth=3)

    root.title("Biscuit Basher")
    root.config(bg='chocolate3')

    frame = tk.Frame(root, highlightbackground='chocolate3', highlightcolor='chocolate3')
    frame.grid(row=0, column=1, rowspan=10, sticky='nse')
    frame.configure(background='chocolate3')

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)


    #creating Biscuit and Bps Counter
    money = tk.Label(root, text=f"Biscuits\n{format_number_abbr(round(biscuits, 1))}\nBPS: {format_number_abbr(round(Bps, 1))}", wraplength=300, justify="center")
    money.config(font=("Arial", 25), bg='chocolate3')
    money.grid(row=0, column=0, sticky="ns")

    #creating biscuit button
    cookie = tk.Button(root, image=cookieimage, command=lambda:button_click('cookie', 'cookie'), borderwidth=0, relief='groove')
    cookie.config(bg='chocolate3', activebackground='chocolate3')
    cookie.grid(row=1, column=0, rowspan=4, sticky="ns")

    #setting up canvas for buttons to allow scrolling
    canvas = tk.Canvas(frame, bg='chocolate3', highlightbackground='chocolate3')
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set, bg='chocolate3')

    autoframe = ttk.Frame(canvas)

    autoframe.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    r = 0

    #creating buildig buttons
    for i in buildingButtons:
        Dict['building'][i]['button'] = tk.Button(autoframe, text=f"{i} ({Dict['building'][i]['num']})\ncost: {formattedCost(buildingButtons[i]['baseCost'], Dict['building'][i]['num'])}", width=17, height=3, command=lambda j=i: button_click(j, 'building'))
        Dict['building'][i]['button'].config(font=("Arial", 11), bg='saddle brown', activebackground='saddle brown')
        Dict['building'][i]['button'].grid(row=r, sticky='nsew')
        r += 1

    r = 0

    #creating upgrade buttons
    for i in upgradeButtons:
        Dict['upgrade'][i]['button'] = tk.Button(autoframe, text=f"{upgradeButtons[i]['level']['1']['name']}\nCost: {format_number_abbr(upgradeButtons[i]['level']['1']['Cost'])}", width=17, height=3, command=lambda j=i: button_click(j, 'upgrade'))
        Dict['upgrade'][i]['button'].config(font=("Arial", 11), bg='saddle brown', activebackground='saddle brown', state=tk.DISABLED)
        Dict['upgrade'][i]['button'].grid(row=r, column=1, sticky='nsew', padx=(0,5))
        r += 1

    window_id = canvas.create_window((0, 0), window=autoframe, anchor="nw")

    #allowing buttons to scale correctly
    def resize_autoframe(event):
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", resize_autoframe)

    autoframe.columnconfigure(0, weight=1)
    autoframe.columnconfigure(1, weight=1)

    #creating scrollbar
    canvas.grid(row=0, column=0, sticky="nse")
    scrollbar.grid(row=0, column=1, sticky="ns")

    #defining how much to scroll when mouse wheel is scrolled
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    #calls _on_mousewheel function
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    #ensures cookie scale function is used
    root.bind("<Configure>", resize_cookie_image)

    #starts auto function
    auto()

    #creates tkinter window
    root.mainloop()