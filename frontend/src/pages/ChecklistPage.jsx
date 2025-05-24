import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

const ChecklistPage = () => {
  const [businessId, setBusinessId] = useState('');
  const [task, setTask] = useState('');
  const [tasks, setTasks] = useState([]);
  const [result, setResult] = useState(null);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`/api/checklist?business_id=${businessId}`);
      setTasks(response.data);
    } catch (error) {
      setTasks([]);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/checklist', { business_id: businessId, task });
      setResult(response.data);
      fetchTasks();
      setTask('');
    } catch (error) {
      setResult({ error: 'Task addition failed' });
    }
  };

  useEffect(() => {
    if (businessId) fetchTasks();
  }, [businessId]);

  return (
    <motion.div
      initial={{ y: 20 }}
      animate={{ y: 0 }}
      className="bg-white p-6 rounded-lg shadow-lg max-w-2xl mx-auto"
    >
      <h2 className="text-2xl font-bold mb-4 text-primary">Compliance Checklist</h2>
      <form onSubmit={handleAddTask} className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Business ID</label>
          <input
            type="text"
            value={businessId}
            onChange={(e) => setBusinessId(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-secondary focus:border-secondary"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Task</label>
          <input
            type="text"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-secondary focus:border-secondary"
            required
          />
        </div>
        <button
          type="submit"
          className="bg-secondary text-white px-4 py-2 rounded-md hover:bg-blue-700 transition w-full"
        >
          Add Task
        </button>
      </form>
      {result && (
        <div className="mb-4 p-4 bg-gray-100 rounded-md">
          {result.error ? (
            <p className="text-red-600">{result.error}</p>
          ) : (
            <p className="text-green-600">{result.message} (Priority: {result.priority})</p>
          )}
        </div>
      )}
      <h3 className="text-xl font-semibold mb-2 text-gray-800">Tasks</h3>
      <ul className="space-y-2">
        {tasks.map((task) => (
          <li
            key={task.id}
            className="p-2 bg-gray-100 rounded-md flex justify-between items-center"
          >
            <span>{task.task}</span>
            <span
              className={`text-sm ${
                task.priority === 'high'
                  ? 'text-red-600'
                  : task.priority === 'medium'
                  ? 'text-yellow-600'
                  : 'text-green-600'
              }`}
            >
              {task.status} ({task.priority})
            </span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
};

export default ChecklistPage;
