const AnswerCard = ({ transcript, answer }: { transcript: string; answer: string }) => {
  if (!answer && !transcript) return null;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="bg-[#1f232b]/80 backdrop-blur-md border border-[#272b36] p-6 rounded-2xl shadow-lg ring-1 ring-white/5 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-brand-main to-brand-accent rounded-l-2xl group-hover:w-2 transition-all duration-300"></div>
        {transcript && (
          <div className="mb-6 pl-4">
            <p className="text-xs font-bold text-gray-500 tracking-widest uppercase mb-2">Transcript</p>
            <p className="text-gray-300 whitespace-pre-wrap italic leading-relaxed border-l-2 border-gray-700 pl-4 py-1">{transcript}</p>
          </div>
        )}
        {answer && (
          <div className="pl-4">
            <p className="text-xs font-bold text-brand-light tracking-widest uppercase mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-brand-accent animate-pulse"></span>
              Answer
            </p>
            <p className="text-white whitespace-pre-wrap leading-relaxed text-lg">{answer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnswerCard;