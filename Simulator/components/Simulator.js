import React from "react";
import { useState, useEffect, useRef } from "react";
import QueryAPI from "./QueryAPI";

const Direction = {
  NORTH: 0,
  EAST: 2,
  SOUTH: 4,
  WEST: 6,
  SKIP: 8,
};

const ObDirection = {
  NORTH: 0,
  EAST: 2,
  SOUTH: 4,
  WEST: 6,
  SKIP: 8,
};

const DirectionToString = {
  0: "Up",
  2: "Right",
  4: "Down",
  6: "Left",
  8: "None",
};

const transformCoord = (x, y) => {
  // Change the coordinate system from (0, 0) at top left to (0, 0) at bottom left
  return { x: 19 - y, y: x };
};

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function Simulator() {
  const [robotState, setRobotState] = useState({
    x: 1,
    y: 1,
    d: Direction.NORTH,
    s: -1,
  });
  const [robotX, setRobotX] = useState(1);
  const [robotY, setRobotY] = useState(1);
  const [robotDir, setRobotDir] = useState(0);
  const [obstacles, setObstacles] = useState([]);
  const [obXInput, setObXInput] = useState(0);
  const [obYInput, setObYInput] = useState(0);
  const [directionInput, setDirectionInput] = useState(ObDirection.NORTH);
  const [isComputing, setIsComputing] = useState(false);
  const [path, setPath] = useState([]);
  const [commands, setCommands] = useState([]);
  const [page, setPage] = useState(0);
  const [simulationRan, setSimulationRan] = useState(false);
  const [simulationData, setSimulationData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // New state for automated simulation
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(500); // milliseconds between steps
  const [showPath, setShowPath] = useState(false);
  const intervalRef = useRef(null);

  const generateNewID = () => {
    while (true) {
      let new_id = Math.floor(Math.random() * 10) + 1; // just try to generate an id;
      let ok = true;
      for (const ob of obstacles) {
        if (ob.id === new_id) {
          ok = false;
          break;
        }
      }
      if (ok) {
        return new_id;
      }
    }
  };

  const generateRobotCells = () => {
    const robotCells = [];
    let markerX = 0;
    let markerY = 0;

    if (Number(robotState.d) === Direction.NORTH) {
      markerY++;
    } else if (Number(robotState.d) === Direction.EAST) {
      markerX++;
    } else if (Number(robotState.d) === Direction.SOUTH) {
      markerY--;
    } else if (Number(robotState.d) === Direction.WEST) {
      markerX--;
    }

    // Go from i = -1 to i = 1
    for (let i = -1; i < 2; i++) {
      // Go from j = -1 to j = 1
      for (let j = -1; j < 2; j++) {
        // Transform the coordinates to our coordinate system where (0, 0) is at the bottom left
        const coord = transformCoord(robotState.x + i, robotState.y + j);
        // If the cell is the marker cell, add the robot state to the cell
        if (markerX === i && markerY === j) {
          robotCells.push({
            x: coord.x,
            y: coord.y,
            d: robotState.d,
            s: robotState.s,
          });
        } else {
          robotCells.push({
            x: coord.x,
            y: coord.y,
            d: null,
            s: -1,
          });
        }
      }
    }

    return robotCells;
  };

  const onChangeX = (event) => {
    // If the input is an integer and is in the range [0, 19], set ObXInput to the input
    if (Number.isInteger(Number(event.target.value))) {
      const nb = Number(event.target.value);
      if (0 <= nb && nb < 20) {
        setObXInput(nb);
        return;
      }
    }
    // If the input is not an integer or is not in the range [0, 19], set the input to 0
    setObXInput(0);
  };

  const onChangeY = (event) => {
    // If the input is an integer and is in the range [0, 19], set ObYInput to the input
    if (Number.isInteger(Number(event.target.value))) {
      const nb = Number(event.target.value);
      if (0 <= nb && nb <= 19) {
        setObYInput(nb);
        return;
      }
    }
    // If the input is not an integer or is not in the range [0, 19], set the input to 0
    setObYInput(0);
  };

  const onChangeRobotX = (event) => {
    // If the input is an integer and is in the range [1, 18], set RobotX to the input
    if (Number.isInteger(Number(event.target.value))) {
      const nb = Number(event.target.value);
      if (1 <= nb && nb < 19) {
        setRobotX(nb);
        return;
      }
    }
    // If the input is not an integer or is not in the range [1, 18], set the input to 1
    setRobotX(1);
  };

  const onChangeRobotY = (event) => {
    // If the input is an integer and is in the range [1, 18], set RobotY to the input
    if (Number.isInteger(Number(event.target.value))) {
      const nb = Number(event.target.value);
      if (1 <= nb && nb < 19) {
        setRobotY(nb);
        return;
      }
    }
    // If the input is not an integer or is not in the range [1, 18], set the input to 1
    setRobotY(1);
  };

  const onClickObstacle = () => {
    // If the input is not valid, return
    if (!obXInput && !obYInput) return;
    // Create a new array of obstacles
    const newObstacles = [...obstacles];
    // Add the new obstacle to the array
    newObstacles.push({
      x: obXInput,
      y: obYInput,
      d: directionInput,
      id: generateNewID(),
    });
    // Set the obstacles to the new array
    setObstacles(newObstacles);
  };

  const onClickRobot = () => {
    // Set the robot state to the input

    setRobotState({ x: robotX, y: robotY, d: robotDir, s: -1 });
  };

  const onDirectionInputChange = (event) => {
    // Set the direction input to the input
    setDirectionInput(Number(event.target.value));
  };

  const onRobotDirectionInputChange = (event) => {
    // Set the robot direction to the input
    setRobotDir(event.target.value);
  };

  const onRemoveObstacle = (idToRemove) => {
    if (path.length > 0 || isComputing) return;
    // Filter out the obstacle with the matching ID
    const newObstacles = obstacles.filter(ob => ob.id !== idToRemove);
    setObstacles(newObstacles);
  };

  const runSimulation = async () => {
    if (obstacles.length === 0) {
      setError("Please add at least one obstacle to run the simulation.");
      return;
    }
    setLoading(true);
    setError(null);
    setSimulationRan(false);
    setSimulationData(null);

    const config = {
      obstacles: obstacles,
      robot_x: robotX,
      robot_y: robotY,
      robot_dir: robotDir,
    };

    try {
      const response = await QueryAPI.runSimulation(config);
      console.log('✅ Simulation response:', response);

      // Safely access the path data from the response.
      // The backend response contains the 'path' directly.
      const path = response?.path;

      if (path && Array.isArray(path)) {
        // The response also contains commands, let's extract them.
        const commands = response?.commands || [];
        setSimulationData({ path, commands });
        setSimulationRan(true);
        setError(null);
      } else {
        // Handle cases where the path is missing or not an array
        console.error('❌ Invalid or missing path in simulation response:', response);
        setError('Simulation successful, but received invalid path data from the backend.');
        setSimulationData(null);
      }
    } catch (e) {
      console.error('❌ Simulation failed:', e);
      setError(e.message || "An unknown error occurred during simulation.");
      setSimulationData(null);
    } finally {
      setLoading(false);
    }
  };


  const compute = () => {
    // Set computing to true, act like a lock
    setIsComputing(true);
    // Call the query function from the API
    QueryAPI.query(obstacles, robotX, robotY, robotDir, (data, err) => {
      if (data) {
        // If the data is valid, set the path
        setPath(data.data.path);
        // Set the commands
        const commands = [];
        for (let x of data.data.commands) {
          // If the command is a snapshot, skip it
          if (x.startsWith("SNAP")) {
            continue;
          }
          commands.push(x);
        }
        setCommands(commands);
      }
      // Set computing to false, release the lock
      setIsComputing(false);
    });
  };

  const onResetAll = () => {
    // Stop any playing simulation
    stopAutoPlay();
    // Reset all the states
    setRobotX(1);
    setRobotDir(0);
    setRobotY(1);
    setRobotState({ x: 1, y: 1, d: Direction.NORTH, s: -1 });
    setPath([]);
    setCommands([]);
    setPage(0);
    setObstacles([]);
  };

  // New functions for automated simulation
  const startAutoPlay = () => {
    if (!simulationData || !simulationData.path || simulationData.path.length === 0) return;
    
    setIsPlaying(true);
    intervalRef.current = setInterval(() => {
      setPage(prevPage => {
        const nextPage = prevPage + 1;
        if (nextPage >= simulationData.path.length) {
          // Reached the end, stop playing
          setIsPlaying(false);
          clearInterval(intervalRef.current);
          return prevPage;
        }
        return nextPage;
      });
    }, playbackSpeed);
  };

  const stopAutoPlay = () => {
    setIsPlaying(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const toggleAutoPlay = () => {
    if (isPlaying) {
      stopAutoPlay();
    } else {
      startAutoPlay();
    }
  };

  const resetToStart = () => {
    stopAutoPlay();
    setPage(0);
  };

  const jumpToEnd = () => {
    stopAutoPlay();
    if (simulationData && simulationData.path) {
      setPage(simulationData.path.length - 1);
    }
  };

  const onReset = () => {
    // Stop any playing simulation
    stopAutoPlay();
    // Reset all the states
    setRobotX(1);
    setRobotDir(0);
    setRobotY(1);
    setRobotState({ x: 1, y: 1, d: Direction.NORTH, s: -1 });
    setPath([]);
    setCommands([]);
    setPage(0);
    setSimulationRan(false);
    setSimulationData(null);
    setError(null);
  };

  const renderGrid = () => {
    // Initialize the empty rows array
    const rows = [];

    // Generate robot cells
    const robotCells = generateRobotCells();

    // Generate the grid
    for (let i = 0; i < 20; i++) {
      const cells = [
        // Header cells
        <td key={`header-${i}`} className="w-8 h-8 lg:w-10 lg:h-10 text-center bg-gray-100 border border-gray-300">
          <span className="text-gray-700 font-semibold text-xs lg:text-sm">
            {19 - i}
          </span>
        </td>,
      ];

      for (let j = 0; j < 20; j++) {
        let foundOb = null;
        let foundRobotCell = null;

        for (const ob of obstacles) {
          const transformed = transformCoord(ob.x, ob.y);
          if (transformed.x === i && transformed.y === j) {
            foundOb = ob;
            break;
          }
        }

        if (!foundOb) {
          for (const cell of robotCells) {
            if (cell.x === i && cell.y === j) {
              foundRobotCell = cell;
              break;
            }
          }
        }

        if (foundOb) {
          let obstacleClass = "w-8 h-8 lg:w-10 lg:h-10 bg-red-500 border-2 relative";
          let directionMarker = null;
          
          if (foundOb.d === Direction.WEST) {
            obstacleClass += " border-l-4 border-l-red-800";
            directionMarker = <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-red-800"></div>;
          } else if (foundOb.d === Direction.EAST) {
            obstacleClass += " border-r-4 border-r-red-800";
            directionMarker = <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-red-800"></div>;
          } else if (foundOb.d === Direction.NORTH) {
            obstacleClass += " border-t-4 border-t-red-800";
            directionMarker = <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-6 h-1 bg-red-800"></div>;
          } else if (foundOb.d === Direction.SOUTH) {
            obstacleClass += " border-b-4 border-b-red-800";
            directionMarker = <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-6 h-1 bg-red-800"></div>;
          } else if (foundOb.d === Direction.SKIP) {
            obstacleClass += " border-gray-400";
          }
          
          cells.push(
            <td key={`obstacle-${i}-${j}`} className={obstacleClass}>
              {directionMarker}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-red-800 rounded-full"></div>
              </div>
            </td>
          );
        } else if (foundRobotCell) {
          let robotClass = "w-8 h-8 lg:w-10 lg:h-10 border-2 relative";
          let robotContent = null;
          
          if (foundRobotCell.d !== null) {
            if (foundRobotCell.s !== -1) {
              // Robot center with image detection
              robotClass += " bg-blue-600 border-blue-800";
              robotContent = (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-3 h-3 bg-white rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-xs font-bold">{foundRobotCell.s}</span>
                  </div>
                </div>
              );
            } else {
              // Robot center
              robotClass += " bg-blue-500 border-blue-700";
              let directionArrow = null;
              
              if (foundRobotCell.d === Direction.NORTH) {
                directionArrow = <div className="absolute top-1 left-1/2 transform -translate-x-1/2 text-white text-xs">▲</div>;
              } else if (foundRobotCell.d === Direction.EAST) {
                directionArrow = <div className="absolute right-1 top-1/2 transform -translate-y-1/2 text-white text-xs">▶</div>;
              } else if (foundRobotCell.d === Direction.SOUTH) {
                directionArrow = <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 text-white text-xs">▼</div>;
              } else if (foundRobotCell.d === Direction.WEST) {
                directionArrow = <div className="absolute left-1 top-1/2 transform -translate-y-1/2 text-white text-xs">◀</div>;
              }
              
              robotContent = (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                  {directionArrow}
                </div>
              );
            }
          } else {
            // Robot body
            robotClass += " bg-blue-300 border-blue-400";
            robotContent = <div className="absolute inset-1 bg-blue-400 rounded-sm"></div>;
          }
          
          cells.push(
            <td key={`robot-${i}-${j}`} className={robotClass}>
              {robotContent}
            </td>
          );
        } else {
          // Check if this cell is part of the path
          let isInPath = false;
          let pathIndex = -1;
          let isVisited = false;
          let isCurrent = false;
          let pathStep = null;
          
          if (showPath && simulationData && simulationData.path) {
            for (let pathIdx = 0; pathIdx < simulationData.path.length; pathIdx++) {
              const step = simulationData.path[pathIdx];
              const pathCoord = transformCoord(step.x, step.y);
              if (pathCoord.x === i && pathCoord.y === j) {
                isInPath = true;
                pathIndex = pathIdx;
                isVisited = pathIdx < page;
                isCurrent = pathIdx === page;
                pathStep = step;
                break;
              }
            }
          }
          
          let cellClass = "w-8 h-8 lg:w-10 lg:h-10 border border-gray-300 transition-all duration-300 relative";
          let cellContent = null;
          
          if (isInPath) {
            if (isCurrent) {
              // Current position in path - bright yellow/gold
              cellClass += " bg-gradient-to-br from-yellow-200 to-amber-300 border-amber-400 shadow-lg transform scale-105";
              cellContent = (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-3 h-3 bg-amber-500 rounded-full animate-pulse shadow-md border-2 border-white"></div>
                  <div className="absolute text-xs font-bold text-amber-800 mt-6">{pathIndex + 1}</div>
                </div>
              );
            } else if (isVisited) {
              // Visited path - green
              cellClass += " bg-gradient-to-br from-green-100 to-emerald-200 hover:from-green-200 hover:to-emerald-300 border-green-300";
              let directionArrow = null;
              if (pathStep) {
                const arrowClass = "absolute text-green-700 text-xs font-bold";
                if (pathStep.d === Direction.NORTH) {
                  directionArrow = <div className={`${arrowClass} top-0.5 left-1/2 transform -translate-x-1/2`}>↑</div>;
                } else if (pathStep.d === Direction.EAST) {
                  directionArrow = <div className={`${arrowClass} right-0.5 top-1/2 transform -translate-y-1/2`}>→</div>;
                } else if (pathStep.d === Direction.SOUTH) {
                  directionArrow = <div className={`${arrowClass} bottom-0.5 left-1/2 transform -translate-x-1/2`}>↓</div>;
                } else if (pathStep.d === Direction.WEST) {
                  directionArrow = <div className={`${arrowClass} left-0.5 top-1/2 transform -translate-y-1/2`}>←</div>;
                }
              }
              cellContent = (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-2 h-2 bg-green-600 rounded-full shadow-sm"></div>
                  {directionArrow}
                  <div className="absolute text-xs text-green-700 font-medium mt-5" style={{ fontSize: '8px' }}>{pathIndex + 1}</div>
                </div>
              );
            } else {
              // Future path - light blue
              cellClass += " bg-gradient-to-br from-blue-50 to-sky-100 hover:from-blue-100 hover:to-sky-200 border-blue-200";
              cellContent = (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full opacity-70"></div>
                  <div className="absolute text-xs text-blue-600 font-medium mt-4" style={{ fontSize: '8px' }}>{pathIndex + 1}</div>
                </div>
              );
            }
          } else {
            cellClass += " bg-white hover:bg-gray-50";
          }
          
          cells.push(
            <td key={`empty-${i}-${j}`} className={cellClass}>
              {cellContent}
            </td>
          );
        }
      }

      rows.push(<tr key={19 - i}>{cells}</tr>);
    }

    const yAxis = [<td key="corner" className="w-8 h-8 lg:w-10 lg:h-10 bg-gray-200 border border-gray-300"></td>];
    for (let i = 0; i < 20; i++) {
      yAxis.push(
        <td key={`y-axis-${i}`} className="w-8 h-8 lg:w-10 lg:h-10 text-center bg-gray-100 border border-gray-300">
          <span className="text-gray-700 font-semibold text-xs lg:text-sm">
            {i}
          </span>
        </td>
      );
    }
    rows.push(<tr key="y-axis">{yAxis}</tr>);
    return rows;
  };

  useEffect(() => {
    // When the page (current step) or the simulation data changes,
    // update the robot's state to reflect its position in the path.
    if (simulationData && simulationData.path && page < simulationData.path.length) {
      setRobotState(simulationData.path[page]);
    }
  }, [page, simulationData]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-black bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mb-3 tracking-tight">
          MDP Algorithm Simulator
        </h1>
        <p className="text-slate-300 text-xl font-medium">Multi-Disciplinary Project Pathfinding Visualization</p>
        <div className="w-24 h-1 bg-gradient-to-r from-emerald-400 to-blue-400 mx-auto mt-4 rounded-full"></div>
      </div>

      <div className="max-w-screen-2xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Panel - Controls */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Robot Position Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center mr-3 shadow-lg">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white">Robot Position</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">X</label>
                  <input
                    onChange={onChangeRobotX}
                    type="number"
                    placeholder="1"
                    min="1"
                    max="18"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 text-white placeholder-slate-400 transition-all duration-200 backdrop-blur-sm"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">Y</label>
                  <input
                    onChange={onChangeRobotY}
                    type="number"
                    placeholder="1"
                    min="1"
                    max="18"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 text-white placeholder-slate-400 transition-all duration-200 backdrop-blur-sm"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">Direction</label>
                  <select
                    onChange={onRobotDirectionInputChange}
                    value={robotDir}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 text-white transition-all duration-200 backdrop-blur-sm"
                  >
                    <option value={ObDirection.NORTH}>↑ Up</option>
                    <option value={ObDirection.SOUTH}>↓ Down</option>
                    <option value={ObDirection.WEST}>← Left</option>
                    <option value={ObDirection.EAST}>→ Right</option>
                  </select>
                </div>
              </div>
              <button 
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-emerald-400 hover:to-teal-400 focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-emerald-500/25"
                onClick={onClickRobot}
              >
                Set Robot Position
              </button>
            </div>
          </div>

          {/* Add Obstacles Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-rose-500 to-pink-500 rounded-xl flex items-center justify-center mr-3 shadow-lg">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white">Add Obstacles</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">X</label>
                  <input
                    onChange={onChangeX}
                    type="number"
                    placeholder="0"
                    min="0"
                    max="19"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-rose-400 focus:border-rose-400 text-white placeholder-slate-400 transition-all duration-200 backdrop-blur-sm"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">Y</label>
                  <input
                    onChange={onChangeY}
                    type="number"
                    placeholder="0"
                    min="0"
                    max="19"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-rose-400 focus:border-rose-400 text-white placeholder-slate-400 transition-all duration-200 backdrop-blur-sm"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-200">Direction</label>
                  <select
                    onChange={onDirectionInputChange}
                    value={directionInput}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-rose-400 focus:border-rose-400 text-white transition-all duration-200 backdrop-blur-sm"
                  >
                    <option value={ObDirection.NORTH}>↑ North</option>
                    <option value={ObDirection.SOUTH}>↓ South</option>
                    <option value={ObDirection.WEST}>← West</option>
                    <option value={ObDirection.EAST}>→ East</option>
                    <option value={ObDirection.SKIP}>- None</option>
                  </select>
                </div>
              </div>
              <button 
                className="w-full bg-gradient-to-r from-rose-500 to-pink-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-rose-400 hover:to-pink-400 focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-rose-500/25"
                onClick={onClickObstacle}
              >
                Add Obstacle
              </button>
            </div>
          </div>

          {/* Current Obstacles Card */}
          {obstacles.length > 0 && (
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl flex items-center justify-center mr-3 shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </div>
                <h2 className="text-xl font-bold text-white">Current Obstacles</h2>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {obstacles.map((ob) => (
                  <div key={ob.id} className="flex items-center justify-between bg-white/5 p-3 rounded-xl border border-white/10">
                    <span className="font-mono text-sm text-slate-200">
                      ID: {ob.id} | (X:{ob.x}, Y:{ob.y}) | Dir: {DirectionToString[ob.d]}
                    </span>
                    <button
                      onClick={() => onRemoveObstacle(ob.id)}
                      className="text-rose-400 hover:text-rose-300 hover:bg-rose-400/10 rounded-lg p-2 transition-colors"
                      aria-label="Remove obstacle"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Path Navigation & Automation Card */}
          {simulationRan && simulationData && (
            <div className="bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center mr-3 shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M15 14h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <h2 className="text-xl font-bold text-white">Path Simulation</h2>
              </div>
              
              <div className="space-y-4">
                {/* Progress Display */}
                <div className="text-center">
                  <p className="text-sm text-slate-300">Step</p>
                  <p className="text-3xl font-black text-white">{page + 1} / {simulationData.path.length}</p>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-white/20 rounded-full h-3 mt-3">
                    <div 
                      className="bg-gradient-to-r from-cyan-400 to-blue-500 h-3 rounded-full transition-all duration-300 ease-out shadow-lg"
                      style={{ width: `${((page + 1) / simulationData.path.length) * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Automation Controls */}
                <div className="bg-white/5 p-5 rounded-2xl border border-white/10 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-white">Automation Controls</h3>
                    <div className="flex items-center space-x-3">
                      <label className="text-sm text-slate-300">Show Path:</label>
                      <input
                        type="checkbox"
                        checked={showPath}
                        onChange={(e) => setShowPath(e.target.checked)}
                        className="w-5 h-5 text-cyan-500 bg-white/10 border-white/20 rounded focus:ring-cyan-400 focus:ring-2"
                      />
                    </div>
                  </div>
                  
                  {/* Speed Control */}
                  <div className="space-y-3">
                    <label className="block text-sm font-medium text-slate-200">
                      Speed: {playbackSpeed}ms per step
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="2000"
                      step="100"
                      value={playbackSpeed}
                      onChange={(e) => setPlaybackSpeed(parseInt(e.target.value))}
                      className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Fast (100ms)</span>
                      <span>Slow (2000ms)</span>
                    </div>
                  </div>

                  {/* Play/Pause Controls */}
                  <div className="flex justify-center space-x-2">
                    <button
                      onClick={resetToStart}
                      disabled={isPlaying}
                      className="px-4 py-3 bg-white/10 text-slate-200 rounded-xl font-medium hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm border border-white/20 hover:border-white/40"
                    >
                      ⏮ Start
                    </button>
                    <button
                      onClick={() => setPage(p => Math.max(0, p - 1))}
                      disabled={page === 0 || isPlaying}
                      className="px-4 py-3 bg-white/10 text-slate-200 rounded-xl font-medium hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm border border-white/20 hover:border-white/40"
                    >
                      ⏪ Prev
                    </button>
                    <button
                      onClick={toggleAutoPlay}
                      className={`px-5 py-3 rounded-xl font-semibold transition-all text-sm shadow-lg ${
                        isPlaying 
                          ? 'bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-400 hover:to-pink-400 text-white border border-red-400' 
                          : 'bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-white border border-emerald-400'
                      }`}
                    >
                      {isPlaying ? '⏸ Pause' : '▶ Play'}
                    </button>
                    <button
                      onClick={() => setPage(p => Math.min(simulationData.path.length - 1, p + 1))}
                      disabled={page >= simulationData.path.length - 1 || isPlaying}
                      className="px-4 py-3 bg-white/10 text-slate-200 rounded-xl font-medium hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm border border-white/20 hover:border-white/40"
                    >
                      ⏩ Next
                    </button>
                    <button
                      onClick={jumpToEnd}
                      disabled={isPlaying}
                      className="px-4 py-3 bg-white/10 text-slate-200 rounded-xl font-medium hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm border border-white/20 hover:border-white/40"
                    >
                      ⏭ End
                    </button>
                  </div>
                </div>

                {/* Statistics */}
                <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-5 rounded-2xl border border-purple-400/30">
                  <h3 className="text-sm font-bold text-white mb-4">Simulation Statistics</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                      <div className="text-slate-300">Total Steps:</div>
                      <div className="font-black text-cyan-400 text-lg">{simulationData.path.length}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-slate-300">Progress:</div>
                      <div className="font-black text-purple-400 text-lg">
                        {Math.round(((page + 1) / simulationData.path.length) * 100)}%
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-slate-300">Obstacles:</div>
                      <div className="font-black text-rose-400 text-lg">{obstacles.length}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-slate-300">Current Position:</div>
                      <div className="font-black text-emerald-400 text-lg">
                        ({robotState.x}, {robotState.y})
                      </div>
                    </div>
                  </div>
                </div>

                {/* Path Details */}
                <div className="pt-2">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-semibold text-white">Path Details:</p>
                    <div className="text-xs">
                      {isPlaying && <span className="animate-pulse text-emerald-400 font-medium">● Playing</span>}
                      {!isPlaying && page < simulationData.path.length - 1 && <span className="text-amber-400 font-medium">⏸ Paused</span>}
                      {!isPlaying && page === simulationData.path.length - 1 && <span className="text-cyan-400 font-medium">✓ Complete</span>}
                    </div>
                  </div>
                  <div className="bg-slate-900/80 backdrop-blur-sm text-white font-mono text-xs p-4 rounded-xl h-32 overflow-y-auto border border-slate-700/50">
                    {simulationData.path.map((step, index) => (
                      <p key={index} className={classNames(
                        "transition-colors leading-relaxed py-0.5",
                        page === index ? "text-cyan-300 font-bold bg-cyan-900/30 px-2 rounded" : 
                        index < page ? "text-emerald-300" : "text-slate-400"
                      )}>
                        {`Step ${String(index + 1).padStart(2, '0')}: (${step.x}, ${step.y}) → ${DirectionToString[step.d]}`}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Right Panel - Grid and Actions */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Grid Card */}
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-4 sm:p-8 flex flex-col items-center justify-center overflow-x-auto">
            <div className="w-full max-w-fit">
              <table className="border-collapse mx-auto">
                <tbody>{renderGrid()}</tbody>
              </table>
            </div>
            
            {/* Legend */}
            {showPath && simulationData && (
              <div className="mt-8 p-6 bg-white/10 rounded-2xl w-full max-w-2xl border border-white/20 backdrop-blur-sm">
                <h3 className="text-sm font-bold text-white mb-4 text-center">Legend</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-blue-500 border-2 border-blue-700 rounded-lg flex items-center justify-center shadow-sm">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <span className="text-slate-200 font-medium">Robot</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-red-500 border-2 border-red-800 rounded-lg flex items-center justify-center shadow-sm">
                      <div className="w-2 h-2 bg-red-800 rounded-full"></div>
                    </div>
                    <span className="text-slate-200 font-medium">Obstacle</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-gradient-to-br from-green-100 to-emerald-200 border border-green-300 rounded-lg flex items-center justify-center shadow-sm">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                    </div>
                    <span className="text-slate-200 font-medium">Visited Path</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-gradient-to-br from-yellow-200 to-amber-300 border border-amber-400 rounded-lg flex items-center justify-center shadow-sm">
                      <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
                    </div>
                    <span className="text-slate-200 font-medium">Current Step</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-gradient-to-br from-blue-50 to-sky-100 border border-blue-200 rounded-lg flex items-center justify-center shadow-sm">
                      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-200 font-medium">Future Path</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 bg-white/10 border border-white/30 rounded-lg shadow-sm"></div>
                    <span className="text-slate-200 font-medium">Empty Space</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-emerald-400 font-bold text-lg">↑→↓←</span>
                    <span className="text-slate-200 font-medium">Direction</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-cyan-400 font-mono text-xs bg-white/10 px-2 py-1 rounded-lg">1,2,3</span>
                    <span className="text-slate-200 font-medium">Step Number</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={runSimulation}
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white py-3 px-4 rounded-xl font-semibold focus:ring-2 focus:ring-emerald-500/50 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 disabled:opacity-60 disabled:cursor-wait shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
              >
                {loading ? 'Computing...' : 'Run Simulation'}
              </button>
              <button
                onClick={onReset}
                className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white py-3 px-4 rounded-xl font-semibold focus:ring-2 focus:ring-amber-500/50 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
              >
                Reset Path
              </button>
              <button
                onClick={onResetAll}
                className="w-full bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white py-3 px-4 rounded-xl font-semibold focus:ring-2 focus:ring-rose-500/50 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
              >
                Reset All
              </button>
            </div>
            {error && (
              <div className="mt-4 p-4 bg-red-500/20 backdrop-blur-sm border border-red-500/30 text-red-100 rounded-xl text-center shadow-lg">
                <p className="font-medium text-red-200">Error:</p>
                <p className="text-red-100">{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
