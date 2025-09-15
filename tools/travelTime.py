#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计 tripinfo.xml 中出发时间在给定窗口内 (默认 25200–27000 s) 的:
  1) 车辆数量
  2) 平均行程时间
  3) 平均行驶速度 (m/s 与 km/h)

用法:
    python stats_trip_window.py               # 默认 07:00–07:30
    python stats_trip_window.py 25000 30000   # 自定义时间窗
"""

import sys
import xml.etree.ElementTree as ET

XML_FILE      = "tripinfo.xml"   
DEFAULT_START = 25200.0          # 07:00
DEFAULT_END   = 28800.0          # 07:30


def main():
  
    try:
        start = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_START
        end   = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_END
    except ValueError:
        sys.exit("⛔  起止时间必须是数字 (秒)")

    if start > end:
        start, end = end, start   

   
    total_duration = 0.0   
    total_distance = 0.0   
    count          = 0


    for _event, elem in ET.iterparse(XML_FILE, events=("end",)):
        if elem.tag == "tripinfo":
            depart  = float(elem.attrib["depart"])
            arrival = float(elem.attrib.get("arrival", "-1"))

            if start <= depart <= end and arrival >= 0:   
                total_duration += float(elem.attrib["duration"])
                total_distance += float(elem.attrib["routeLength"])
                count          += 1
            elem.clear()  

   
    if count and total_duration:
        mean_duration   = total_duration / count
        mean_speed_mps  = total_distance  / total_duration
        mean_speed_kph  = mean_speed_mps * 3.6

        print(f"📊 depart ∈ [{start}, {end}] 秒")
        print(f"🚗 number of cars           : {count}")
        print(f"⏱️ average travel time       : {mean_duration:.2f} s")
        print(f"🏎️ average speed           : {mean_speed_mps:.2f} m/s  ≈ {mean_speed_kph:.2f} km/h")
    else:
        print("⚠️ no cars arrived in the specified time window")


if __name__ == "__main__":
    main()
