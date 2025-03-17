**Custom Prometheus Agent**
This custom Prometheus agent dynamically discovers and registers functions from Python files within a specified folder, integrating them into a Prometheus connector for real-time monitoring and metrics collection.

***Features***
Automatic Function Discovery – Scans a given directory for Python files and extracts functions.
Dynamic Registration – Registers discovered functions as Prometheus metrics.
Seamless Integration – Connects with Prometheus to expose collected metrics.
Flexible & Extensible – Easily adaptable for different monitoring needs.
***Usage***
Place your Python files containing functions in the designated folder.
Run the agent to automatically register and expose function metrics.
Configure Prometheus to scrape the exposed metrics.
