import React from "react";
import { useState, useEffect } from "react";
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

  const onReset = () => {
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
          cells.push(
            <td key={`empty-${i}-${j}`} className="w-8 h-8 lg:w-10 lg:h-10 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent mb-2">
          MDP Algorithm Simulator
        </h1>
        <p className="text-gray-600 text-lg">Multi-Disciplinary Project Pathfinding Visualization</p>
      </div>

      <div className="max-w-screen-2xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Panel - Controls */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Robot Position Card */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-800">Robot Position</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">X</label>
                  <input
                    onChange={onChangeRobotX}
                    type="number"
                    placeholder="1"
                    min="1"
                    max="18"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Y</label>
                  <input
                    onChange={onChangeRobotY}
                    type="number"
                    placeholder="1"
                    min="1"
                    max="18"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Direction</label>
                  <select
                    onChange={onRobotDirectionInputChange}
                    value={robotDir}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition-colors"
                  >
                    <option value={ObDirection.NORTH}>↑ Up</option>
                    <option value={ObDirection.SOUTH}>↓ Down</option>
                    <option value={ObDirection.WEST}>← Left</option>
                    <option value={ObDirection.EAST}>→ Right</option>
                  </select>
                </div>
              </div>
              <button 
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105"
                onClick={onClickRobot}
              >
                Set Robot Position
              </button>
            </div>
          </div>

          {/* Add Obstacles Card */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-800">Add Obstacles</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">X</label>
                  <input
                    onChange={onChangeX}
                    type="number"
                    placeholder="0"
                    min="0"
                    max="19"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-gray-900 transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Y</label>
                  <input
                    onChange={onChangeY}
                    type="number"
                    placeholder="0"
                    min="0"
                    max="19"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-gray-900 transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Direction</label>
                  <select
                    onChange={onDirectionInputChange}
                    value={directionInput}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-gray-900 transition-colors"
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
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-2 px-4 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105"
                onClick={onClickObstacle}
              >
                Add Obstacle
              </button>
            </div>
          </div>

          {/* Current Obstacles Card */}
          {obstacles.length > 0 && (
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-shadow duration-300">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-gray-500 to-gray-600 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-800">Current Obstacles</h2>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {obstacles.map((ob) => (
                  <div key={ob.id} className="flex items-center justify-between bg-gray-50 p-2 rounded-lg">
                    <span className="font-mono text-sm text-gray-700">
                      ID: {ob.id} | (X:{ob.x}, Y:{ob.y}) | Dir: {DirectionToString[ob.d]}
                    </span>
                    <button
                      onClick={() => onRemoveObstacle(ob.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-100 rounded-full p-1 transition-colors"
                      aria-label="Remove obstacle"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Path Navigation Card */}
          {simulationRan && simulationData && (
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-shadow duration-300">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-800">Path Navigation</h2>
              </div>
              <div className="space-y-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Step</p>
                  <p className="text-2xl font-bold text-gray-800">{page + 1} / {simulationData.path.length}</p>
                </div>
                <div className="flex justify-between items-center">
                  <button
                    onClick={() => setPage(p => Math.max(0, p - 1))}
                    disabled={page === 0}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(simulationData.path.length - 1, p + 1))}
                    disabled={page >= simulationData.path.length - 1}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
                <div className="pt-2">
                  <p className="text-sm font-medium text-gray-700 mb-1">Commands:</p>
                  <div className="bg-gray-900 text-white font-mono text-xs p-3 rounded-lg h-40 overflow-y-auto">
                    {simulationData.path.map((step, index) => (
                      <p key={index} className={classNames("transition-colors", page === index ? "text-green-400 font-bold" : "text-gray-400")}>
                        {`Step ${index}: X:${step.x}, Y:${step.y}, Dir:${DirectionToString[step.d]}`}
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
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-4 sm:p-6 flex flex-col items-center justify-center overflow-x-auto">
            <table className="border-collapse">
              <tbody>{renderGrid()}</tbody>
            </table>
          </div>

          {/* Action Buttons Card */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={runSimulation}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-teal-500 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-600 hover:to-teal-600 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 disabled:opacity-60 disabled:cursor-wait"
              >
                {loading ? 'Computing...' : 'Run Simulation'}
              </button>
              <button
                onClick={onReset}
                className="w-full bg-gradient-to-r from-yellow-500 to-amber-500 text-white py-3 px-4 rounded-lg font-semibold hover:from-yellow-600 hover:to-amber-600 focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 transition-all duration-200"
              >
                Reset Path
              </button>
              <button
                onClick={onResetAll}
                className="w-full bg-gradient-to-r from-red-500 to-pink-500 text-white py-3 px-4 rounded-lg font-semibold hover:from-red-600 hover:to-pink-600 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200"
              >
                Reset All
              </button>
            </div>
            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-300 text-red-800 rounded-lg text-center">
                <p className="font-medium">Error:</p>
                <p>{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
