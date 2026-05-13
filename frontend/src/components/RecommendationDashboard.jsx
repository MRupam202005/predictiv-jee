import { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

// Maps a safety tag to Tailwind classes for card styling
const TAG_STYLES = {
  Safe: {
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-950/40',
    badge: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    dot: 'bg-emerald-400',
    label: '✅ Safe',
  },
  Target: {
    border: 'border-amber-500/40',
    bg: 'bg-amber-950/40',
    badge: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    dot: 'bg-amber-400',
    label: '🎯 Target',
  },
  Reach: {
    border: 'border-rose-500/40',
    bg: 'bg-rose-950/40',
    badge: 'bg-rose-500/20 text-rose-300 border border-rose-500/30',
    dot: 'bg-rose-400',
    label: '🚀 Reach',
  },
};

/**
 * Transforms the flat recommendations array into grouped college objects.
 * Each entry: { collegeName, maxChance, bestTag, branches: [...] }
 * Sorted so highest maxChance colleges appear first.
 */
function groupResultsByCollege(results) {
  const map = {};

  // Tag priority for picking the college's overall best tag
  const TAG_PRIORITY = { Safe: 3, Target: 2, Reach: 1 };

  for (const rec of results) {
    const name = rec.institute;
    if (!map[name]) {
      map[name] = { collegeName: name, branches: [], _bestMargin: -Infinity, bestTag: 'Reach' };
    }
    map[name].branches.push(rec);

    // Track the best margin and best tag across all branches for this college
    if (rec.margin > map[name]._bestMargin) {
      map[name]._bestMargin = rec.margin;
    }
    if ((TAG_PRIORITY[rec.tag] || 0) > (TAG_PRIORITY[map[name].bestTag] || 0)) {
      map[name].bestTag = rec.tag;
    }
  }

  // Convert bestMargin → a 0–100 chance score (capped and normalised)
  // margin = predicted_cutoff - user_rank
  // +5000 margin  → ~100%  |  -500 margin → ~0%
  const scoreFromMargin = (m) => Math.min(100, Math.max(0, Math.round(((m + 500) / 5500) * 100)));

  const grouped = Object.values(map).map((college) => {
    const maxChance = scoreFromMargin(college._bestMargin);
    // Sort branches within college: safest first, then by margin desc
    college.branches.sort((a, b) =>
      (TAG_PRIORITY[b.tag] || 0) - (TAG_PRIORITY[a.tag] || 0) || b.margin - a.margin
    );
    return { collegeName: college.collegeName, maxChance, bestTag: college.bestTag, branches: college.branches };
  });

  // Sort colleges: highest maxChance first
  grouped.sort((a, b) => b.maxChance - a.maxChance);
  return grouped;
}

/**
 * Maps (userRank, predictedCutoff) → an admission probability percentage.
 *
 * Zone 1: margin > 2000  → 95–99%  (virtually guaranteed, small variance)
 * Zone 2: margin 0–2000  → 50–95%  (linear interpolation)
 * Zone 3: margin < 0     → 5–50%   (linear decay, capped at 5%)
 */
function calculateProbability(userRank, predictedCutoff) {
  const margin = predictedCutoff - userRank;

  if (margin > 2000) {
    // High-confidence zone: 95% base + small bonus capped at 99%
    return Math.min(99, 95 + Math.round((margin - 2000) / 1000));
  } else if (margin >= 0) {
    // Mid zone: 50% → 95% scaled linearly over 0–2000 margin
    return Math.round(50 + (margin / 2000) * 45);
  } else {
    // Negative margin zone: 50% → 5% scaled over 0 → -5000
    const clamped = Math.max(-5000, margin);
    return Math.max(5, Math.round(50 + (clamped / 5000) * 45));
  }
}

/** A small circular SVG ring showing probability %. Coloured by value. */
function MiniRing({ pct }) {
  const radius = 15;
  const circumference = 2 * Math.PI * radius; // ≈ 94.25
  const filled = (pct / 100) * circumference;

  const color =
    pct >= 75 ? '#34d399' : // emerald
    pct >= 45 ? '#fbbf24' : // amber
    '#f87171';               // rose

  return (
    <div className="relative shrink-0 w-10 h-10">
      <svg className="w-10 h-10 -rotate-90" viewBox="0 0 36 36">
        {/* Track */}
        <circle cx="18" cy="18" r={radius} fill="none" stroke="#ffffff10" strokeWidth="3" />
        {/* Fill */}
        <circle
          cx="18" cy="18" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeDasharray={`${filled} ${circumference}`}
          strokeLinecap="round"
        />
      </svg>
      <span
        className="absolute inset-0 flex items-center justify-center"
        style={{ fontSize: '9px', fontWeight: 700, color }}
      >
        {pct}%
      </span>
    </div>
  );
}
/** A single branch row inside a CollegeGroup */
function BranchRow({ rec }) {
  const style = TAG_STYLES[rec.tag] || TAG_STYLES.Target;
  const marginSign = rec.margin > 0 ? '+' : '';
  const pct = calculateProbability(rec.predicted_cutoff - rec.margin, rec.predicted_cutoff);

  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${style.border} ${style.bg}`}>
      {/* Probability ring */}
      <MiniRing pct={pct} />

      {/* Branch name */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-200 leading-snug line-clamp-2">{rec.program}</p>
      </div>

      {/* Cutoff + margin */}
      <div className="shrink-0 text-right">
        <p className="text-slate-200 font-bold text-sm">{rec.predicted_cutoff.toLocaleString()}</p>
        <p className={`text-xs font-medium ${rec.margin > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
          {marginSign}{rec.margin.toLocaleString()}
        </p>
      </div>

      {/* Tag badge */}
      <span className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${style.badge}`}>
        {style.label}
      </span>
    </div>
  );
}

/**
 * A single clickable college row with a smooth animated branch table below it.
 * Controlled externally via selectedCollege / onSelect props.
 */
function CollegeRow({ college, filterTag, isSelected, onSelect }) {
  const style = TAG_STYLES[college.bestTag] || TAG_STYLES.Target;
  const circumference = 2 * Math.PI * 15; // 94.25
  const filled = (college.maxChance / 100) * circumference;
  const ringColor =
    college.bestTag === 'Safe' ? '#34d399' :
    college.bestTag === 'Target' ? '#fbbf24' : '#f87171';

  const visibleBranches = filterTag === 'All'
    ? college.branches
    : college.branches.filter((b) => b.tag === filterTag);

  if (visibleBranches.length === 0) return null;

  return (
    <div className="group">
      {/* ── Clickable College Header Row ─────────────────── */}
      <button
        onClick={() => onSelect(college.collegeName)}
        className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl border text-left
          transition-all duration-200
          ${
            isSelected
              ? 'bg-white/[0.07] border-blue-500/50 shadow-lg shadow-blue-900/20'
              : 'bg-white/[0.03] border-white/8 hover:bg-white/[0.055] hover:border-white/15'
          }`}
      >
        {/* Circular progress ring (maxChance of best branch) */}
        <div className="relative shrink-0 w-13 h-13">
          <svg className="w-13 h-13 -rotate-90" viewBox="0 0 36 36" style={{ width: 52, height: 52 }}>
            <circle cx="18" cy="18" r="15" fill="none" stroke="#ffffff0d" strokeWidth="3" />
            <circle
              cx="18" cy="18" r="15" fill="none"
              stroke={ringColor}
              strokeWidth="3"
              strokeDasharray={`${filled} ${circumference}`}
              strokeLinecap="round"
              style={{ transition: 'stroke-dasharray 0.5s ease' }}
            />
          </svg>
          <span
            className="absolute inset-0 flex items-center justify-center font-bold"
            style={{ fontSize: '10px', color: ringColor }}
          >
            {college.maxChance}%
          </span>
        </div>

        {/* College info */}
        <div className="flex-1 min-w-0">
          <p className={`font-semibold text-sm leading-snug truncate transition-colors ${
            isSelected ? 'text-white' : 'text-slate-200 group-hover:text-white'
          }`}>
            {college.collegeName}
          </p>
          <p className="text-xs text-slate-500 mt-0.5">
            {visibleBranches.length} eligible branch{visibleBranches.length !== 1 ? 'es' : ''}
          </p>
        </div>

        {/* Best tag badge */}
        <span className={`shrink-0 hidden sm:block text-xs font-semibold px-2.5 py-1 rounded-full ${style.badge}`}>
          {style.label}
        </span>

        {/* Expand chevron */}
        <svg
          className={`shrink-0 w-4 h-4 text-slate-500 transition-transform duration-300 ${
            isSelected ? 'rotate-180 text-blue-400' : ''
          }`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* ── Branch Table (animated expand) ───────────────── */}
      <div
        className="overflow-hidden transition-all duration-300 ease-in-out"
        style={{ maxHeight: isSelected ? `${visibleBranches.length * 64 + 80}px` : '0px', opacity: isSelected ? 1 : 0 }}
      >
        <div className="mt-1 mx-1 mb-2 rounded-xl border border-white/8 bg-black/20 overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 px-4 py-2.5 bg-white/[0.04] border-b border-white/5">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Branch / Program</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide text-right">Predicted Cutoff</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide text-right">Margin</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide text-center">Chance</span>
          </div>

          {/* Branch rows */}
          {visibleBranches.map((rec, i) => {
            const bStyle = TAG_STYLES[rec.tag] || TAG_STYLES.Target;
            const pct = calculateProbability(rec.predicted_cutoff - rec.margin, rec.predicted_cutoff);
            const marginSign = rec.margin > 0 ? '+' : '';
            const isFirst = i === 0;

            return (
              <div
                key={i}
                className={`grid grid-cols-[1fr_auto_auto_auto] gap-x-4 items-center px-4 py-3
                  border-b border-white/5 last:border-0 transition-colors
                  ${isFirst ? 'bg-white/[0.03]' : 'hover:bg-white/[0.025]'}`}
              >
                {/* Program name with best-match star */}
                <div className="flex items-start gap-2 min-w-0">
                  {isFirst && (
                    <span className="shrink-0 mt-0.5 text-amber-400 text-xs">★</span>
                  )}
                  <p className="text-sm text-slate-200 leading-snug line-clamp-2">{rec.program}</p>
                </div>

                {/* Cutoff */}
                <span className="text-sm font-bold text-slate-100 text-right whitespace-nowrap">
                  {rec.predicted_cutoff.toLocaleString()}
                </span>

                {/* Margin */}
                <span className={`text-xs font-semibold text-right whitespace-nowrap ${
                  rec.margin > 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}>
                  {marginSign}{rec.margin.toLocaleString()}
                </span>

                {/* Mini probability ring */}
                <div className="flex justify-center">
                  <MiniRing pct={pct} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function RecommendationDashboard() {
  const [userRank, setUserRank] = useState('');
  const [category, setCategory] = useState('');
  const [gender, setGender] = useState('');
  const [examType, setExamType] = useState('Mains');
  const [quota, setQuota] = useState('OS');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [options, setOptions] = useState({ categories: [], genders: [] });
  const [filterTag, setFilterTag] = useState('All');
  const [selectedCollege, setSelectedCollege] = useState(null);

  // Fetch dropdown options from backend on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/options`)
      .then((res) => res.json())
      .then((data) => {
        setOptions(data);
        setCategory(data.categories[0] || '');
        setGender(data.genders[0] || '');
      })
      .catch(() => setError('Could not connect to backend. Make sure the API is running.'));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults(null);
    setFilterTag('All');

    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_rank: parseInt(userRank, 10),
          category,
          gender,
          exam_type: examType,
          quota: examType === 'Mains' ? quota : 'AI',
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'API returned an error');
      }

      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError(err.message || 'Unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  // Filtered view based on selected safety tag
  const filteredResults = results?.recommendations?.filter(
    (r) => filterTag === 'All' || r.tag === filterTag
  );

  const tagCounts = results?.recommendations?.reduce((acc, r) => {
    acc[r.tag] = (acc[r.tag] || 0) + 1;
    return acc;
  }, {});

  return (
    // <div className="min-h-screen bg-gradient-to-br from-slate-950 via-[#0d1b3e] to-slate-950">
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-[#0d1b3e] to-slate-950">
      {/* Header */}
      <header className="border-b border-white/5 bg-white/[0.02] backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm">
            P
          </div>
          <div>
            <h1 className="text-white font-bold text-base leading-none">Predictiv JEE</h1>
            <p className="text-slate-500 text-xs mt-0.5">ML-Powered College Predictor</p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-1.5 text-xs text-blue-300 font-medium mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
            2026 Cutoff Predictions · Powered by Random Forest ML
          </div>
          <h2 className="text-4xl font-extrabold text-white mb-3 tracking-tight">
            Find Your Best{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-400">
              College Matches
            </span>
          </h2>
          <p className="text-slate-400 text-base max-w-xl mx-auto">
            Enter your JEE rank and profile. Our ML engine will predict 2026 cutoffs across every
            eligible college and rank them by your admission probability.
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur-sm mb-8">
          <form onSubmit={handleSubmit}>
            {/* Exam Type Toggle */}
            <div className="flex gap-2 mb-6 bg-black/30 rounded-xl p-1">
              {['Mains', 'Advanced'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setExamType(type)}
                  className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    examType === type
                      ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-lg shadow-blue-900/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  JEE {type} {type === 'Mains' ? '(NIT / IIIT / GFTI)' : '(IIT)'}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {/* Rank Input */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Your Rank</label>
                <input
                  type="number"
                  required
                  min={1}
                  placeholder="e.g. 15000"
                  value={userRank}
                  onChange={(e) => setUserRank(e.target.value)}
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white 
                             placeholder-slate-600 text-sm focus:outline-none focus:border-blue-500/60 
                             focus:ring-1 focus:ring-blue-500/30 transition-all"
                />
              </div>

              {/* Category */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  required
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white 
                             text-sm focus:outline-none focus:border-blue-500/60 focus:ring-1 
                             focus:ring-blue-500/30 transition-all appearance-none cursor-pointer"
                >
                  {options.categories.map((c) => (
                    <option key={c} value={c} className="bg-slate-900">{c}</option>
                  ))}
                </select>
              </div>

              {/* Gender */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Gender Pool</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  required
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white 
                             text-sm focus:outline-none focus:border-blue-500/60 focus:ring-1 
                             focus:ring-blue-500/30 transition-all appearance-none cursor-pointer"
                >
                  {options.genders.map((g) => (
                    <option key={g} value={g} className="bg-slate-900">{g}</option>
                  ))}
                </select>
              </div>

              {/* Quota (Mains only) */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Quota {examType === 'Advanced' && <span className="text-slate-600">(N/A for IITs)</span>}
                </label>
                <select
                  value={quota}
                  onChange={(e) => setQuota(e.target.value)}
                  disabled={examType === 'Advanced'}
                  className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white 
                             text-sm focus:outline-none focus:border-blue-500/60 focus:ring-1 
                             focus:ring-blue-500/30 transition-all appearance-none cursor-pointer
                             disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <option value="OS" className="bg-slate-900">Other State (OS)</option>
                  <option value="HS" className="bg-slate-900">Home State (HS)</option>
                </select>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 rounded-xl font-semibold text-sm text-white
                         bg-gradient-to-r from-blue-600 to-violet-600 
                         hover:from-blue-500 hover:to-violet-500
                         transition-all duration-200 shadow-lg shadow-blue-900/30
                         disabled:opacity-60 disabled:cursor-not-allowed
                         flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Running ML Inference...
                </>
              ) : (
                '⚡ Generate Recommendations'
              )}
            </button>
          </form>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-rose-950/40 border border-rose-500/30 rounded-xl p-4 mb-6 text-rose-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div>
            {/* Summary Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
              <div>
                <h3 className="text-white font-bold text-lg">
                  {results.results_count} Colleges Found
                </h3>
                <p className="text-slate-500 text-sm">
                  For JEE {examType} Rank {results.user_query.rank.toLocaleString()} · {results.user_query.category}
                </p>
              </div>

              {/* Tag Filter Pills */}
              <div className="flex gap-2 flex-wrap">
                {['All', 'Safe', 'Target', 'Reach'].map((tag) => {
                  const count = tag === 'All' ? results.results_count : (tagCounts?.[tag] || 0);
                  const active = filterTag === tag;
                  return (
                    <button
                      key={tag}
                      onClick={() => setFilterTag(tag)}
                      className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                        active
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'bg-white/5 border-white/10 text-slate-400 hover:border-white/20'
                      }`}
                    >
                      {tag} {count > 0 && <span className="opacity-70">({count})</span>}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* College Rows */}
            {(() => {
              const grouped = groupResultsByCollege(filteredResults || []);
              const visible = grouped.filter((c) =>
                filterTag === 'All' ? true : c.branches.some((b) => b.tag === filterTag)
              );
              return visible.length > 0 ? (
                <div className="flex flex-col gap-2">
                  {visible.map((college) => (
                    <CollegeRow
                      key={college.collegeName}
                      college={college}
                      filterTag={filterTag}
                      isSelected={selectedCollege === college.collegeName}
                      onSelect={(name) =>
                        setSelectedCollege((prev) => (prev === name ? null : name))
                      }
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500">
                  No {filterTag} colleges found for your profile.
                </div>
              );
            })()}
          </div>
        )}
      </main>
    </div>
  );
}
