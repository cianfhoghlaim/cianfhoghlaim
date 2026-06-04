export function SyllabusPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl text-purple-400">Syllabus Visualiser</h1>
      <p className="text-slate-400">NCCA / CCEA / SQA / CfW concept graph and Celtic-language coverage.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
          <h2 className="font-bold text-purple-300 mb-2">National authorities</h2>
          <ul className="text-sm space-y-2 text-slate-300">
            <li><strong className="text-slate-100">NCCA</strong> (Ireland)</li>
            <li><strong className="text-slate-100">CCEA</strong> (NI)</li>
            <li><strong className="text-slate-100">SQA</strong> (Scotland)</li>
            <li><strong className="text-slate-100">CfW</strong> (Wales)</li>
          </ul>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
          <h2 className="font-bold text-purple-300 mb-2">Celtic languages</h2>
          {[["ga","Irish"],["gd","Scottish Gaelic"],["cy","Welsh"],["gv","Manx"],["kw","Cornish"],["br","Breton"]].map(([c,n]) => (
            <div key={c} className="flex justify-between">{n} <code className="text-xs text-purple-300">{c}</code></div>
          ))}
        </div>
      </div>
    </div>
  );
}
