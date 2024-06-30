import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class _FileWatcher:
    def __init__(self, path):
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Path to watch
        self.path = path

        # Check if the path exists
        if not os.path.exists(self.path):
            self.logger.error(f"The path {self.path} does not exist.")
            exit(1)

        # Create a custom event handler class that prints a message when the file is modified.
        class MyEventHandler(FileSystemEventHandler):
            def __init__(self, watch_path):
                self.watch_path = watch_path
                super().__init__()

            def on_modified(self, event):
                if event.src_path == self.watch_path:
                    print("MOOOO DIIIIII FYYYY")

        self.event_handler = MyEventHandler(self.path)
        self.observer = Observer()

    def start(self):
        # Schedule the observer
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        
        # Start the observer
        self.observer.start()
        try:
            while True:
                # Keep the script running
                time.sleep(1)
        except KeyboardInterrupt:
            # Stop the observer if a keyboard interrupt is received
            self.observer.stop()
        except Exception as e:
            # Log any other exceptions that occur
            self.logger.error(f"An error occurred: {e}")
        finally:
            # Wait for the observer to finish
            self.observer.join()

# # Example usage
# if __name__ == "__main__":
#     path_to_watch = "/home/ubuntu/fl-project/log.txt"
#     file_watcher = FileWatcher(path_to_watch)
#     file_watcher.start()
