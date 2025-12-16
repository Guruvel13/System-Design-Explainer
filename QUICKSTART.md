# 🚀 Quick Start Guide - SystemSketch AI

## Prerequisites
- Python 3.8 or higher
- Groq API Key ([Get one free here](https://console.groq.com))

## Installation

### 1️⃣ Clone or Download the Repository
```bash
cd System-Design-Explainer
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Your Groq API Key

**Option A: Environment Variable (Recommended for local testing)**
```powershell
# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_api_key_here"

# Linux/Mac
export GROQ_API_KEY="gsk_your_api_key_here"
```

**Option B: Streamlit Secrets (Recommended for deployment)**
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_api_key_here"
```

**Option C: .env File**
Create `.env` in the project root:
```env
GROQ_API_KEY=gsk_your_api_key_here
```

### 4️⃣ Run the Application
```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🎯 How to Use

### Step 1: Describe Your System
Enter a detailed system requirement in the text area:

**Examples:**
- "Design a scalable e-commerce platform handling 1M daily active users with real-time inventory management"
- "Build a video streaming service like Netflix with CDN, adaptive bitrate, and recommendation engine"
- "Create a ride-sharing app like Uber with real-time GPS tracking, payment processing, and surge pricing"

### Step 2: Generate Architecture
Click the "✨ Generate Architecture" button

### Step 3: Review Results
- **Architecture Explanation**: Comprehensive breakdown with 18 subsections
- **Architecture Diagram**: Visual representation of your system
- **Export Options**: Download PNG or PDF versions

---

## 🎨 Features

✨ **AI-Powered Generation** - Llama 3.1 8B Instant model  
🎨 **Professional Diagrams** - Graphviz visualization  
📥 **Export Ready** - PNG and PDF downloads  
🌙 **Premium Dark UI** - Glassmorphism design  
⚡ **Fast Responses** - Optimized for speed  
🔒 **Secure** - API key management  

---

## 🛠 Troubleshooting

### "GROQ_API_KEY missing" Error
- Make sure you've set the API key using one of the methods above
- Verify the key is correct and active
- Restart the Streamlit app after setting the key

### "Export failed" Warning
- This means Kroki.io service is temporarily unavailable
- You can still view and use the diagram in the browser
- Try exporting again later or take a screenshot

### Diagram Not Showing
- The AI might have generated invalid JSON
- Click "Show Raw AI Output" to see what was generated
- Try refining your prompt to be more specific

---

## 📊 System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Internet**: Required for Groq API and Kroki.io
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

---

## 🌐 Deployment Options

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `GROQ_API_KEY` to Secrets
4. Deploy!

### Other Platforms
- **Heroku**: Use Procfile
- **AWS/GCP/Azure**: Standard Python deployment
- **Docker**: Create Dockerfile with Python + dependencies

---

## 💡 Tips for Best Results

### Writing Good Prompts
✅ **Be Specific**: Include user count, features, technologies  
✅ **Mention Scale**: Daily users, requests per second  
✅ **List Requirements**: Security, availability, latency  
✅ **Include Constraints**: Budget, timeline, team size  

### Example Good Prompt
```
Design a social media platform for 10M daily active users with:
- Real-time messaging and notifications
- Image/video uploads up to 100MB
- News feed with personalized recommendations
- 99.9% uptime requirement
- GDPR compliance
- Support for 50K concurrent connections
```

### Example Poor Prompt
```
Make a website
```

---

## 🔗 Resources

- [Groq Documentation](https://console.groq.com/docs)
- [Streamlit Docs](https://docs.streamlit.io)
- [Graphviz Guide](https://graphviz.org/documentation/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

## 📝 License
Open source and free to use

---

## 🤝 Support
For issues or questions, please review the error details in the expander sections or check the troubleshooting guide above.

---

**Happy Architecture Design! 🎉**
