import React, { useState } from 'react';
import './App.css';

function App() {
  const [submitted, setSubmitted] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [csvData, setCsvData] = useState([]);
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);  // Get the selected file
  };

  const handleTranscriptionChange = (e) => {
    setTranscription(e.target.value);  // Get the transcription query
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setResponseMessage('Please select a file');
      return;
    }

    if (!transcription) {
      setResponseMessage('Please enter a transcription query');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);  // Append the file to FormData
    formData.append('transcription', transcription);  // Append the transcription to FormData

    const response = await fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    console.log(data);

    setSubmitted(true);
    setResponseMessage(data.message);

    // Transform the data for rendering
    if (data.data) {
      const headers = Object.keys(data.data[0] || {});
      const rows = data.data.map(row => headers.map(header => row[header]));
      setCsvData([headers, ...rows]);
    } else {
      setCsvData([]);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Select CSV file:</label>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
          />
        </div>
        <div>
          <label>Enter transcription query:</label>
          <input
            type="text"
            value={transcription}
            onChange={handleTranscriptionChange}
          />
        </div>
        <button type="submit">Submit</button>
      </form>

      {submitted && <p>{responseMessage}</p>}  {/* Conditional rendering of the message */}
      
      {csvData.length > 0 && (
        <div className="table-container">
          <h3>Processed Data:</h3>
          <table>
            <thead>
              <tr>
                {csvData[0].map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {csvData.slice(1).map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
