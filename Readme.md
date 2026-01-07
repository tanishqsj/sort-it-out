# Sort It Out 🕹️

> *Fixing the chaos, one beep at a time.*

**Sort It Out** is an interactive, game-styled sorting algorithm visualizer built with Python and Pygame. It reimagines standard computer science algorithms as an 8-bit audio-visual experience.

Instead of just watching bars move, you *hear* the logic. The application features a custom-built sound engine that synthesizes 8-bit square waves in real-time—higher values produce higher pitches, creating a "chiptune" melody as the data organizes itself.

![Project Demo](demo.gif)
*(Note: Add a gif of your project here to make the repo pop!)*

## 🌟 Key Features

* **🕹️ Game-Style UI:** A custom control dashboard built from scratch (no external UI libraries) featuring sliders, input fields, and interactive buttons.
* **🎹 Real-Time Audio Synthesis:** Uses `numpy` and `pygame.sndarray` to generate audio on the fly. No pre-recorded MP3s—this is pure math converted to sound.
* **🏆 The Victory Sweep:** Upon completion, the visualizer performs a satisfying "green sweep" accompanied by an ascending musical scale.
* **🐢 to 🐇 Speed Control:** Dynamic speed adjustment allowing for frame-by-frame analysis or 120 FPS chaos.
* **🔒 Bogo Safety Protocol:** Includes a special override for "Bogo Sort" that locks the array size to 7 elements, preventing infinite loops and CPU meltdown.

## 📦 Algorithms Included

1.  **Bubble Sort:** The classic sinking sort.
2.  **Insertion Sort:** Building the sorted list one item at a time.
3.  **Selection Sort:** Finding the minimum and swapping.
4.  **Quick Sort:** Divide and conquer.
5.  **Heap Sort:** Using a binary heap structure.
6.  **Cocktail Shaker Sort:** Bubbling in both directions.
7.  **Gnome Sort:** The "garden gnome" approach to sorting.
8.  **Bogo Sort:** The "Honorable Mention" (Random shuffling until sorted).

## 🛠️ Installation

### Prerequisites
* Python 3.10+
* pip

### Setup
1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/sort-it-out.git](https://github.com/YOUR_USERNAME/sort-it-out.git)
    cd sort-it-out
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you don't have a requirements file, just run: `pip install pygame numpy`*

3.  **Run the application**
    ```bash
    python main.py
    ```

## 🎮 Complete Walkthrough

The interface is divided into two sections: the **Visualizer Arena** (top) and the **Control Deck** (bottom).

### 1. Setting the Stage
* **Size Input:** Locate the text box labeled `Size`. Type a number between **5** and **600**.
    * *Recommendation:* Use **50-100** for the best balance of visuals and distinct audio notes.
    * *Press Enter* to generate a new randomized array.
* **Speed Slider:** Drag the yellow knob left or right.
    * **Left:** Slow motion (great for understanding how Quick Sort partitions data).
    * **Right:** Turbo mode (great for hearing the "texture" of the algorithm).

### 2. Choosing Your Weapon (Algorithm)
* Use the **`<`** and **`>`** arrow buttons to cycle through the available algorithms.
* The current selection is displayed in bold text above the stats counter.

### 3. The Sort
* Press the **START** button.
* **Visuals:**
    * 🟦 **Blue:** Idle elements.
    * 🟥 **Red:** Elements currently being compared.
    * 🟩 **Green:** Elements swapping positions.
* **Audio:** You will hear two distinct pitches corresponding to the two bars being handled.

### 4. The Victory Lap
* Once the array is fully sorted, the **Sweep Phase** begins.
* The visualizer will scan from left to right, turning the bars bright green and playing a perfect ascending scale.

### 5. The Chaos Mode (Bogo Sort)
* Select **BOGO SORT** from the menu.
* **Notice the Change:** The array size automatically locks to **7**. This is intentional! Bogo sort works by randomly shuffling the deck and checking if it's sorted.
    * *Probability:* With 7 items, there are 5,040 permutations. It might take 1 second, or it might take 10 minutes. Good luck!

## 🧠 Technical Highlights

* **Generators over Loops:** The sorting algorithms are implemented as Python **Generators** (`yield`). This allows the main Pygame loop to request the "next step" of the sort one frame at a time, keeping the UI responsive without threading.
* **Audio Envelope:** To make the sound pleasing rather than harsh, a decay envelope is applied to the sine waves, giving them a "plucked" or "percussive" quality similar to 8-bit sound effects.

## 🤝 Contributing

Got a favorite sorting algorithm I missed? (Maybe *Radix Sort* or *Shell Sort*?)
1.  Fork the repo.
2.  Create a generator function for your sort.
3.  Add it to the `self.algos` list in `main.py`.
4.  Submit a Pull Request!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).