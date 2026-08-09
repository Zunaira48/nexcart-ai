import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { verifyEmail } from "../services/authService";
import "./Auth.css";

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState(token ? "loading" : "error");

  useEffect(() => {
    if (!token) {
      return;
    }
    verifyEmail(token)
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [token]);

  return (
    <div className="container auth-page">
      <div className="auth-card">
        {status === "loading" && <h1>Verifying...</h1>}
        {status === "success" && (
          <>
            <h1>Email Verified!</h1>
            <p>Your account is now fully activated.</p>
            <Link to="/login">Go to login</Link>
          </>
        )}
        {status === "error" && (
          <>
            <h1>Verification Failed</h1>
            <p>This link is invalid or has expired.</p>
            <Link to="/login">Back to login</Link>
          </>
        )}
      </div>
    </div>
  );
}

export default VerifyEmail;