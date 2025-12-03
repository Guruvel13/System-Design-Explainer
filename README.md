📘 System Design Explainer

AI-powered architecture generator using Groq Llama 3.1 (8B Instant)

This project takes a plain English system requirement—e.g.,
“Build a scalable real-time chat application”—and automatically generates:

A detailed system architecture explanation

A structured breakdown of components

A Graphviz architecture diagram

Valid JSON describing nodes and edges

Powered entirely by Groq’s ultra-fast Llama-3.1-8B-Instant model.

🚀 Features

Handles any system requirement

Uses llama-3.1-8b-instant (free, fast, optimized)

Generates detailed and structured system design

Produces valid component diagrams via Graphviz

Fully compatible with Streamlit Cloud

Strong error handling (invalid JSON, API issues, etc.)

🧠 Model Used
llama-3.1-8b-instant

Why this model?

Fastest Groq model

Free to use

Low latency

Strong reasoning for system architecture

Works perfectly on Streamlit Cloud

📂 Project Structure
System-Design-Explainer/
│
├── streamlit_app.py         # Main Streamlit UI
├── llm_client.py            # Groq API + prompt logic
├── diagram_parser.py        # Extract explanation + diagram JSON
├── diagram_builder.py       # Graphviz diagram generator
├── requirements.txt         # Python dependencies
└── README.md                # Documentation

🔧 Setup Instructions
1. Install dependencies
pip install -r requirements.txt

2. Add Your Groq API Key (Streamlit Cloud)

Go to:

Streamlit Cloud → App → Settings → Secrets

Add:

GROQ_API_KEY = "gsk_your_real_key_here"


You do not need .env on Streamlit Cloud.

3. Run Locally (Optional)
streamlit run streamlit_app.py

🧩 How It Works
1. User enters a system requirement

Example:

"Design an e-commerce platform handling 1M daily active users."

2. Streamlit sends the text to Groq:
model="llama-3.1-8b-instant"

3. Groq returns:

[EXPLANATION] — architecture overview

[DIAGRAM_JSON] — component graph in JSON

4. The parser extracts:

Explanation text

Nodes

Edges

5. The UI renders:

Full architecture explanation

A Graphviz component diagram

📈 Example Output
Explanation

Architecture overview

Component list

Data flow

Scaling strategies

Caching

Fault tolerance

Security layers

Monitoring & logging

Trade-offs

Diagram JSON Example
{
  "nodes": ["Client", "API Gateway", "Service A"],
  "edges": [
    ["Client", "API Gateway"],
    ["API Gateway", "Service A"]
  ]
}


Rendered directly using Graphviz.

🛡 Error Handling

Invalid or missing diagram JSON

Missing API key

Groq API request failures

Unexpected model output

The app provides clear and helpful errors for each case.

📝 Requirements
streamlit
groq
graphviz
python-dotenv   # optional

🤝 Contributing

Contributions, issues, and feature requests are welcome.

📜 License

This project is open-source and free to use.

⭐ Acknowledgement

Built using:

Groq API

Llama-3.1-8B-Instant

Streamlit

Graphviz