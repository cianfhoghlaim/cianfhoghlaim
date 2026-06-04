export function Syllabus() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <header>
        <h1 className="font-cinzel text-3xl text-purple-400">Syllabus Visualiser</h1>
        <p className="text-slate-400">
          NCCA / CCEA / SQA / CfW concept graph and Celtic-language coverage.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
          <h2 className="font-bold text-purple-300 mb-2">National authorities</h2>
          <ul className="text-sm space-y-2 text-slate-300">
            <li>
              <strong className="text-slate-100">NCCA</strong> (Ireland) — 33
              senior cycle + 18 junior cycle + primary + early childhood
            </li>
            <li>
              <strong className="text-slate-100">CCEA</strong> (Northern Ireland) —
              A-level / GCSE equivalents
            </li>
            <li>
              <strong className="text-slate-100">SQA</strong> (Scotland) — Higher /
              Advanced Higher / National 5
            </li>
            <li>
              <strong className="text-slate-100">CfW</strong> (Wales) — Curriculum
              for Wales
            </li>
          </ul>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
          <h2 className="font-bold text-purple-300 mb-2">Celtic-language coverage</h2>
          <table className="text-sm w-full">
            <tbody>
              {[
                ["ga", "Irish (Gaeilge)"],
                ["gd", "Scottish Gaelic"],
                ["cy", "Welsh (Cymraeg)"],
                ["gv", "Manx (Gaelg)"],
                ["kw", "Cornish (Kernewek)"],
                ["br", "Breton (Brezhoneg)"],
              ].map(([code, name]) => (
                <tr key={code} className="border-b border-slate-800">
                  <td className="py-1 font-mono text-purple-300">{code}</td>
                  <td className="py-1 text-slate-300">{name}</td>
                  <td className="py-1 text-right text-slate-500 text-xs">
                    via <code>curriculum_translation</code> flow
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-slate-400 text-sm">
        <h2 className="font-bold text-purple-300 mb-2">Concept graph</h2>
        <p>
          The full concept graph is rendered by{" "}
          <code>data_platform/cocoindex_flows/learning_outcome_graph.py</code>{" "}
          and indexed in LanceDB as{" "}
          <code>celtic_curriculum_embeddings</code>. The marimo notebook{" "}
          <code>syllabus_visualizer.py</code> renders it interactively.
        </p>
      </div>
    </div>
  );
}
