import React, { useState, useEffect } from 'react';
import styles from './BoardDescription.module.css';



function BoardDescription({ BoardId }) {
    const [board_info, setBoardInfo] = useState(null);
    const [error, setError] = useState('');
    const [functionParams, setfuncParams] = useState('');
    const [notification, setNotification] = useState(null);

    useEffect(() => {
        async function fetchBoardDescription() {

            try {
                const response = await fetch(`http://192.168.0.234:8000/Boards/${BoardId}/description`);
                if (!response.ok) {
                    const responseCheck = await fetch(`http://192.168.0.234:8000/Boards/check`);
                    if(!responseCheck.ok){
                      
                      throw new Error('Database Empty, create Board on the Client Board webapp');

                    }else{
                      throw new Error(`Failed to fetch board ${BoardId}`);
                    }
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
        try{
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
        if (response.ok) {

            setNotification(data.message);
            setTimeout(() => setNotification(null), 3000);    
          
        }else{

          setNotification(data.message);
          setTimeout(() => setNotification(null), 3000);
        }
        
        }catch(err){
          setError(err.message);
        }

    }

      const handleDelete = async (event, boardId ,board_ip) => {
        event.preventDefault();
        try{
        const response = await fetch(`http://${board_ip}:8000/deleteBoard/`)
        const data = await response.json();
        if (response.ok) {
          setNotification(data.message);
          setTimeout(() => {
            setNotification(null);
            window.location.reload(); // Reload the page
          }, 100);
        } else {
          setError(data.message);
        }

      }catch(err){
        setError(err.message);

      }};

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
        setNotification(data.message); // Set notification message
        setTimeout(() => setNotification(null), 3000); // Clear notification after 3 seconds
      };

    return (

    <div>

    {notification && (
            <div style={{
              position: 'fixed',
              top: '10px',
              left: '10px',
              backgroundColor: 'lightgreen',
              padding: '10px',
              borderRadius: '5px',
              zIndex: 9999 
            }}>
              {notification}
            </div>
          )}
    {board_info ? (
        
            <div key={board_info.name}>
      
                <div className={styles.boardTab}>
                  <div className={styles.tabHeader}>{board_info.name}</div>

                {Object.entries(board_info.description).map(([moduleName, functions]) => (
              <div className = {styles.tabModule} key={moduleName}>
                    <h3>{moduleName}</h3>
            
                {functions.map(([functionName, type]) => (
                    <div className='tektonLabelContainter' key={functionName}>
                      
                        <label htmlFor= 'name' className='tektonLabel'>{functionName}</label>
                        
                        {type === "Button" ? (
                            
                            <button className='btn btn--plain' onClick={(e) => handleSubmit(e, moduleName, functionName, board_info.client_ip)}>Run</button>
                        ) : (
                            <div>
                                <input className='tektonInput' type="text"  value={functionParams} onChange={(e) => setfuncParams(e.target.value)} placeholder={`Enter ${functionName} parameters`} />
                                <button className='btn btn--plain' onClick={(e) => handleSubmitParams(e, moduleName, functionName, board_info.client_ip)}>Submit</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
                ))}
            <div className={styles.tabFooter}>
              <button className='btn btn--outline' onClick={(e) => handleDelete(e , BoardId ,board_info.client_ip)}> Delete Board </button> 
            </div>
            </div>
            </div>
        )
     : <p>No item details available.</p>}
    {error && <p>Error: {error}</p>}
</div>
);
}


export default BoardDescription;
