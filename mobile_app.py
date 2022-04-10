import os

from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.uix.list import MDList
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.picker import MDDatePicker
from kivy.properties import ObjectProperty
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog

from app_server import AppServer, InvalidLoginError


import datetime
import json


def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))



KV = '''
<ContentNavigationDrawer>:

    orientation: "vertical"
    spacing: '8dp'
    padding: '8dp'


    MDLabel:
        text: "    xakatoH project"
        font_size: 30
        size_hint_y: None
        height: self.texture_size[1]


    ScrollView:

        MDList:


            OneLineListItem:
                text: "Profile"

                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.transition.direction = 'left'
                    root.screen_manager.current = 'profile'
                    app.root.ids.toolbar.title = 'Profile'


            OneLineListItem:
                text: "Log out"

                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.transition.direction = 'left'
                    root.screen_manager.current = 'log in'
                    app.root.ids.toolbar.title = 'Log In'



Screen:



    MDNavigationLayout:
        id: nav
        x: toolbar.height

        ScreenManager:
            id: screen_manager
            
            
            LogInScreen:
                name: "log in"

                MDToolbar:
                    id: toolbar
                    pos_hint: {"top": 1}
                    elevation: 10
                    title: "Log In"
                    left_action_items: []


                MDLabel:
                    id: auth_label
                    text: 'Authorization'
                    font_size: 40
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding_y: 15
                    pos_hint: {'center_x': .5, 'center_y': .7}

                MDTextField:
                    id: user
                    hint_taxt: 'username'
                    icon_right: 'account'
                    size_hint_x: None
                    width: 300
                    font_size: 28
                    pos_hint: {'center_x': .5, 'center_y': .57}

                MDTextField:
                    id: password
                    hint_taxt: 'password'
                    icon_right: 'eye-off'
                    size_hint_x: None
                    width: 300
                    font_size: 28
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    password: True

                MDRectangleFlatButton:
                    text: 'LOG IN'
                    font_size: 25
                    width: 300
                    pos_hint: {'center_x': .5, 'center_y': .3}
                    on_press: app.auth()


            MainScreen:
                name: "main"
                view: view
                BoxLayout:
                    orientation: 'vertical'

                    MDToolbar:
                        id: toolbar
                        pos_hint: {"top": 1}
                        elevation: 10
                        title: "Booking room"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [['calendar', lambda x: app.show_date_picker()]]
                    
                    BoxLayout:
                        orientation: 'vertical'
                    
                        ScrollView:
                            id: view
                            

                            MDList:
                                id: room_list
                                
                                
                                
                               
                            
            TimeScreen:
                name: 'time'
                
                BoxLayout:
                    orientation: 'vertical'

                    MDToolbar:
                        id: toolbar
                        pos_hint: {"top": 1}
                        elevation: 10
                        title: "Choose time"
                        left_action_items: [["keyboard-backspace", lambda x: app.to_main()]]
                        
                    BoxLayout:
                        orientation: 'vertical'
                    
                        ScrollView:
                            id: view_time
                            

                            MDList:
                                id: time_list




                
            ProfileScreen:
                name: "profile"

                MDToolbar:
                    id: toolbar
                    pos_hint: {"top": 1}
                    elevation: 10
                    title: "Profile"
                    left_action_items: [["keyboard-backspace", lambda x: app.to_main()]]


                MDLabel:
                    text: "Profile"
                    halign: "center"
                    
            

            


        MDNavigationDrawer:
            id: nav_drawer

            ContentNavigationDrawer:
                screen_manager: screen_manager
                nav_drawer: nav_drawer
'''
rooms_json = """[
{
    "room_name": "room 1",
    "data":
    [
 {
     "time_id": "11:00",
     "user": "Марина"
 },
 {
     "time_id": "12:30",
     "user": "Марина"
 },
 {
     "time_id": "17:00",
     "user": "Anon"
 },
 {
     "time_id": "13:00",
     "user": "Женя"
 },
 {
     "time_id": "13:30",
     "user": null
 },
 {
     "time_id": "14:00",
     "user": null
 }
    ]
}
]
"""


aps = AppServer('127.0.0.1', 3310)

# main screen with rooms
class MainScreen(Screen):
    pass

# screet to choose time
class TimeScreen(Screen):
    pass

# i don't know
class LogInScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()



