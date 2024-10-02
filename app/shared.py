import threading

# Define message lists and events
messages_sensor_data_response = []
messages_consumed_sensor_data_event = threading.Event()

messages_get_all_sensor_data_response = []
messages_consumed_get_all_sensor_data_event = threading.Event()

messages_get_by_id_sensor_data_response = []
messages_consumed_get_by_id_sensor_data_event = threading.Event()

messages_camera_response = []
messages_consumed_camera_event = threading.Event()

messages_get_all_camera_response = []
messages_consumed_get_all_camera_event = threading.Event()

messages_get_by_id_camera_response = []
messages_consumed_get_by_id_camera_event = threading.Event()

messages_prediction_response = []
messages_consumed_prediction_event = threading.Event()

# Define locks for each message list
lock_sensor_data_response = threading.Lock()
lock_get_all_sensor_data_response = threading.Lock()
lock_get_by_id_sensor_data_response = threading.Lock()
lock_camera_response = threading.Lock()
lock_get_all_camera_response = threading.Lock()
lock_get_by_id_camera_response = threading.Lock()
lock_prediction_response = threading.Lock()
