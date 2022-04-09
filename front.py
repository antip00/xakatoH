#!/usr/bin/env python3
from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
import json

rooms_json = """{
    "rooms":
    [
        {
            "name": "переговорка 1",
            "intervals":
            [
                {
                    "id": 1,
                    "start": "12:00",
                    "end": "12:30",
                    "owner": "Марина"
                },
                {
                    "id": 2,
                    "start": "12:30",
                    "end": "13:00",
                    "owner": "Марина"
                },
                {
                    "id": 3,
                    "start": "13:00",
                    "end": "13:30",
                    "owner": "Марина"
                },
                {
                    "id": 4,
                    "start": "13:30",
                    "end": "14:00",
                    "owner": null
                },
                {
                    "id": 5,
                    "start": "14:00",
                    "end": "14:30",
                    "owner": null
                }
            ]
        }
    ]
}
"""

rooms_dict = json.loads(rooms_json)

class room_1(MDApp):
    def build(self):
        screen = Screen()
        for i in range(len(rooms_dict["rooms"][0]["intervals"])):
            if rooms_dict["rooms"][0]["intervals"][i]["owner"] is None:
                screen.add_widget(
                    OneLineListItem(
                        text=rooms_dict["rooms"][0]["intervals"][i]["start"]+"-"+rooms_dict["rooms"][0]["intervals"][i]["end"],
                        pos_hint={"center_x": 0.5, "center_y": 0.9 - 0.1*i},
                        on_release=self.show_data_i(i), bg_color=(0, 1, 0, 1), text_color=(0, 0, 0, 1),  theme_text_color="Custom"
                    )
                )
            else:
                screen.add_widget(
                    OneLineListItem(
                        text=rooms_dict["rooms"][0]["intervals"][i]["start"] + "-" +
                             rooms_dict["rooms"][0]["intervals"][i]["end"],
                        pos_hint={"center_x": 0.5, "center_y": 0.9 - 0.1*i},
                        on_release=self.show_data_i(i), bg_color=(1, 0,  0, 1), text_color=(0, 0, 0, 1),  theme_text_color="Custom"
                    )
                )
        return screen

    def show_data_i(self, i):
        def show_data(obj):
            close_button = MDFlatButton(text="close", on_release=self.close_dialog)
            book_button = MDFlatButton(text="book")
            if obj.text_color == [0, 1, 0, 1]:
                text = "СВОБОДНО, ПИДР"
            else:
                owner_name = rooms_dict["rooms"][0]["intervals"][i]["owner"]
                text = f"ЗАНЯТО существом по имени {owner_name}, СВАЛИ НАХУЙ"
            self.dialog = MDDialog(title=obj.text, text=text,
                              buttons=[close_button, book_button])
            self.dialog.open()
        return show_data

    def close_dialog(self, obj):
        self.dialog.dismiss()


room_1().run()
