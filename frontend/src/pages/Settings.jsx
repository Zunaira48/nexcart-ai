import { useTheme } from "../context/useTheme";
import "./Settings.css";

function Settings() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="container settings-page">
      <h1 className="admin-title">Settings</h1>

      <section className="admin-section">
        <h2>Appearance</h2>
        <p className="settings-description">Choose how NexCart AI looks on your device.</p>

        <div className="theme-options">
          <button
            className={`theme-option ${theme === "dark" ? "theme-option-active" : ""}`}
            onClick={() => setTheme("dark")}
          >
            🌙 Dark
          </button>
          <button
            className={`theme-option ${theme === "light" ? "theme-option-active" : ""}`}
            onClick={() => setTheme("light")}
          >
            ☀️ Light
          </button>
        </div>
      </section>
    </div>
  );
}

export default Settings;