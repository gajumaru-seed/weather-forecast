import requests
from datetime import datetime
from win11toast import toast
import re
import customtkinter as ctk
import time

class weather_forecast:
    @property
    def datetime_data(self):
        return self.__datetime_data

    @datetime_data.setter
    def datetime_data(self, value:str):
        self.__datetime_data = value

    @property
    def interval_3hour(self):
        return self.__interval_3hour

    @interval_3hour.setter
    def interval_3hour(self, value:str):
        self.__interval_3hour = value
        
    @property
    def area(self):
        return self.__area

    @area.setter
    def area(self, value:str):
        self.__area = value

    @property
    def detail_area(self):
        return self.__detail_area

    @detail_area.setter
    def detail_area(self, value:str):
        self.__detail_area = value
        
    @property
    def observatory(self):
        return self.__observatory

    @observatory.setter
    def observatory(self, value:str):
        self.__observatory = value
        
    @property
    def detail_array(self):
        return self.__detail_array

    @detail_array.setter
    def detail_array(self, value:str):
        self.__detail_array = value
    
    def __init__(self):
        self.area = None
        self.detail_area = None
        self.observatory = None
        self.datetime_data = None
        self.interval_3hour = None
    
    def set_area(self, area_name:str):
        if area_name == "愛知県":
            self.area = "230000" # 愛知県
            self.detail_area = "230010" # 愛知県西部
            self.observatory = "51106" # 名古屋
        elif area_name == "大阪府":
            self.area = "270000" # 大阪府
            self.detail_area = "270000" # 大阪府
            self.observatory = "62078" # 大阪
        elif area_name == "東京都":
            self.area = "130000" # 東京都
            self.detail_area = "130010" # 東京地方
            self.observatory = "44132" # 東京
        else:
            pass
        return
    
    def get_datetime(self):
        # アメダスから日付情報を取得
        latest_time_url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
        latest_time_req = requests.get(latest_time_url)
        latest_datetime = datetime.strptime(latest_time_req.text, "%Y-%m-%dT%H:%M:%S%z")
        datetime_data = latest_datetime.strftime('%Y%m%d')
        interval_3hour = ("0" + str((latest_datetime.hour//3)*3))[-2:]
        return datetime_data, interval_3hour
    
    def get_weather(self):
        forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{self.area}.json"
        forecast_req = requests.get(forecast_url)
        forecast_data = forecast_req.json()
        forecast_data = forecast_data[0]["timeSeries"][0]["areas"] #エリア毎の予報データ
        forecast_data_target_index = index = [num for num, i in enumerate(forecast_data) if i["area"]["code"] == self.detail_area][0]
        weathers = forecast_data[forecast_data_target_index]["weathers"] # 今日、明日の天気
        
        today_weather = re.sub(r"\s", "", weathers[0])
        tomorrow_weather = re.sub(r"\s", "", weathers[1])
        return today_weather, tomorrow_weather
    
    def get_overview(self):
        overview_url = f"https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{self.area}.json"
        overview_req = requests.get(overview_url)
        overview_data = overview_req.json() # 天気概況
        overview_text = "\n".join(overview_data["text"].split())
        return overview_text
    
    def get_temperature_precipitation(self):
        amedas_url = f"https://www.jma.go.jp/bosai/amedas/data/point/{self.observatory}/{self.datetime_data}_{self.interval_3hour}.json"
        amedas_req = requests.get(amedas_url)
        amedas_data = amedas_req.json()
        latest_key = max(amedas_data)
        temperature = str(amedas_data[latest_key]["temp"][0])
        precipitation = str(amedas_data[latest_key]["precipitation10m"][0])
        return temperature, precipitation
    
    def button_push(self):
        self.set_area(combo.get())
        root.destroy()
    
    def view_detail(self):
        detail_view = ctk.CTk()
        detail_view.title("天気予報")
        detail_temperature = ctk.CTkLabel(master=detail_view, text=self.detail_array[0], font=("Arial", 12))
        detail_temperature.place(relx=0.5, rely=0.5)
        detail_temperature.pack(anchor=ctk.W)
        detail_precipitation = ctk.CTkLabel(master=detail_view, text=self.detail_array[1], font=("Arial", 12))
        detail_precipitation.place(relx=0.5, rely=0.5)
        detail_precipitation.pack(anchor=ctk.W)
        detail_today_weather = ctk.CTkLabel(master=detail_view, text=self.detail_array[2], font=("Arial", 12))
        detail_today_weather.place(relx=0.5, rely=0.5)
        detail_today_weather.pack(anchor=ctk.W)
        detail_tomorrow_weather = ctk.CTkLabel(master=detail_view, text=self.detail_array[3], font=("Arial", 12))
        detail_tomorrow_weather.place(relx=0.5, rely=0.5)
        detail_tomorrow_weather.pack(anchor=ctk.W)
        detail_overview = ctk.CTkLabel(master=detail_view, text=self.detail_array[4], font=("Arial", 12))
        detail_overview.place(relx=0.5, rely=0.5)
        detail_overview.pack(anchor=ctk.W)
        detail_view.mainloop()
        
    def toast_click(self, event):
        self.view_detail()

if __name__=="__main__":
    self = weather_forecast()
    
    # 地域選択ダイアログ表示
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.geometry("200x120")
    root.title("天気予報")
    label = ctk.CTkLabel(master=root, text="天気予報の地域", font=("Arial", 18))
    label.place(relx=0.5, rely=0.5, anchor=ctk.S)
    label.pack()
    
    prefectures = ["愛知県", "大阪府", "東京都"]
    combo = ctk.CTkComboBox(master=root, values=prefectures, state="readonly")
    combo.set("愛知県")
    combo.place(relx=0.5, rely=0.5, anchor=ctk.S)
    combo.pack()
    
    button = ctk.CTkButton(master=root, text="選択", command=self.button_push)
    button.place(relx=0.5, rely=0.5, anchor=ctk.S)
    button.pack(pady=12)
    root.mainloop()

    # 地域選択されない場合は終了
    if self.area is None:
        exit()

    
    
    while True:
        # 気温、降水量取得
        self.datetime_data, self.interval_3hour = self.get_datetime()
        temperature, precipitation = self.get_temperature_precipitation()
    
        # 今日、明日の天気
        today_weather, tomorrow_weather = self.get_weather()
    
        # 概況
        overview = self.get_overview()
        
        weather_data = [f"現在の気温  ：{temperature} 度",
                        f"現在の降水量：{precipitation} mm/10分",
                        f"今日の天気  ：{today_weather}"]
    
        toast_string = "\n".join(weather_data)
        weather_data.append(f"明日の天気  ：{tomorrow_weather}")
        weather_data.append(f"天気概況    ：{overview}")
        self.detail_array = weather_data
    
        toast("天気予報", toast_string, on_click=self.toast_click)
        
        # AM:0時に終了
        if self.interval_3hour == 0:
            exit()
        
        time.sleep(10800) # 3時間ごとに表示

