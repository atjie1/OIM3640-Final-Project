# Source for how to download Kivy: https://www.youtube.com/watch?v=kV2eCVmc_Ig
# Source for Kivy issues and necessary to create a virtual environ with Python 3.10.10: https://github.com/kivy/kivy/issues/8042
# Source of starter code: https://www.youtube.com/watch?v=YDp73WjNISc

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from tv_shows_webscraping import preference_filter, random_pick


class TomatoSoup(App):
    def build(self):
        self.window = GridLayout()
        # add widgets to window
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # image widget
        self.window.add_widget(Image(source="logo.png", size_hint=(5, 5)))

        # label widget
        self.greeting = Label(
            text="Enter your Tomatometer and Audience Score Tolerance below\nto generate a popular NETFLIX show to watch!",
            font_size=14,
            color="#FF7A00",
        )
        self.window.add_widget(self.greeting)

        # slider input widget for tomatometer tolerance
        self.user_1 = Slider(
            min=0,
            max=100,
            value=0,
            value_track=True,
            value_track_color=[1, 0, 0, 1],
        )
        self.user_1.bind(value=self.update_label_1)
        self.window.add_widget(self.user_1)

        # slider label
        self.label_1 = Label(
            text="Tomatometer: " + str(int(self.user_1.value)), font_size=14
        )
        self.window.add_widget(self.label_1)

        # slider input widget for audience_score tolerance

        self.user_2 = Slider(
            min=0, max=100, value=0, value_track=True, value_track_color=[1, 0, 0, 1]
        )
        self.user_2.bind(value=self.update_label_2)
        self.window.add_widget(self.user_2)

        # slider label
        self.label_2 = Label(
            text="Audience Score: " + str(int(self.user_2.value)), font_size=14
        )
        self.window.add_widget(self.label_2)

        # button widget
        self.button = Button(
            text="SHOW ME!",
            size_hint=(1, 0.5),
            bold=True,
            background_color="#FF7A00",
            background_normal="",
        )

        self.button.bind(on_press=self.show_info)
        self.window.add_widget(self.button)

        return self.window

    def update_label_1(self, instance, value):
        self.label_1.text = "Tomatometer: " + str(int(value))

    def update_label_2(self, instance, value):
        self.label_2.text = "Audience Score: " + str(int(value))

    def show_info(self, instance):
        shows = preference_filter(
            "tv_shows.db",
            min_tomatometer=self.user_1.value,
            min_audience_score=self.user_2.value,
        )
        picked_show_text = random_pick(shows)
        picked_show_dict = {}
        if picked_show_text is not None:
            picked_show_dict = dict(
                zip(
                    [
                        "Title",
                        "Synopsis",
                        "Genre",
                        "Tomatometer",
                        "Critic Sentiment",
                        "Critic Consensus",
                        "Audience Score",
                        "Audience Sentiment",
                        "Latest Episode Date",
                        "Executive Producers",
                        "Cast Members",
                    ],
                    picked_show_text.split("\n"),
                )
            )

            # Create popup
            popup_layout = GridLayout(
                cols=1, padding=[10, 10, 10, 10], spacing=[10, 10]
            )

            # Create a label widget for the synopsis
            synopsis_label = Label(
                text=picked_show_dict["Synopsis"][:300] + "...",
                text_size=(popup_layout.width * 8, None),
                height=80,
                valign="top",
            )
            popup_layout.add_widget(synopsis_label)
            popup_layout.add_widget(Label(text=picked_show_dict["Genre"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Tomatometer"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Critic Sentiment"]))
            # popup_layout.add_widget(Label(text=picked_show_dict['Critic Consensus']))
            popup_layout.add_widget(Label(text=picked_show_dict["Audience Score"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Audience Sentiment"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Latest Episode Date"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Executive Producers"]))
            popup_layout.add_widget(Label(text=picked_show_dict["Cast Members"]))

            popup = Popup(
                title=picked_show_dict["Title"],
                # synopsis=picked_show_dict['Synopsis'],
                content=popup_layout,
                size_hint=(0.7, 0.7),
            )
            popup.open()

if __name__ == "__main__":
    TomatoSoup().run()
