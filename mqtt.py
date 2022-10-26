import logging
from paho.mqtt import client as mqtt_client
import json

from resumatcd4 import BitField
logger = logging.getLogger()


class MQTT:
    def __init__(self, host = "localhost", port = 1883) -> None:
        mqtt_client_id = "hass_resumatcd4"
        self.client = mqtt_client.Client(mqtt_client_id)
        self.client.connect(host, port)

    def build_hass_config(self, attr):
        config =  {
            "name": attr.pretty_name,
            "unique_id": make_unique_id_for(attr.id),
            "state_topic": make_topic_for(attr.id),
            "value_template": "{{ value_json.value }}",
            "device": {
                "name": "Heizung",
                "manufacturer": "Waterkottte",
                "model": "ResümatCD4",
                "identifiers": "ResümatCD4"
                },
        }
        if attr.unit:
            config["unit_of_measurement"] = attr.unit
        if attr.device_class: 
            config["device_class"] = attr.device_class
        if not issubclass(attr.type, BitField):
            config["state_class"] = "measurement"
        return config

    def publish_hass_config(self, attr):
        config = self.build_hass_config(attr)
        config_topic = "homeassistant/sensor/" + make_unique_id_for(attr.id) + "/config"
        self.client.publish(config_topic, json.dumps(config), retain = True)


    def publish_value(self, attr_id, value):
        if value.toJson() == "":
            return
        payload = json.dumps({"name": attr_id, "value": value.toJson()})
        topic = make_topic_for(attr_id)
        logger.debug("Publish %s on %s", payload, topic)
        self.client.publish(topic, payload)

def make_topic_for(attr_id):
    return "heizung/" + slugify(attr_id)

def make_unique_id_for(attr_id):
    return "hzg_" + slugify(attr_id)

def slugify(text):
    return text
