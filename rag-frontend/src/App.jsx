import { useState } from "react";
import axios from "axios";

function App() {
  const [files, setFiles] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!files.length) return alert("Select files first!");

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      setLoading(true);
      setError("");
      const res = await axios.post("http://127.0.0.1:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert(res.data.message);
    } catch (err) {
      setError("Upload failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query) return alert("Type a question!");

    try {
      setLoading(true);
      setError("");
      const res = await axios.get("http://127.0.0.1:8000/query", {
        params: { q: query, use_llm: true },
      });

      let parsedAnswer = res.data.answer;
      try {
        parsedAnswer = JSON.parse(res.data.answer);
      } catch {
        // keep as string if not JSON
      }

      setAnswer(parsedAnswer);
      setResults(res.data.results || []);
    } catch (err) {
      setError("Query failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        fontFamily: "Inter, sans-serif",
        minHeight: "100vh",
        padding: "2rem",
        backgroundColor: "#000000ff",
        color: "#eaeaea",
        display: "flex",
        flexDirection: "column",
        alignItems: "start",
      }}
    >
      <div style={{ width: "100%", maxWidth: "950px" }}>
        <h1
          style={{
            fontSize: "2rem",
            fontWeight: "600",
            textAlign: "center",
            marginBottom: "2rem",
            color: "#00c6ff",
            textShadow: "0 0 10px #00c6ff66",
          }}
        >
          Smart Document QA
        </h1>

        {/* Upload Section */}
        <section
          style={{
            background: "#1a1a1a",
            padding: "1rem",
            borderRadius: "8px",
            marginBottom: "1.5rem",
            boxShadow: "0 0 10px rgba(255,255,255,0.05)",
          }}
        >
          <h3 style={{ marginBottom: "0.6rem" }}>📂 Upload Documents</h3>
          <input
            type="file"
            multiple
            onChange={(e) => setFiles([...e.target.files])}
            style={{
              color: "white",
              backgroundColor: "#222",
              border: "1px solid #333",
              borderRadius: "6px",
              padding: "6px",
              marginBottom: "0.6rem",
              marginRight: "1rem",
              width: "50%",
              fontSize: "0.9rem",
            }}
          />
          <button
            onClick={handleUpload}
            disabled={loading}
            style={{
              borderRadius: "5px",
              padding: "6px 12px",
              backgroundColor: "#00c6ff",
              color: "white",
              border: "none",
              cursor: "pointer",
              transition: "0.3s",
              fontSize: "0.9rem",
            }}
            onMouseOver={(e) => (e.target.style.backgroundColor = "#009ad6")}
            onMouseOut={(e) => (e.target.style.backgroundColor = "#00c6ff")}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </section>

        {/* Query Section */}
        <section
          style={{
            background: "#1a1a1a",
            padding: "1rem",
            borderRadius: "8px",
            marginBottom: "1.5rem",
            boxShadow: "0 0 10px rgba(255,255,255,0.05)",
          }}
        >
          <h3 style={{ marginBottom: "0.6rem" }}>💬 Ask a Question</h3>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Ask a question?"
            style={{
              width: "90%",
              padding: "8px",
              borderRadius: "6px",
              border: "1px solid #333",
              backgroundColor: "#222",
              color: "white",
              marginBottom: "0.6rem",
              marginRight: "1rem",
              fontSize: "0.9rem",
              display: "flex",
              flexDirection: "column",
            }}
          />
          <button
            onClick={handleQuery}
            disabled={loading}
            style={{
              borderRadius: "5px",
              padding: "6px 12px",
              backgroundColor: "#ff7a00",
              color: "white",
              border: "none",
              cursor: "pointer",
              transition: "0.3s",
              fontSize: "0.9rem",
            }}
            onMouseOver={(e) => (e.target.style.backgroundColor = "#e06a00")}
            onMouseOut={(e) => (e.target.style.backgroundColor = "#ff7a00")}
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </section>

        {/* Error Message */}
        {error && (
          <p
            style={{
              color: "#ff4d4d",
              backgroundColor: "#2a0000",
              padding: "0.8rem",
              borderRadius: "6px",
              marginBottom: "1rem",
            }}
          >
            ❌ {error}
          </p>
        )}

        {/* Answer Display */}
        {answer && (
          <section
            style={{
              background: "#151515",
              padding: "1rem",
              borderRadius: "8px",
              marginBottom: "1.5rem",
              border: "1px solid #333",
            }}
          >
            <h3 style={{ color: "#00c6ff" }}>🧠 Answer:</h3>
            <div
              style={{
                marginTop: "0.5rem",
                background: "#0f0f0f",
                padding: "0.8rem",
                borderRadius: "6px",
                overflowX: "auto",
              }}
            >
              {typeof answer === "object" ? (
                <pre
                  style={{
                    fontSize: "0.9rem",
                    whiteSpace: "pre-wrap",
                    color: "#eaeaea",
                  }}
                >
                  {JSON.stringify(answer, null, 2)}
                </pre>
              ) : (
                <p style={{ lineHeight: "1.6" }}>{answer}</p>
              )}
            </div>
          </section>
        )}

        {/* Retrieved Chunks */}
        {results.length > 0 && (
          <section
            style={{
              background: "#151515",
              padding: "1rem",
              borderRadius: "8px",
              border: "1px solid #333",
            }}
          >
            <h3 style={{ color: "#00ff95" }}>📄 Retrieved Chunks:</h3>
            <ul style={{ listStyle: "none", padding: 0 }}>
              {results.map((r, i) => (
                <li
                  key={i}
                  style={{
                    marginBottom: "1rem",
                    background: "#1f1f1f",
                    padding: "0.8rem",
                    borderRadius: "6px",
                    borderLeft: "4px solid #00ff95",
                  }}
                >
                  <strong>Source:</strong> {r.source} <br />
                  <strong>Score:</strong> {r.score?.toFixed(4)} <br />
                  <p style={{ marginTop: "0.5rem", lineHeight: "1.6" }}>
                    {r.text}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
