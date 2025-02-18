import pyautogui
import time
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load date ranges from JSON file
JSON_PATH = "report_downloader/monthly_data_2000_2025_corrected.json"

if not os.path.exists(JSON_PATH):
    logging.error(f"JSON file not found at {JSON_PATH}")
    raise FileNotFoundError(f"JSON file not found at {JSON_PATH}")

with open(JSON_PATH, "r") as file:
    date_ranges = json.load(file)

# UI coordinates (update as necessary)
UI_COORDS = {
    "from_field": (580, 210),
    "refresh_button": (1074, 178),
    "excel_button": (887, 179)
}

CSV_CREATION_IMAGE = "report_downloader/csv_creation.png"


def clear_field():
    """Clears an input field by pressing backspace and delete multiple times."""
    for _ in range(10):
        pyautogui.press(["backspace", "delete"])


def is_image_on_screen(image_path):
    """Checks if an image is currently on screen, returning True if found, False otherwise."""
    try:
        return pyautogui.locateOnScreen(image_path) is not None
    except pyautogui.ImageNotFoundException:
        return False


def wait_for_csv_creation(timeout=60):
    """
    Waits for CSV creation to complete by monitoring the screen.
    Timeout prevents infinite loops.
    """
    logging.info("Waiting for CSV creation process to complete...")
    time.sleep(3)  # Initial wait

    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_image_on_screen(CSV_CREATION_IMAGE):
            logging.info("CSV creation detected as complete.")
            return
        time.sleep(5)

    logging.warning("CSV creation took too long. Continuing execution.")


def cycle(from_date, to_date, filename):
    """Automates UI interactions using PyAutoGUI to export CSV files."""
    logging.info(f"Processing: {filename} ({from_date} to {to_date})")

    try:
        # Click 'From' field and input date
        pyautogui.click(UI_COORDS["from_field"])
        clear_field()
        pyautogui.write(from_date)

        # Tab to 'To' field and input date
        pyautogui.press("tab")
        clear_field()
        pyautogui.write(to_date)

        # Click refresh button
        pyautogui.click(UI_COORDS["refresh_button"])
        time.sleep(13)  # Allow time for refresh

        # Click Excel button
        pyautogui.click(UI_COORDS["excel_button"])

        # Navigate and confirm download
        pyautogui.press(["down", "enter", "enter"])
        time.sleep(1)

        # Input filename and confirm
        pyautogui.write(filename)
        pyautogui.press("enter")

        # Wait for CSV creation to complete
        wait_for_csv_creation()

    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")
        return


def main():
    """Main function to iterate over months and process them."""
    logging.info(f"Starting automated QuickBooks export for {len(date_ranges)} entries.")

    try:
        for idx, entry in enumerate(date_ranges, start=1):
            logging.info(f"Processing entry {idx}/{len(date_ranges)}: {entry['filename']}")
            cycle(entry["from"], entry["to"], entry["filename"])

        logging.info("Data export completed successfully.")

    except KeyboardInterrupt:
        logging.warning("Process interrupted by user. Exiting gracefully.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()