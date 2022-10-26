from time import sleep
from resumatcd4 import ResumatCD4
from mqtt import MQTT
import config
import logging

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger()


cd4 = ResumatCD4(config.CD4_DEV, config.CD4_BAUDRATE)
mqtt = MQTT(config.MQTT_HOST, config.MQTT_PORT)


attributes = [
    "Temp-Aussen",
    "Temp-Ruecklauf-Soll",
    "Temp-Ruecklauf",
    "Temp-Vorlauf",
    "Temp-WW-Soll",
    "Temp-WW-Ist",
    "Temp-Raum",
    "Temp-WQuelle-Ein",
    "Temp-WQuelle-Aus",
    "Unterbrechungen",
    "WarnungEingang",
    "WarnungAusgang",
    "WarnungSonstige",
    "Ausfall",
    "Betriebszustaende",
    "Mode-Heizung",
    "Mode-Kuehlung",
    "Mode-Warmwasser",
]

attr_retrieval_order = [[attr_id, ResumatCD4.attributes[attr_id].poll_intervall] for attr_id in attributes]

for attr_id in attributes:
    mqtt.publish_hass_config(ResumatCD4.attributes[attr_id])
    value = cd4.get_attr(attr_id)
    mqtt.publish_value(attr_id, value)

while True:
    attr_retrieval_order.sort(key = lambda e : e[1])
    min_sleep_duration = attr_retrieval_order[0][1]
    sleep(min_sleep_duration)
    
    attr_retrieval_order = [[n, i-min_sleep_duration] for n,i in attr_retrieval_order]

    while len(attr_retrieval_order) > 0 and attr_retrieval_order[0][1] <= 0:
        attr_id, _ = attr_retrieval_order.pop(0)
        value = cd4.get_attr(attr_id)
        mqtt.publish_value(attr_id, value)
        attr_retrieval_order.append([attr_id, ResumatCD4.attributes[attr_id].poll_intervall])