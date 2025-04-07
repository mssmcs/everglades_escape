# **Everglades Escape \- System Design Document**

Version: 0.1  
Date: April 7, 2025  
Project Status: Conceptual Design Phase  
Development Context: Initial development in Python, text-based interface, designed for future migration to a graphical interface. Developed in Limestone, Maine, United States.  
**Table of Contents:**

1. Introduction  
2. System Architecture  
3. High-Level Components  
4. Core Data Concepts  
5. Gameplay Mechanics Overview  
6. Coding Standards & Software Engineering Principles  
7. Recommended Tooling  
8. Future Development & Graphics Integration Path

## **1\. Introduction**

### **1.1. Purpose:**

This document outlines the design and architecture for "Everglades Escape," a survival simulation game. The game challenges the player to lead a party through the Florida Everglades around 1000 AD, fleeing an impending environmental disaster (hurricane/flood) within a strict time limit.

### **1.2. Goals:**

* Create an engaging survival simulation experience focused on resource management, navigation, and event handling.  
* Develop a maintainable and testable codebase using Python.  
* Implement a text-based interface initially.  
* Design the core logic independently of the interface to facilitate future porting to a graphical engine.  
* Adhere to sound software engineering principles and coding standards.

### **1.3. Target Audience (Initial):**

Players interested in simulation, survival, and historical/environmental themes, comfortable with text-based interactions.

### **1.4. Technology Stack (Initial):**

* **Language:** Python (latest stable version recommended)  
* **Interface:** Standard Text Console I/O

## **2\. System Architecture**

### **2.1. Architectural Pattern:**

The system will follow a pattern inspired by Model-View-Controller (MVC), emphasizing Separation of Concerns. This is crucial for achieving the goal of UI-independent core logic.

* **Model (Core Logic & State):** Represents the game's data (party status, resources, location, time, events) and enforces the game rules. It contains all simulation logic and state manipulation functions. *Crucially, the Model will have no knowledge of how information is displayed or how player input is gathered.* This layer encapsulates the fundamental simulation.  
* **View (Presentation):** Responsible for presenting the game state to the player. In the initial version, this will be text output to the console. In a future graphical version, this layer would handle rendering graphics, UI elements, etc. It reads data from the Model (or receives it via the Controller) but does not modify it.  
* **Controller (Input & Orchestration):** Handles player input, interprets it into commands, interacts with the Model to update the game state based on those commands, and instructs the View on what to display. It acts as the intermediary between the user, the Model, and the View.

### **2.2. Benefits:**

* **Reusability:** The Model (core game logic) can be reused with different Views/Controllers (text, graphical).  
* **Testability:** The Model can be tested independently of the UI, allowing for automated unit and integration tests of the game mechanics.  
* **Maintainability:** Changes to the UI don't necessitate changes to the core game logic, and vice versa. Code is organized logically.  
* **Collaboration:** Different developers could potentially work on the Model and View/Controller layers somewhat independently.

## **3\. High-Level Components**

The system will be logically divided into several key areas of responsibility, aligning with the MVC pattern:

* Core Simulation Engine:  
  * Responsibilities: Manages the central game state (time, resources, party status, location, events, win/loss conditions). Applies time-based effects (e.g., daily consumption), checks game rules and conditions. This forms the heart of the Model.  
* Player Action Logic:  
  * Responsibilities: Implements the specific consequences of player choices (e.g., travel, forage, rest). Calculates outcomes, modifies the game state accordingly, and determines resource/time costs. This is also part of the Model.  
* Environmental Simulation:  
  * Responsibilities: Handles world-related aspects like random events, weather effects (if any), location-specific properties, and the progression of the overarching disaster. Operates on the game state, often independently of direct player commands. Part of the Model.  
* User Interface (Presentation & Input):  
  * Responsibilities: Handles all direct interaction with the user. Displays game status, messages, and prompts. Captures and parses user input. This component acts as the View and part of the Controller (input handling).  
* Application Orchestrator / Game Loop:  
  * Responsibilities: Initializes the system, runs the main game loop, coordinates the flow of control between receiving input (Controller), updating the simulation (Model), and displaying results (View). This is the primary Controller logic.

## **4\. Core Data Concepts**

The simulation relies on structured data representing the game world and player status:

* Central State Container: An object or structure holding all current, dynamic game information (day, time remaining, party resources, current location reference, active events, overall party condition, win/loss status). This is the primary data manipulated by the Model and read by the View/Controller.  
* Party Member Representation: Data structures defining individual party members, including attributes like health, hunger, and any status effects (e.g., injured, sick). The state container will manage a collection of these.  
* Location Data: Representation of distinct areas in the game world, including connections to other locations, travel costs/risks, and potentially location-specific attributes (resource availability, hazards).  
* Event Data: Structures defining game events (random or triggered), including descriptive text, trigger conditions, and their effects on the game state (e.g., changes to resources, health, time).  
* Action Results & State Queries: Functions modifying the state (Model) should return structured data indicating outcomes (e.g., messages, time elapsed) rather than directly interacting with the UI. Functions querying the state should return data structures (like dictionaries) suitable for the UI (View) to present. This enforces separation.

## **5\. Gameplay Mechanics Overview**

