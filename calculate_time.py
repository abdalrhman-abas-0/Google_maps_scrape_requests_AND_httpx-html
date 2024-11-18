"""tracks the time taken for crawling.

Typical usage example:

    from time import time
    
    start_time = time()
    hours, minutes, seconds = Calculate_Runtime(start_time)
    print(f"it took {hours}:{minutes}:{seconds} to run the program.")
"""

from time import time

def Calculate_Runtime(start_time):
    """Calculates the runtime of a process.

    Args:
        start_time (float): The start time of the process in seconds since the epoch.

    Returns:
        tuple: A tuple containing:
            - hours (int): The number of hours elapsed.
            - minutes (int): The number of minutes elapsed.
            - seconds (int): The number of seconds elapsed.
    
    Example:
        >>> start = time()
        >>> # Some process
        >>> hours, minutes, seconds = Calculate_Runtime(start)
    """
    end_time = time()  # Get the current time
    runtime_seconds = end_time - start_time  # Calculate the total runtime in seconds
    hours = int(runtime_seconds / 3600)  # Convert seconds to hours
    minutes = int((runtime_seconds % 3600) / 60)  # Calculate remaining minutes
    seconds = int(runtime_seconds % 60)  # Calculate remaining seconds
    return hours, minutes, seconds  # Return the runtime as a tuple
