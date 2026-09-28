import { useState } from "react";

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
    <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Churn Risk Checker</h1>

      <label>
        Tenure (months):
        <input type="number" name="tenure" value={formData.tenure} onChange={handleChange} />
      </label>
      <br />

      <label>
        Monthly Charges:
        <input type="number" name="MonthlyCharges" value={formData.MonthlyCharges} onChange={handleChange} />
      </label>
      <br />

      <label>
        Total Charges:
        <input type="number" name="TotalCharges" value={formData.TotalCharges} onChange={handleChange} />
      </label>
      <br />

      <label>
        Gender:
        <select name="gender" value={formData.gender} onChange={handleChange}>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </label>
      <br />

      <label>
        Internet Service:
        <select name="InternetService" value={formData.InternetService} onChange={handleChange}>
          <option value="Fiber optic">Fiber optic</option>
          <option value="DSL">DSL</option>
          <option value="No">No</option>
        </select>
      </label>
      <br />

      <label>
        Contract:
        <select name="Contract" value={formData.Contract} onChange={handleChange}>
          <option value="Month-to-month">Month-to-month</option>
          <option value="One year">One year</option>
          <option value="Two year">Two year</option>
        </select>
      </label>
      <br />

      <label>
        Payment Method:
        <select name="PaymentMethod" value={formData.PaymentMethod} onChange={handleChange}>
          <option value="Electronic check">Electronic check</option>
          <option value="Mailed check">Mailed check</option>
          <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
          <option value="Credit card (automatic)">Credit card (automatic)</option>
        </select>
      </label>
      <br />

      {yesNoFields.map((field) => (
        <div key={field}>
          <label>
            {field}:
            <select name={field} value={formData[field]} onChange={handleChange}>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </label>
        </div>
      ))}

      <br />

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Checking..." : "Check Risk"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>
            Churn Probability: {(result.churn_probability * 100).toFixed(1)}%
          </h2>
          <p>
            Decision: {result.churn_prediction === 1 ? "At risk" : "Likely to stay"}
            {" "}(threshold {result.threshold})
          </p>
          <h3>Top Drivers</h3>
          <ul>
            {result.top_drivers.map((d) => (
              <li key={d.feature}>
                {d.feature}: {d.contribution} ({d.direction})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;