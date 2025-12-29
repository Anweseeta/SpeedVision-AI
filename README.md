🚗 SpeedVision AI  
 Real-Time Vehicle Speed Detection System using Computer Vision

SpeedVision AI is a computer vision–based application that detects vehicles and estimates their speed in real time from video input.  
The system uses YOLO object detection combined with motion analysis to monitor traffic and identify overspeeding vehicles.

 ✨ Key Features
- 🚘 Real-time vehicle detection using YOLO
- 📏 Speed estimation using frame-to-frame displacement
- 🚨 Overspeed vehicle identification
- 🎥 Supports video file input (camera support optional)
- 📊 Visual output with bounding boxes and speed labels

 🧠 Tech Stack
- Python
- YOLO (Ultralytics)
- OpenCV
- NumPy
- (Optional) Streamlit / Flask for UI

 ⚙️ How It Works
1. Video frames are read sequentially  
2. YOLO detects vehicles in each frame  
3. Vehicles are tracked across frames  
4. Speed is calculated using distance over time  
5. Overspeeding vehicles are highlighted in the output  

 ▶️ Installation & Usage
 1️⃣ Clone the repository
```bash
git clone https://github.com/Anweseeta/SpeedVision-AI.git
cd SpeedVision-AI
```  
2️⃣ Create and activate virtual environment
```  
python -m venv venv
venv\Scripts\activate
```  
3️⃣ Install dependencies
```  
pip install -r requirements.txt
```  
4️⃣ Run the application
```  
python src/main.py
```  
📌 Note: YOLO weights are automatically downloaded during the first run.

🌐 Live Demo
https://speedy-vision-heart.lovable.app

🚀 Future Enhancements

•	Multi-lane speed analysis

•	Automatic Number Plate Recognition (ANPR)

•	Real-time dashboard for traffic analytics

•	Cloud and edge deployment support

👩‍💻 Author
Anweseeta Sahoo
B.Tech CSE (AIML)
Hyderabad, India
🔗 GitHub: https://github.com/Anweseeta

⭐ If you find this project useful, please give it a star!

