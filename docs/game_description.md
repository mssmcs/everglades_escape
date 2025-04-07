# **Everglades Escape \- Gameplay Mechanics**

## **1\. Overview & Setting**

"Everglades Escape" places you in the role of a leader guiding a small party (perhaps a family or band) through the perilous Florida Everglades around 1000 AD. The core premise is survival against the clock, fleeing an impending environmental catastrophe (like a major hurricane or flood) while navigating a complex, water-logged environment teeming with both resources and dangers. Success hinges on careful resource management, strategic navigation, and responding effectively to unpredictable events.

## **2\. Core Objective**

The primary goal is to travel from your starting location to a designated safe destination within a strict time limit (measured in days). Failure to reach the destination before the deadline, or the loss of your entire party, results in failure.

## **3\. The Journey: Travel & Navigation**

* **Mode of Travel:** Movement relies primarily on dugout canoes through the "river of grass" – a network of sloughs, rivers, and coastal routes. Some travel on foot across shallower marshes or elevated hardwood hammocks may be necessary or possible.  
* **Navigation:** There is no single trail. Navigation involves interpreting the landscape, potentially following known water trails, using landmarks (distinctive tree groupings, ancient shell mounds), and managing the risks of getting lost in confusing waterways like mangrove tunnels. Travel likely occurs between defined points or nodes on a map representing key locations (hammocks, river forks, coastal sites).  
* **Pace & Risks:** Travel speed depends on factors like paddling effort (party health/energy), canoe condition, water currents, and potential hazards. Each travel segment consumes time and may carry risks like damaging the canoe on submerged obstacles (logs, rocks), encountering wildlife, or facing adverse weather.

## **4\. Resource Management**

Resource scarcity and management are central to survival. Unlike games with towns and shops, resources are primarily acquired directly from the environment.

* **Food:** A constant concern. Food must be continuously gathered, hunted, or fished.  
  * *Sources:* Fish, turtles, snails, shellfish, alligators, birds, deer (on hammocks), and various plants (hearts of palm, cocoplum, sea grape, tubers like coontie – requiring processing).  
  * *Acquisition:* Success depends on location, season, available tools, party skill/health, and luck. Actions like forage\_and\_fish or hunt will consume time.  
  * *Spoilage:* Food may spoil quickly in the heat and humidity, requiring careful management or preservation techniques (if implemented).  
* **Water:** Generally available, but ensuring access to clean water or transporting it might be a minor challenge.  
* **Canoe Condition:** The canoe is a critical resource, analogous to the wagon in other trail simulations.  
  * *Damage:* Can be damaged by submerged hazards, storms, or aggressive wildlife (e.g., alligators).  
  * *Repair:* Requires finding suitable materials (wood, fibers for lashing, potentially resin/tar) and spending time on repairs. A destroyed canoe could be catastrophic.  
* **Tools:** Essential for resource acquisition.  
  * *Types:* Fishing gear (nets, spears, hooks made of bone/shell), hunting tools (spears, atlatls/darts), traps/snares.  
  * *Durability:* Tools may break with use or be lost, requiring time and resources to craft replacements.

## **5\. Party Management**

Keeping your party members alive, healthy, and functional is paramount.

* **Health Threats:** Dangers are specific to the Everglades environment:  
  * *Wildlife:* Venomous snakes, alligator attacks.  
  * *Environmental:* Insect-borne diseases (fevers), infections from cuts/scratches exposed to swamp water.  
  * *General:* Malnutrition, injuries from difficult terrain or accidents.  
* **Status Effects:** Party members can suffer from conditions like injured, sick, snakebitten, exhausted, or hungry, impacting their ability to contribute or even threatening their survival. Rest and specific actions may be needed to recover.

## **6\. Core Gameplay Loop**

The game progresses in turns, typically representing parts of a day or a full day. Each turn generally follows this cycle:

1. **Display Status:** The current game state is presented (Day, Time Remaining, Food Stores, Canoe Condition, Party Health/Status, Current Location).  
2. **Check End Conditions:** The game checks if a win (reached destination) or loss (out of time, party wiped out) condition has been met.  
3. **Present Actions:** Available player actions are listed (e.g., Paddle, Forage/Fish, Hunt, Repair Canoe, Rest, Manage Inventory).  
4. **Get Player Input:** The player chooses an action.  
5. **Execute Action:** The chosen action's logic is executed, consuming time and potentially resources, modifying the game state, and providing feedback on the outcome.  
6. **Environmental Effects/Events:** Random or triggered events occur (weather changes, wildlife encounters, resource discoveries).  
7. **Advance Time:** Game time progresses, and daily effects are applied (food consumption, potential health changes).  
8. **Repeat:** The loop begins again.

## **7\. Events & Challenges**

The journey is punctuated by events reflecting the dynamic Everglades environment:

* **Weather:** Intense thunderstorms (lightning risk, flash floods), debilitating heat, droughts (affecting travel and resources), seasonal flooding, potentially devastating hurricanes.  
* **Wildlife Encounters:** Both dangerous (alligator attacks, snake bites, panther sightings) and potentially beneficial (finding a large school of fish, a vulnerable prey animal, a bird colony).  
* **Navigation Challenges:** Getting lost, finding routes blocked (fallen trees, low water), making poor route choices.  
* **Resource Crises:** Tools breaking at critical moments, food stores spoiling, canoe springing a leak, periods of poor hunting/fishing luck.  
* **Human Encounters:** Meeting other bands (ancestors of Calusa/Tequesta) – presenting opportunities for trade or information sharing, but also potential conflict or the need for avoidance.

## **8\. Winning and Losing**

* **Winning:** Successfully navigate your party to the designated destination location before the time limit expires. The condition of the party upon arrival might influence the quality of the win.  
* **Losing:**  
  * Running out of time before reaching the destination.  
  * The death or incapacitation of the entire party.  
  * Potentially, the irrecoverable loss of a critical resource like the canoe in a hostile location.