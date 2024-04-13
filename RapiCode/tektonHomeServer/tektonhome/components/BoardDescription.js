import React, { useState, useEffect } from 'react';

function BoardDescription({ BoardId }) {
    const [board_info, setBoardInfo] = useState(null);
    const [error, setError] = useState('');
    const [functionParams, setfuncParams] = useState('');

    useEffect(() => {
        async function fetchBoardDescription() {
            try {
                const response = await fetch(`http://192.168.0.234:8000/Boards/${BoardId}/description`);
                if (!response.ok) {
                    throw new Error('Failed to fetch Board description :)');
                }
                const data = await response.json();
                setBoardInfo(data);
                setError('');
            } catch (err) {
                setError(err.message);
                setBoardInfo(null);
            }
        }
        
        fetchBoardDescription();
    }, [BoardId]);

    const handleSubmit = async (event, moduleName, functionName, board_ip) => {
        event.preventDefault();
        const response = await fetch(`http://${board_ip}:8000/run-function/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            moduleName,
            functionName,
            functionParams
            // RGBvalues,
          }),
        });
    
        const data = await response.json();
        alert(data.message);  // Simple way to show the response
      };

      const handleSubmitParams = async (event, moduleName, functionName, board_ip) => {
        event.preventDefault();
        const response = await fetch(`http://${board_ip}:8000/run-function-params/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            moduleName,
            functionName,
            functionParams
          }),
        });
    
        const data = await response.json();
        alert(data.message);  // Simple way to show the response
      };

    return (

    <div>
    {board_info ? (
        
            <div key={board_info.name}>
                <h2>{board_info.name}</h2>

            
                {Object.entries(board_info.description).map(([moduleName, functions]) => (
                    <div key={moduleName}>
                    <h3>{moduleName}</h3>
            
                {functions.map(([functionName, type]) => (
                    <div key={functionName}>
                        <label>{functionName}</label>
                        
                        {type === "Button" ? (
                            
                            <button onClick={(e) => handleSubmit(e, moduleName, functionName, board_info.client_ip)}>Run</button>
                        ) : (
                            <div>
                                <input type="text"  value={functionParams} onChange={(e) => setfuncParams(e.target.value)} placeholder={`Enter ${functionName} parameters`} />
                                <button onClick={(e) => handleSubmitParams(e, moduleName, functionName, board_info.client_ip)}>Submit</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
                ))}

            </div>
        )
     : <p>No item details available.</p>}
    {error && <p>Error: {error}</p>}
</div>
);
}


export default BoardDescription;
