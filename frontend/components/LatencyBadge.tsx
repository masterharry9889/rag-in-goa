import { useState, useEffect } from 'react';

// This LatencyBadge now receives the latency as a prop and displays it.
const LatencyBadge = ({ latency }) => {
  // We can still use useEffect to update the latency if we want to simulate changes,
  // but now we are getting it from the parent via props.
  // For the purpose of this task, we'll just display the given latency.

  // Determine color based on latency
  const getLatencyColor = (latencyMs) => {
    if (latencyMs < 100) return 'bg-green-500';
    if (latencyMs < 200) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className={`p-2 px-4 rounded-full text-white text-sm font-medium ${
      getLatencyColor(latency)
    }`}>
      Latency: {latency}ms
    </div>
  );
};

export default LatencyBadge;