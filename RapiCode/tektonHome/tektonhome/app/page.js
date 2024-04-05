"use client"; // This is a client component

import { useState } from 'react';

export default function Home() {
  const [RGBvalues, setRGBValues] = useState('');

  const handleSubmit = async (event, buttonValue) => {
    event.preventDefault();
    const response = await fetch('http://192.168.0.234:8001/run-script/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        button: buttonValue,
        RGBvalues,
      }),
    });

    const data = await response.json();
    alert(data.message);  // Simple way to show the response
  };

  return (
    <div>
      <h1>Web Control Panel</h1>
      <form>
        <button onClick={(e) => handleSubmit(e, 'turnOn')}>Turn On</button>
        <button onClick={(e) => handleSubmit(e, 'turnOff')}>Turn Off</button>
        <input type="text" value={RGBvalues} onChange={(e) => setRGBValues(e.target.value)} placeholder="Enter RGB values" />
        <button onClick={(e) => handleSubmit(e, 'changeColor')}>Change Color</button>
      </form>
    </div>
  );
}
