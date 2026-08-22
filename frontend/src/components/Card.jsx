export default function Card({ children, className = "" }) {
    return (
        <div className={`bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 ${className}`}>
            {children}
        </div>
    );
}