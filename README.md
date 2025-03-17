**Custom Prometheus Agent**
This custom Prometheus agent dynamically discovers and registers functions from Python files within a specified folder, integrating them into a Prometheus connector for real-time monitoring and metrics collection.

***Features***
  1. Automatic Function Discovery – Scans a given directory for Python files and extracts functions.
  2. Dynamic Registration – Registers discovered functions as Prometheus metrics.
  3. Seamless Integration – Connects with Prometheus to expose collected metrics.
  4. Flexible & Extensible – Easily adaptable for different monitoring needs.

***Usage***
  1. Place your Python files containing functions in the designated folder.
  2. Run the agent to automatically register and expose function metrics.
  3. Configure Prometheus to scrape the exposed metrics.
