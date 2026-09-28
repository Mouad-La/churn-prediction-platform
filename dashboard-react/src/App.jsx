import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

const initialFormData = {
  tenure: "",
  MonthlyCharges: "",
  TotalCharges: "",
  SeniorCitizen: "No",
  Partner: "No",
  Dependents: "No",
  PhoneService: "Yes",
  MultipleLines: "No",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  PaperlessBilling: "Yes",
  gender: "Male",
  InternetService: "Fiber optic",
  Contract: "Month-to-month",
  PaymentMethod: "Electronic check",
};

const yesNoFields = [
  "SeniorCitizen", "Partner", "Dependents", "PhoneService", "MultipleLines",
  "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
  "StreamingTV", "StreamingMovies", "PaperlessBilling",
];

function App() {
  const [formData, setFormData] = useState(initialFormData);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      ...formData,
      tenure: Number(formData.tenure),
      MonthlyCharges: Number(formData.MonthlyCharges),
      TotalCharges: Number(formData.TotalCharges),
    };

    try {
      const response = await fetch(`${API_URL}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Something went wrong.");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Could not reach the API. Is it running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Churn Risk Checker</h1>
      <p className="subtitle">
        Enter a customer's profile to estimate churn probability and see the
        top contributing factors.
      </p>

      <div className="section">
        <h2>Account</h2>
        <div className="grid-2">
          <div className="field">
            <label>Tenure (months)</label>
            <input type="number" name="tenure" min="0" max="100" value={formData.tenure} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Monthly Charges</label>
            <input type="number" name="MonthlyCharges" min="0" value={formData.MonthlyCharges} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Total Charges</label>
            <input type="number" name="TotalCharges" min="0" value={formData.TotalCharges} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Gender</label>
            <select name="gender" value={formData.gender} onChange={handleChange}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>
      </div>

      <div className="section">
        <h2>Service</h2>
        <div className="field">
          <label>Internet Service</label>
          <select name="InternetService" value={formData.InternetService} onChange={handleChange}>
            <option value="Fiber optic">Fiber optic</option>
            <option value="DSL">DSL</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="field">
          <label>Contract</label>
          <select name="Contract" value={formData.Contract} onChange={handleChange}>
            <option value="Month-to-month">Month-to-month</option>
            <option value="One year">One year</option>
            <option value="Two year">Two year</option>
          </select>
        </div>
        <div className="field">
          <label>Payment Method</label>
          <select name="PaymentMethod" value={formData.PaymentMethod} onChange={handleChange}>
            <option value="Electronic check">Electronic check</option>
            <option value="Mailed check">Mailed check</option>
            <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
            <option value="Credit card (automatic)">Credit card (automatic)</option>
          </select>
        </div>
      </div>

      <div className="section">
        <h2>Add-ons</h2>
        <div className="grid-2">
          {yesNoFields.map((field) => (
            <div className="field" key={field}>
              <label>{field}</label>
              <select name={field} value={formData[field]} onChange={handleChange}>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          ))}
        </div>
      </div>

      <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Checking..." : "Check Risk"}
      </button>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className={`result ${result.churn_prediction === 1 ? "at-risk" : "likely-stay"}`}>
          <p className="probability">
            {(result.churn_probability * 100).toFixed(1)}% churn probability
          </p>
          <p className="decision">
            {result.churn_prediction === 1 ? "At risk" : "Likely to stay"}
            {" "}&middot; threshold {result.threshold}
          </p>
          <ul>
            {result.top_drivers.map((d) => (
              <li key={d.feature}>
                {d.feature}: {d.contribution > 0 ? "+" : ""}{d.contribution} ({d.direction})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;