* **Objective:** Travel from a starting location to a destination before a time limit expires, managing resources and party well-being.  
* **Core Loop:**  
  1. Display current status (View).  
  2. Check for Game Over/Win conditions (Model/Controller).  
  3. Present available actions to player (Controller/View).  
  4. Get player input (Controller).  
  5. Execute chosen action logic (Controller invokes Model).  
  6. Trigger/resolve environmental effects/events (Model).  
  7. Advance game time and apply time-based effects (Model).  
  8. Repeat.  
* **Resource Management:** Balance essential resources like Food, Party Health, and potentially tool/vehicle condition (e.g., Canoe).  
* Travel: Movement between defined locations, consuming time and potentially resources, possibly incurring risks.  
* Time Limit: A core constraint driving urgency and potentially linked to increasing environmental threats.  
* Events: Random or triggered occurrences impacting the party's situation.

## **6\. Coding Standards & Software Engineering Principles**

Adherence to these principles is expected to ensure code quality, maintainability, and readability.

### **6.1. Style Guide:**

* **PEP 8:** Follow Python's official style guide (PEP 8\) for code formatting, naming conventions, and layout.  
  * *Tools:* Use flake8 for checking compliance and black for automatic formatting. isort for import sorting.  
* **Naming Conventions:**  
  * snake\_case for variables, functions, and methods.  
  * PascalCase for classes.  
  * UPPER\_SNAKE\_CASE for constants.  
  * Use clear, descriptive names. Avoid single-letter variables except in very small, obvious scopes (like loop counters).  
* **Comments & Docstrings:**  
  * Use \# inline comments for explaining complex or non-obvious lines.  
  * Use """Docstrings""" for modules, classes, functions, and methods to explain their purpose, arguments, and return values. Follow PEP 257 conventions.

### **6.2. Core Principles:**

* **DRY (Don't Repeat Yourself):** Avoid duplicating code. Use functions, classes, and loops to abstract common logic. If you copy-paste code, consider refactoring it into a reusable unit.  
* **KISS (Keep It Simple, Stupid):** Favor simple, straightforward solutions over complex ones, especially early on. Avoid premature optimization or overly abstract designs.  
* **YAGNI (You Ain't Gonna Need It):** Do not implement features or abstractions until they are actually required by the current needs of the project. Focus on delivering the core functionality first.

### **6.3. SOLID Principles:**

* **S \- Single Responsibility Principle (SRP):** Each class or logical component should have one primary responsibility or reason to change. *Example:* The UI component handles presentation, the Core Simulation Engine manages state – they change for different reasons.  
* **O \- Open/Closed Principle (OCP):** Software entities should be open for extension but closed for modification. *Example:* Adding a new player action should ideally involve adding new logic within the Player Action component and registering it with the Orchestrator, not modifying the core game loop logic extensively.  
* **L \- Liskov Substitution Principle (LSP):** Subtypes should be substitutable for their base types without altering the correctness of the program. *Example:* If introducing different Event types later, the core event handling logic should work correctly with any Event type adhering to a common interface.  
* **I \- Interface Segregation Principle (ISP):** Clients should not be forced to depend on interfaces (methods) they do not use. Aim for smaller, more focused interfaces between components.  
* **D \- Dependency Inversion Principle (DIP):** High-level modules (like the Orchestrator) should not depend directly on low-level modules (specific action implementations). Both should depend on abstractions (like defined interfaces for actions or state updates). This is key for separating the UI and enabling testability.

## **7\. Recommended Tooling**

* **Version Control:** **Git**. Essential for tracking changes, collaboration, and reverting errors. Use platforms like GitHub, GitLab, or Bitbucket for remote repositories. *Commit frequently with clear messages.* Use branches for developing new features.  
* **Virtual Environments:** **venv** (Python's built-in module). Crucial for isolating project dependencies and avoiding conflicts with system-wide packages. Always work within an activated virtual environment. Create a requirements.txt file.  
* **Linter:** **flake8**. Checks for PEP 8 compliance and common coding errors. Integrate into your editor or run manually.  
* **Formatter:** **black**. Automatically formats code to a consistent style, reducing arguments about formatting. Run before committing.  
* **Import Sorter:** **isort**. Automatically sorts and formats import statements.  
* **Testing Framework:** **pytest**. Allows writing clear, concise unit and integration tests for the core logic (Model components). Aim for good test coverage of the simulation engine and action logic.  
* **Debugger:** Python's built-in **pdb** or IDE-integrated debuggers (like in VS Code, PyCharm). Essential for stepping through code and diagnosing issues.

## **8\. Future Development & Graphics Integration Path**

* **Graphics Integration:** The Separation of Concerns architecture directly supports this. To create a graphical version:  
  1. Keep the existing Model components (Core Simulation Engine, Player Action Logic, Environmental Simulation).  
  2. Replace the text-based User Interface component with a new one using a graphical library (e.g., Pygame, Kivy, Godot via Python bindings). This new component fulfills the View and input-handling Controller roles graphically.  
  3. The new graphical layer will call the *same* Model interfaces to get state information and execute actions. It will then render this information visually.  
  4. The Application Orchestrator may need adaptation to manage the graphical environment's event loop.  
* **Potential Expansions:** Crafting system, more detailed health/illness simulation, more complex character skills, dynamic weather patterns, AI for other encountered groups, procedural map generation elements. The component-based design should make adding these features manageable by isolating their logic within specific components or new ones.