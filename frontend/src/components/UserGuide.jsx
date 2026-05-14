import { useState } from 'react';

const STEPS = [
  {
    icon: '🎓',
    title: 'Choose Your Exam',
    body: 'Select JEE Mains if you appeared for the NIT/IIIT/GFTI counselling (JoSAA), or JEE Advanced if you sat for the IIT entrance exam.',
  },
  {
    icon: '🏷️',
    title: 'Enter Your Category Rank',
    critical: true,
    body: 'This is the most important rule. Enter the rank for the category you selected — not your overall general rank.',
    examples: [
      { good: true, text: 'OBC-NCL selected → enter your OBC-NCL rank (e.g. 8,200)' },
      { good: false, text: 'OBC-NCL selected → entering your General / CRL rank (e.g. 25,000) ❌' },
      { good: true, text: 'OPEN selected → enter your CRL / All India Rank' },
      { good: true, text: 'SC selected → enter your SC rank' },
    ],
  },
  {
    icon: '⚧️',
    title: 'Select Your Gender Pool',
    body: '"Gender-Neutral" pools include all applicants. "Female-only" pools are exclusively reserved seats for female candidates — select this if you are applying for those supernumerary seats.',
  },
  {
    icon: '🏠',
    title: 'Home State vs. Other State (Mains only)',
    body: `For NITs, 50% of seats are reserved for Home State (HS) students at lower cutoffs. If you're from the same state as the NIT, choose HS. Otherwise, choose OS (Other State). This setting does not apply to IITs.`,
  },
];

const HOW_IT_WORKS = [
  {
    icon: '📚',
    title: 'Trained on 8 Years of Real Data',
    body: 'The AI has studied 4,30,000+ actual JoSAA / CSAB cutoff records from 2018 to 2025 — every round, every college, every branch, every category.',
  },
  {
    icon: '🌲',
    title: 'Random Forest Algorithm',
    body: 'The model uses 100 "decision trees" that each independently vote on what a cutoff should be. The final prediction is the average of all 100 votes — making it robust and resistant to outliers.',
  },
  {
    icon: '🔮',
    title: 'Predicting 2026 Cutoffs',
    body: 'For each college branch that historically matched your profile, the model is asked: "Given this institute, program, category, round, and the year 2026 — what will the closing rank be?" It predicts demand patterns, not random guesses.',
  },
  {
    icon: '🎯',
    title: 'Safe / Target / Reach Logic',
    body: `Once cutoffs are predicted, your rank is compared to each result. If the cutoff is significantly above your rank (safe buffer), it's "Safe". If it's close, it's "Target". If it's below your rank, it's "Reach" — meaning you'd need luck or a lower-demand round.`,
  },
];

export default function UserGuide() {
  const [open, setOpen] = useState(false);

  return (
    <div className="mb-8">
      {/* Toggle Button */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-3 px-5 py-3.5
          bg-blue-500/10 hover:bg-blue-500/15 border border-blue-500/25
          rounded-2xl transition-all duration-200 text-left group"
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">💡</span>
          <div>
            <p className="text-sm font-semibold text-blue-200 animate-pulse">How to use this tool — Read before searching!</p>
            <p className="text-xs text-blue-400/70 mt-0.5">Common mistakes to avoid · How the AI works</p>
          </div>
        </div>
        <svg
          className={`shrink-0 w-4 h-4 text-blue-400 transition-transform duration-300 ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Collapsible Content */}
      <div
        className="overflow-hidden transition-all duration-500 ease-in-out"
        style={{ maxHeight: open ? '2000px' : '0px', opacity: open ? 1 : 0 }}
      >
        <div className="mt-3 space-y-5">

          {/* ── Step-by-Step Guide ─────────────────────────────── */}
          <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5">
            <h3 className="text-white font-bold text-sm mb-4 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">?</span>
              Step-by-Step: How to Fill the Form
            </h3>
            <div className="space-y-4">
              {STEPS.map((step, i) => (
                <div key={i} className={`rounded-xl p-4 border ${step.critical ? 'border-amber-500/30 bg-amber-500/5' : 'border-white/5 bg-white/[0.02]'}`}>
                  <div className="flex items-start gap-3">
                    <span className="text-xl shrink-0 mt-0.5">{step.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-semibold text-white">
                          Step {i + 1}: {step.title}
                        </p>
                        {step.critical && (
                          <span className="text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full">
                            ⚠️ Critical
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-400 leading-relaxed">{step.body}</p>

                      {step.examples && (
                        <ul className="mt-3 space-y-2">
                          {step.examples.map((ex, j) => (
                            <li key={j} className={`flex items-start gap-2 text-xs rounded-lg px-3 py-2 ${
                              ex.good
                                ? 'bg-emerald-950/40 border border-emerald-500/20 text-emerald-300'
                                : 'bg-rose-950/40 border border-rose-500/20 text-rose-300'
                            }`}>
                              <span className="shrink-0 font-bold">{ex.good ? '✓' : '✗'}</span>
                              <span>{ex.text}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── How the AI Works ───────────────────────────────── */}
          <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5">
            <h3 className="text-white font-bold text-sm mb-4 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-violet-600 flex items-center justify-center text-white text-xs font-bold">AI</span>
              How the Prediction Engine Works
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {HOW_IT_WORKS.map((item, i) => (
                <div key={i} className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                  <p className="text-2xl mb-2">{item.icon}</p>
                  <p className="text-sm font-semibold text-slate-200 mb-1">{item.title}</p>
                  <p className="text-xs text-slate-500 leading-relaxed">{item.body}</p>
                </div>
              ))}
            </div>

            {/* Disclaimer */}
            <div className="mt-4 flex items-start gap-3 bg-slate-800/40 border border-white/5 rounded-xl px-4 py-3">
              <span className="text-slate-400 shrink-0 mt-0.5">ℹ️</span>
              <p className="text-xs text-slate-500 leading-relaxed">
                <span className="text-slate-300 font-medium">Important: </span>
                These predictions are based on historical trends and are meant to guide your choices — not guarantee admission.
                Always cross-check with the official JoSAA portal. Sudden surge in demand, new seats, or policy changes can
                shift actual cutoffs.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
