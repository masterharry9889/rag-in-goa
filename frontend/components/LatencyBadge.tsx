// This LatencyBadge now receives the latency as a prop and displays it.
const LatencyBadge = ({ latency }: { latency: number }) => {
  // We can still use useEffect to update the latency if we want to simulate changes,
  // but now we are getting it from the parent via props.
  // For the purpose of this task, we'll just display the given latency.

  // Determine color based on latency
  const getLatencyStyle = (latencyMs: number) => {
    if (latencyMs < 100) return 'bg-brand-dark/30 text-brand-light border-brand-main/50 shadow-[0_0_15px_rgba(73,154,19,0.3)]';
    if (latencyMs < 300) return 'bg-yellow-900/30 text-yellow-400 border-yellow-700/50 shadow-[0_0_15px_rgba(234,179,8,0.2)]';
    return 'bg-red-900/30 text-red-400 border-red-700/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]';
  };

  return (
    <div className={`px-5 py-2 rounded-full text-sm font-bold tracking-wider border backdrop-blur-md flex items-center gap-3 ${
      getLatencyStyle(latency)
    }`}>
      <span className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${latency < 100 ? 'bg-brand-accent' : latency < 300 ? 'bg-yellow-400' : 'bg-red-400'}`}></span>
        <span className={`relative inline-flex rounded-full h-2 w-2 ${latency < 100 ? 'bg-brand-main' : latency < 300 ? 'bg-yellow-500' : 'bg-red-500'}`}></span>
      </span>
      {latency}ms
    </div>
  );
};

export default LatencyBadge;