import threading

messages_sensor_data_response = []
messages_get_all_sensor_data_response = []
messages_get_by_id_sensor_data_response = []

messages_camera_response = []
messages_get_all_camera_response = []
messages_get_by_id_camera_response = []

messages_prediction_response = []

messages_consumed_sensor_data_event = threading.Event()
messages_consumed_camera_event = threading.Event()
messages_consumed_prediction_event = threading.Event()

