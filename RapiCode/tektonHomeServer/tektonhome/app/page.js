"use client"; // This is a client component
import BoardDescription from '../components/BoardDescription';
import containerStyles from '../components/BoardDescription.module.css';

import React, { useState, useEffect } from 'react';

export default function Home() {
  const [error, setError] = useState('');
  const [board_num, setBoardnum] = useState(null);

  useEffect(() => {
    async function checkBoards() {

        try {
                const responseCheck = await fetch(`http://192.168.0.234:8000/Boards/check`);
                if(!responseCheck.ok){
                  throw new Error('Database Empty, create Board on the Client Board webapp');
                }
                const num = await responseCheck.json();
                setBoardnum(num)

        } catch (err) {
            setError(err.message);

        }
    }
    
    checkBoards();
}, []);

  return (
    <div id='top' className='dark app'>
        <h1 className= 'stickyTop'>Web Control Panel</h1>
        <h2>Boards</h2>
    
    {board_num ? (
      <div>
        <div className={containerStyles.boardTabsContainer}> 
        {Object.values(board_num.num).map((boardId) => (
              <BoardDescription key={boardId} BoardId={boardId} /> 
            ))}
        </div>
    </div>



    ): <p> No Boards available. Add a board client in their Webapp </p>}
    </div>


  );
}