class Booker(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_info = {}
    def build(self):
        return Builder.load_string(KV)
    
    def on_start(self):
        # временно, убрать потом
        self.user_name = "Марина"
        for i in range(20):
            self.root.ids.room_list.add_widget(
                OneLineListItem(text=f"room {i}", on_press=self.to_time)
            )
        
                    
        
    # click OK
    def on_save(self, instance, value, date_range):
        # here we capture date
        self.current_date = value
    # click X
    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(title='SELECT DATE',
                                  min_date=datetime.datetime.now().date(),
                                  max_date=datetime.datetime.now().date() + datetime.timedelta(days=7))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        
    def to_booking(self, elem):
        # elem is time to check
        #if it is free, we'll book, else no
        start, end = elem.text.split(' - ')
        self.time_n = start
        
        ind = -1
        for j, dop in enumerate(self.room_info):
            if dop['room_name'] == self.room_n: 
                ind = j
                room = dop
        text = "The room is free"
        if ind == -1:
            # room was nor booked at all
            text = "The room is free"
        else:
            for k in range(len(room['data'])):
                if room['data'][k]['time_id'] == start and room['data'][k]['user'] is not None:
                    text = f"The room is booked by {room['data'][k]['user']}"
                    break
        

        
        close_button = MDFlatButton(text="close", on_release=self.close_dialog)
        book_button = MDFlatButton(text="book", on_release=self.book_room)
        
                
        self.dialog = MDDialog(
                text=text, buttons=[close_button, book_button]
        )
        self.dialog.open()

    
    def close_dialog(self, obj):
        self.dialog.dismiss()
        
    def book_room(self, elem):
        # here we can make booking
        pass
       
    def to_time(self, elem):
        # elem is OneLineList object
        self.room_n = elem.text
        self.room_info = json.loads(rooms_json)
        self.root.ids.screen_manager.transition.direction = 'left'
        self.root.ids.screen_manager.current = 'time'
        
        for i in range(15):
            if i % 2 == 0:
                start = str(i + 9) + ':00'
                end = str(i + 9) + ':30'
            else:
                start = str(i - 1 + 9) + ':30'
                end = str(i - 1 + 10) + ':00'
                
            ind = -1
            for j, dop in enumerate(self.room_info):
                if dop['room_name'] == elem.text: 
                    ind = j
                    room = dop
            if ind == -1:
                # add time in red color
                self.root.ids.time_list.add_widget(
                    TwoLineListItem(text=start + ' - ' + end, secondary_text="free", on_press=self.to_booking) # red
                )
            else:
                #print(room)
                # this room was booked today, check time and user. if time and user are equal, we add time in green
                # if name is not equal, we add time in red
                fl = True
                nm = 'free'
                for k in range(len(room['data'])):
                    if room['data'][k]['time_id'] == start and room['data'][k]['user'] == self.user_name:
                        self.root.ids.time_list.add_widget(
                        TwoLineListItem(text=start + ' - ' + end, secondary_text="booked by you", on_press=self.to_booking, bg_color=(0, 1, 0, .1)) # green
                        )
                        fl = False
                        #print(start, end)
                        break
                    elif room['data'][k]['time_id'] == start and room['data'][k]['user'] != self.user_name and room['data'][k]['user'] is not None:
                        nm = 'booked by ' + room['data'][k]['user']
                if fl and nm != 'free':
                    self.root.ids.time_list.add_widget(
                        TwoLineListItem(text=start + ' - ' + end, secondary_text=nm, on_press=self.to_booking, bg_color=(1, 0, 0, .1)) # red
                    ) 
                elif fl and nm == 'free':
                    self.root.ids.time_list.add_widget(
                        TwoLineListItem(text=start + ' - ' + end, secondary_text=nm, on_press=self.to_booking) # no colour
                    ) 
            
                
    def to_main(self):
        self.root.ids.screen_manager.transition.direction = 'right'
        self.root.ids.screen_manager.current = 'main'


    def auth(self):

        try:
            login = self.root.ids.user.text
            password = self.root.ids.password.text

            aps.auth(login, password)
            self.user_name = login
            Clock.schedule_interval(self.try_notify, 10)
            self.to_main()


        except InvalidLoginError as ile:
            self.root.ids.user.text = ""
            self.root.ids.password.text = ""

    def try_notify(self, *args):
        notification = aps.get_notification()

        if notification is not None:
            notify("Booker", notification)
            # self.user_name = login
            return

Booker().run()
