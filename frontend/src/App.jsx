
import { useState } from "react";
import "./App.css";

// FastAPI backend endpoint
const API_URL = "http://127.0.0.1:8000/api/translate-video";

// Supported file extensions
const AUDIO_EXTENSIONS = [".mp3", ".wav"];
const VIDEO_EXTENSIONS = [".mp4", ".avi"];

export default function App() {
  const [mode, setMode] = useState("video");
  const [file, setFile] = useState(null);
  const [targetLanguage, setTargetLanguage] = useState("English");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  // Select audio or video file
  function handleFileChange(event) {
    const selected = event.target.files?.[0] || null;

    setError("");
    setResult(null);

    if (!selected) {
      setFile(null);
      return;
    }

    const extension = selected.name
      .slice(selected.name.lastIndexOf("."))
      .toLowerCase();

    const allowedExtensions =
      mode === "audio" ? AUDIO_EXTENSIONS : VIDEO_EXTENSIONS;

    if (!allowedExtensions.includes(extension)) {
      setFile(null);
      event.target.value = "";
      setError(
        mode === "audio"
          ? "Please select an MP3 or WAV audio file."
          : "Please select an MP4 or AVI video file."
      );
      return;
    }

    setFile(selected);
  }

  // Change the selected media type
  function handleModeChange(newMode) {
    setMode(newMode);
    setFile(null);
    setResult(null);
    setError("");
  }

  // Upload media and request translation
  async function handleTranslate(event) {
    event.preventDefault();

    if (!file) {
      setError(`Please select an ${mode} file first.`);
      return;
    }

    if (targetLanguage !== "English") {
      setError(
        "The current backend supports English translation only."
      );
      return;
    }

    const formData = new FormData();

    // These fields match the existing backend endpoint.
    formData.append("file", file);

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The backend returned an invalid response. Check the FastAPI terminal."
        );
      }

      if (!response.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : "Translation failed. Please try again.";

        throw new Error(detail);
      }

     setResult({
  ...data,
  spoken_text: data.audio_transcription ?? data.spoken_text ?? "",
  translation: data.translation ?? "",
  visual_context: data.visual_context ?? "",
  fused_prompt: data.fused_prompt ?? "",
  target_language: "English",
});
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
        );
      } else {
        setError(
          err.message || "An unexpected error occurred."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // Support the response field names returned by the backend.
  const spokenText =
    result?.audio_transcription ||
    result?.spoken_text ||
    "";

  const translatedText = result?.translation || "";

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">V</span>
          <span>
            Vox<span className="brand-accent">Bridge</span>
          </span>
        </a>

        <span className="topbar-label">
          MULTIMODAL TRANSLATION LAB
        </span>
      </header>

      <section className="hero">
        <span className="eyebrow">
          AI-POWERED LANGUAGE ACCESS
        </span>

        <h1>
          Every voice.
          <br />
          <span>Every perspective.</span>
        </h1>

        <p>
          Translate spoken language with contextual understanding
          from audio and video.
        </p>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <div>
            <span className="step-label">01 / INPUT</span>
            <h2>Choose your media</h2>
          </div>

          <span className="supported">
            MP4 · MP3 · AVI · WAV
          </span>
        </div>

        <div
          className="mode-switch"
          role="tablist"
          aria-label="Media type"
        >
          <button
            type="button"
            role="tab"
            aria-selected={mode === "audio"}
            className={mode === "audio" ? "mode active" : "mode"}
            onClick={() => handleModeChange("audio")}
          >
            <span className="mode-icon">♫</span>

            <span>
              <strong>Audio</strong>
              <small>Speech and sound</small>
            </span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={mode === "video"}
            className={mode === "video" ? "mode active" : "mode"}
            onClick={() => handleModeChange("video")}
          >
            <span className="mode-icon">▶</span>

            <span>
              <strong>Video</strong>
              <small>Speech and visual context</small>
            </span>
          </button>
        </div>

        <form onSubmit={handleTranslate}>
          <label className="upload-area" htmlFor="media-file">
            <span className="upload-icon">↑</span>

            <strong>
              {file ? file.name : `Upload ${mode}`}
            </strong>

            <span>
              {file
                ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
                : "Click to browse or drag your file here"}
            </span>

            <input
              id="media-file"
              type="file"
              accept={
                mode === "audio"
                  ? ".mp3,.wav"
                  : ".mp4,.avi"
              }
              onChange={handleFileChange}
              disabled={loading}
            />
          </label>

          <div className="language-row">
            <label htmlFor="target-language">
              Translate into
            </label>

            <select
              id="target-language"
              value={targetLanguage}
              onChange={(event) =>
                setTargetLanguage(event.target.value)
              }
              disabled={loading}
            >
              <option value="English">English</option>
            </select>
          </div>

          <p className="integration-note">
            Translation is currently configured for English,
            matching the backend's existing translation settings.
          </p>

          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}

          <button
            className="translate-button"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Processing media…"
              : "Translate media →"}
          </button>
        </form>
      </section>

      {result && (
        <section className="results">
          <div className="section-heading">
            <div>
              <span className="step-label">
                02 / RESULTS
              </span>

              <h2>Translation results</h2>
            </div>

            <span className="status">
              {result.status || "Completed"}
            </span>
          </div>

          <div className="result-card final-result">
            <span className="result-label">
              FINAL TRANSLATION
            </span>

            <p>
              {translatedText || "No translation returned."}
            </p>
          </div>

          <div className="result-grid">
            <div className="result-card">
              <span className="result-label">
                SOURCE LANGUAGE
              </span>

              <p>
                {result.detected_audio_language ||
                  "Not provided by backend"}
              </p>
            </div>

            <div className="result-card">
              <span className="result-label">
                TARGET LANGUAGE
              </span>

              <p>English</p>
            </div>

            <div className="result-card">
              <span className="result-label">
                SPOKEN TEXT
              </span>

              <p>
                {spokenText || "No transcription returned."}
              </p>
            </div>

            <div className="result-card">
              <span className="result-label">
                VISUAL CONTEXT
              </span>

              <p>
                {result.visual_context ||
                  "No visual context returned."}
              </p>
            </div>

            {result.fused_prompt && (
              <div className="result-card full-width">
                <span className="result-label">
                  FUSED CONTEXT
                </span>

                <p>{result.fused_prompt}</p>
              </div>
            )}
          </div>
        </section>
      )}

      <footer>
        <span>VOXBRIDGE</span>
        <span>Multimodal AI · Language Understanding</span>
      </footer>
    </main>
  );
}

