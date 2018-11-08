import os
import sys
import json
import xml.etree.cElementTree as cET
from datetime import datetime
from math import floor

SPORT_TYPES = {
    22: 'racecycling'
}


def __indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            __indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def __print_help():
    print("Usage: python " + sys.argv[0] + "data_dir out_dir")
    print("where data_dir is the path to your session data")
    print("and out_dir the path where your converted .tcx files will be saved.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        __print_help()
        exit(0)

    root = sys.argv[1]
    out = sys.argv[2]
    activities = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    for activity in activities:
        with open(os.path.join(root, activity), 'r') as header_file:
            header = json.loads(header_file.readline())

            start_time = datetime.utcfromtimestamp(header.get('start_time') / 1000)
            duration = str(floor(header.get('duration') / 1000))
            distance = str(header.get('distance'))
            calories = str(header.get('calories'))
            pulse_avg = str(header.get('pulse_avg'))
            pulse_max = str(header.get('pulse_max'))
            max_speed = str(header.get('max_speed') / 3.6)
            cadence = str(header.get('avg_cadence'))
            sport_type = SPORT_TYPES.get(int(header.get('sport_type_id')))

            xml_tree = cET.parse('template.xml')
            xml_root = xml_tree.getroot()

            xml_root.set('xsi:schemaLocation',
                         "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 " +
                         "http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")
            xml_root.set('xmlns:ns5', "http://www.garmin.com/xmlschemas/ActivityGoals/v1")
            xml_root.set('xmlns:ns3', "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
            xml_root.set('xmlns:ns2', "http://www.garmin.com/xmlschemas/UserProfile/v2")
            xml_root.set('xmlns', "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
            xml_root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
            xml_root.set('xmlns:ns4', "http://www.garmin.com/xmlschemas/ProfileExtension/v1")

            activity_tag = xml_tree.find('./Activities/Activity')
            activity_tag.set('Sport', sport_type)
            activity_tag.find('Id').text = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            lap_tag = activity_tag.find('Lap')
            lap_tag.set("StartTime", start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
            lap_tag.find("TotalTimeSeconds").text = duration
            lap_tag.find("DistanceMeters").text = distance
            lap_tag.find("Calories").text = calories
            lap_tag.find("AverageHeartRateBpm/Value").text = pulse_avg
            lap_tag.find("MaximumHeartRateBpm/Value").text = pulse_max
            lap_tag.find("MaximumSpeed").text = max_speed
            lap_tag.find("Cadence").text = cadence

            track_tag = lap_tag.find("Track")

            try:
                with open(os.path.join(root, 'GPS-data', activity), 'r') as gps_file:
                    for trackpoint in json.loads(gps_file.read()):
                        trackpoint_time = datetime.strptime(trackpoint.get('timestamp'), '%Y-%m-%d %H:%M:%S %z')
                        trackpoint_time = trackpoint_time - trackpoint_time.utcoffset()
                        trackpoint_distance = str(trackpoint.get('distance'))
                        trackpoint_altitude = str(trackpoint.get('altitude'))
                        trackpoint_latitude = str(trackpoint.get('latitude'))
                        trackpoint_longitude = str(trackpoint.get('longitude'))

                        trackpoint_tag = cET.Element('Trackpoint')
                        time_tag = cET.SubElement(trackpoint_tag, 'Time')
                        time_tag.text = trackpoint_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                        distance_tag = cET.SubElement(trackpoint_tag, 'DistanceMeters')
                        distance_tag.text = trackpoint_distance

                        altitude_tag = cET.SubElement(trackpoint_tag, 'AltitudeMeters')
                        altitude_tag.text = trackpoint_altitude

                        position_tag = cET.SubElement(trackpoint_tag, 'Position')
                        latitude_tag = cET.SubElement(position_tag, 'LatitudeDegrees')
                        latitude_tag.text = trackpoint_latitude

                        longitude_tag = cET.SubElement(position_tag, 'LongitudeDegrees')
                        longitude_tag.text = trackpoint_longitude

                        track_tag.append(trackpoint_tag)
            except FileNotFoundError:
                pass
        __indent(xml_root)
        xml_tree.write(
            os.path.join(out, 'runtastic_' + start_time.strftime('%Y%m%d_%H%M_') + sport_type + '.tcx'),
            "UTF-8",
            True
            )
