import threading

# Define message lists and events
messages_user_response = []
messages_consumed_user_event = threading.Event()

messages_get_all_user_response = []
messages_consumed_get_all_user_event = threading.Event()

messages_get_by_id_user_response = []
messages_consumed_get_by_id_user_event = threading.Event()


# Define locks for each message list
lock_user_response = threading.Lock()
lock_get_all_user_response = threading.Lock()
lock_get_by_id_user_response = threading.Lock()
