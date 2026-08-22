export default function Button({ children, variant = "primary", ...props }) {
    const base = "px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
    const variants = {
        primary: "bg-blue-600 text-white hover:bg-blue-700",
        danger: "bg-red-500 text-white hover:bg-red-600",
        secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200",
    };
    return (
        <button className={`${base} ${variants[variant]}`} {...props}>
            {children}
        </button>
    );
}