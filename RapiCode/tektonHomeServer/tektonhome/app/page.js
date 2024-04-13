"use client"; // This is a client component
import BoardDescription from '../components/BoardDescription';


import { useState } from 'react';

export default function Home() {
  const [RGBvalues, setRGBValues] = useState('');

  const handleSubmit = async (event, buttonValue) => {
    event.preventDefault();
    const response = await fetch('http://192.168.0.234:8000/run-script/', {
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
            <h2>Board Functions</h2>
            <BoardDescription BoardId={1} />
    </div>

  );
}
